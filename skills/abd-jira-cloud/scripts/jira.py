#!/usr/bin/env python3
"""Jira Cloud CLI — thin wrapper over the Jira Cloud REST API v3.

Standard library only (urllib), so it runs anywhere with Python 3.8+ and needs
no `pip install`. Every command prints JSON to stdout and human-readable errors
to stderr, and exits non-zero on failure so callers can detect problems.

Auth + target come from environment variables:
    JIRA_BASE_URL   e.g. https://your-site.atlassian.net
    JIRA_EMAIL      the Atlassian account email
    JIRA_API_TOKEN  token from id.atlassian.com/manage-profile/security/api-tokens

Add --dry-run to ANY command to print the request that would be sent (method,
URL, headers with the credential redacted, and body) without sending it. This is
the safe way to inspect exactly what the tool will do before it touches Jira.
"""

import argparse
import base64
import json
import os
import socket
import sys
from typing import Mapping, Optional
import urllib.error
import urllib.parse
import urllib.request

API = "/rest/api/3"
REQUEST_TIMEOUT = 30
ERROR_BODY_LIMIT = 64 * 1024
DEFAULT_SEARCH_LIMIT = 100


# --------------------------------------------------------------------------- #
# Config + transport
# --------------------------------------------------------------------------- #
class JiraError(Exception):
    pass


def validate_base_url(value: str) -> str:
    if not value:
        raise JiraError("Missing required environment variable: JIRA_BASE_URL.")
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as error:
        raise JiraError(f"Invalid JIRA_BASE_URL: {error}.") from None
    hostname = (parsed.hostname or "").lower()
    site_name = hostname[: -len(".atlassian.net")] if hostname.endswith(".atlassian.net") else ""
    if parsed.scheme.lower() != "https":
        raise JiraError("JIRA_BASE_URL must use HTTPS.")
    if not hostname.endswith(".atlassian.net"):
        raise JiraError("JIRA_BASE_URL must be an HTTPS *.atlassian.net site URL.")
    if not site_name or site_name.endswith("."):
        raise JiraError("JIRA_BASE_URL must be an HTTPS *.atlassian.net site URL.")
    if parsed.username is not None or parsed.password is not None:
        raise JiraError("JIRA_BASE_URL must not contain credentials.")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise JiraError("JIRA_BASE_URL must not contain a path, query, or fragment.")
    if port not in (None, 443):
        raise JiraError("JIRA_BASE_URL must use the default HTTPS port.")
    return f"https://{hostname}"


def path_segment(value: str, label: str) -> str:
    if not value:
        raise JiraError(f"{label} must not be empty.")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise JiraError(f"{label} contains control characters.")
    return urllib.parse.quote(value, safe="")


def issue_path(issue_id_or_key: str, suffix: str = "") -> str:
    return f"{API}/issue/{path_segment(issue_id_or_key, 'issue ID or key')}{suffix}"


class Config:
    def __init__(self, environ: Optional[Mapping[str, str]] = None):
        source = os.environ if environ is None else environ
        self.base_url = source.get("JIRA_BASE_URL", "")
        self.email = source.get("JIRA_EMAIL", "")
        self.token = source.get("JIRA_API_TOKEN", "")

    def require(self, live: bool = True) -> None:
        self.base_url = validate_base_url(self.base_url)
        if not live:
            return
        missing = [
            name
            for name, value in (
                ("JIRA_EMAIL", self.email),
                ("JIRA_API_TOKEN", self.token),
            )
            if not value
        ]
        if missing:
            raise JiraError(
                "Missing required environment variable(s): " + ", ".join(missing) + "."
            )

    def auth_header(self) -> str:
        raw = f"{self.email}:{self.token}".encode("utf-8")
        return "Basic " + base64.b64encode(raw).decode("ascii")


def _origin(url):
    parsed = urllib.parse.urlsplit(url)
    try:
        port = parsed.port
    except ValueError as error:
        raise JiraError(f"Invalid redirect URL: {error}.") from None
    if parsed.username is not None or parsed.password is not None:
        raise JiraError("Refusing a redirect URL with credentials.")
    port = port or (443 if parsed.scheme.lower() == "https" else 80)
    return parsed.scheme.lower(), (parsed.hostname or "").lower(), port


class SameOriginRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        destination = urllib.parse.urljoin(req.full_url, newurl)
        if _origin(destination) != _origin(req.full_url) or _origin(destination)[0] != "https":
            raise JiraError("Refusing an unsafe cross-origin or non-HTTPS redirect.")
        return super().redirect_request(req, fp, code, msg, headers, destination)


HTTP_OPENER = urllib.request.build_opener(SameOriginRedirectHandler())


def _redact(text, cfg):
    return text.replace(cfg.token, "<redacted>") if cfg.token else text


def request(method, path, cfg, query=None, body=None, dry_run=False):
    cfg.require(live=not dry_run)
    url = cfg.base_url + path
    if query:
        url += "?" + urllib.parse.urlencode(query, doseq=True)

    authorization = "Basic <redacted>" if dry_run else cfg.auth_header()
    headers = {"Accept": "application/json", "Authorization": authorization}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if dry_run:
        emit({"method": method, "url": url, "headers": headers, "body": body})
        return None

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with HTTP_OPENER.open(req, timeout=REQUEST_TIMEOUT) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        raw = error.read(ERROR_BODY_LIMIT + 1)
        truncated = len(raw) > ERROR_BODY_LIMIT
        detail = raw[:ERROR_BODY_LIMIT].decode("utf-8", errors="replace")
        detail = _redact(detail, cfg)
        lines = [f"HTTP {error.code} on {method} {path}"]
        retry_after = error.headers.get("Retry-After") if error.headers else None
        if retry_after:
            lines.append(f"Retry-After: {retry_after}")
        if detail:
            lines.append(detail + ("\n[truncated]" if truncated else ""))
        raise JiraError("\n".join(lines)) from None
    except (urllib.error.URLError, socket.timeout, TimeoutError) as error:
        reason = getattr(error, "reason", error)
        raise JiraError(f"Could not reach {cfg.base_url}: {reason}") from None

    if not raw.strip():
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise JiraError(f"Jira returned invalid JSON: {error}.") from None


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def text_to_adf(text):
    """Convert plain text into a minimal valid Atlassian Document Format doc.

    Jira Cloud v3 requires comment and description bodies as ADF (not strings).
    Blank lines separate paragraphs; single newlines become hard breaks. Text
    nodes are never emitted empty (that would be invalid ADF).
    """
    paragraphs = text.split("\n\n")
    content = []
    for para in paragraphs:
        lines = para.split("\n")
        nodes = []
        for i, line in enumerate(lines):
            if line:
                nodes.append({"type": "text", "text": line})
            if i < len(lines) - 1:
                nodes.append({"type": "hardBreak"})
        content.append({"type": "paragraph", "content": nodes} if nodes
                       else {"type": "paragraph"})
    if not content:
        content = [{"type": "paragraph"}]
    return {"type": "doc", "version": 1, "content": content}


def resolve_account_id(cfg, email_or_name, dry_run=False):
    """Resolve an email/display name to a Jira Cloud accountId via user search.

    In dry-run we cannot hit the network, so return a readable placeholder so the
    caller can still show a meaningful request body.
    """
    if dry_run:
        return f"<accountId-resolved-from:{email_or_name}>"
    res = request("GET", f"{API}/user/search", cfg, query={"query": email_or_name})
    if not res:
        raise JiraError(f"No user found matching '{email_or_name}'.")
    # Prefer an exact email match when the query looks like an email.
    for user in res:
        if user.get("emailAddress", "").lower() == email_or_name.lower():
            return user["accountId"]
    if len(res) == 1:
        return res[0]["accountId"]
    names = ", ".join(
        f"{u.get('displayName')} ({u.get('accountId')})" for u in res[:10]
    )
    raise JiraError(
        f"'{email_or_name}' matched {len(res)} users; be more specific or pass "
        f"--account-id. Matches: {names}"
    )


def emit(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def parse_kv_json(pairs):
    """Turn ['labels=[\"a\"]', 'priority={\"name\":\"High\"}', 'summary=Hi']
    into a fields dict. Each value is parsed as JSON if possible, else kept as a
    string. This lets simple scalars and full JSON structures share one flag.
    """
    fields = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise JiraError(f"--field expects key=value, got: {pair}")
        key, val = pair.split("=", 1)
        if not key:
            raise JiraError("--field expects a non-empty key before '='.")
        try:
            fields[key] = json.loads(val)
        except json.JSONDecodeError:
            fields[key] = val
    return fields


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_whoami(args, cfg):
    result = request("GET", f"{API}/myself", cfg, dry_run=args.dry_run)
    if result is not None:
        emit(result)


def cmd_get(args, cfg):
    query = {}
    if args.fields:
        query["fields"] = args.fields
    if args.expand:
        query["expand"] = args.expand
    res = request(
        "GET", issue_path(args.key), cfg, query=query or None,
        dry_run=args.dry_run,
    )
    if res is not None:
        emit(res)


def cmd_search(args, cfg):
    fields = (
        [f.strip() for f in args.fields.split(",")]
        if args.fields
        else ["summary", "status", "assignee", "updated"]
    )
    collected = []
    next_token = None
    while True:
        page_size = 100
        if args.limit:
            page_size = min(page_size, args.limit - len(collected))
        body = {"jql": args.jql, "maxResults": page_size, "fields": fields}
        if next_token:
            body["nextPageToken"] = next_token
        res = request("POST", f"{API}/search/jql", cfg, body=body,
                      dry_run=args.dry_run)
        if res is None:  # dry-run
            return
        collected.extend(res.get("issues", []))
        next_token = res.get("nextPageToken")
        if res.get("isLast") or not next_token:
            break
        if args.limit and len(collected) >= args.limit:
            break
    if args.limit:
        collected = collected[: args.limit]
    emit({"count": len(collected), "issues": collected})


def cmd_comment(args, cfg):
    if args.adf_file:
        with open(args.adf_file) as fh:
            adf = json.load(fh)
    else:
        text = args.body if args.body is not None else sys.stdin.read()
        adf = text_to_adf(text)
    res = request(
        "POST", issue_path(args.key, "/comment"), cfg,
        body={"body": adf}, dry_run=args.dry_run,
    )
    if res is not None:
        emit({"id": res.get("id"), "self": res.get("self")})


def cmd_update(args, cfg):
    fields = parse_kv_json(args.field)
    if args.summary is not None:
        fields["summary"] = args.summary
    if args.description is not None:
        fields["description"] = text_to_adf(args.description)
    if args.labels is not None:
        fields["labels"] = [l.strip() for l in args.labels.split(",") if l.strip()]
    if args.priority is not None:
        fields["priority"] = {"name": args.priority}
    if args.duedate is not None:
        fields["duedate"] = args.duedate
    if not fields:
        raise JiraError(
            "Nothing to update. Pass --field k=v (repeatable) and/or a "
            "convenience flag (--summary/--description/--labels/--priority/--duedate)."
        )
    res = request(
        "PUT", issue_path(args.key), cfg,
        body={"fields": fields}, dry_run=args.dry_run,
    )
    # A successful PUT returns 204 No Content.
    if res is not None:
        emit({"updated": args.key, "fields": list(fields.keys())})


def cmd_transitions(args, cfg):
    res = request(
        "GET", issue_path(args.key, "/transitions"), cfg, dry_run=args.dry_run
    )
    if res is None:
        return
    emit(
        [
            {"id": t["id"], "name": t["name"], "to": t.get("to", {}).get("name")}
            for t in res.get("transitions", [])
        ]
    )


def cmd_transition(args, cfg):
    cfg.require(live=not args.dry_run)
    transition_id = args.id
    if transition_id is None:
        if args.dry_run:
            print(
                f"[dry-run] Would GET {issue_path(args.key, '/transitions')} to "
                f"resolve '{args.to}' to a transition id, then POST it."
            )
            transition_id = "<resolved-id>"
        else:
            listing = request("GET", issue_path(args.key, "/transitions"), cfg)
            match = None
            for t in listing.get("transitions", []):
                to_name = t.get("to", {}).get("name", "")
                if args.to.lower() in (t["name"].lower(), to_name.lower()):
                    match = t["id"]
                    break
            if match is None:
                avail = ", ".join(
                    f'{t["name"]} -> {t.get("to", {}).get("name")}'
                    for t in listing.get("transitions", [])
                )
                raise JiraError(
                    f"No transition matching '{args.to}'. Available: {avail}"
                )
            transition_id = match

    body = {"transition": {"id": transition_id}}
    if args.resolution:
        body["fields"] = {"resolution": {"name": args.resolution}}
    if args.comment:
        body["update"] = {
            "comment": [{"add": {"body": text_to_adf(args.comment)}}]
        }
    res = request(
        "POST", issue_path(args.key, "/transitions"), cfg,
        body=body, dry_run=args.dry_run,
    )
    if res is not None:  # 204 on success
        emit({"transitioned": args.key, "transition_id": transition_id})


def cmd_assign(args, cfg):
    if args.unassign:
        account_id = None
    elif args.account_id:
        account_id = args.account_id
    elif args.email:
        account_id = resolve_account_id(cfg, args.email, dry_run=args.dry_run)
    else:
        raise JiraError("Pass one of --email, --account-id, or --unassign.")
    res = request(
        "PUT", issue_path(args.key, "/assignee"), cfg,
        body={"accountId": account_id}, dry_run=args.dry_run,
    )
    if res is not None:  # 204 on success
        emit({"assigned": args.key, "accountId": account_id})


def cmd_watch(args, cfg):
    account_id = args.account_id
    if account_id is None and args.email:
        account_id = resolve_account_id(cfg, args.email, dry_run=args.dry_run)
    # Add-watcher takes the accountId as the RAW json body (a bare string),
    # not an object. Remove uses a query param instead.
    if args.remove:
        if account_id is None:
            raise JiraError("--remove needs --email or --account-id.")
        res = request(
            "DELETE", issue_path(args.key, "/watchers"), cfg,
            query={"accountId": account_id}, dry_run=args.dry_run,
        )
        if res is not None:
            emit({"removed_watcher": account_id, "issue": args.key})
        return
    if account_id is None:
        raise JiraError("Pass --email or --account-id (or --remove to drop one).")
    res = request(
        "POST", issue_path(args.key, "/watchers"), cfg,
        body=account_id, dry_run=args.dry_run,
    )
    if res is not None:
        emit({"added_watcher": account_id, "issue": args.key})


def cmd_watchers(args, cfg):
    res = request(
        "GET", issue_path(args.key, "/watchers"), cfg, dry_run=args.dry_run
    )
    if res is not None:
        emit(res)


def cmd_create(args, cfg):
    fields = parse_kv_json(args.field)
    fields.setdefault("project", {"key": args.project})
    fields.setdefault("issuetype", {"name": args.type})
    if args.summary is not None:
        fields["summary"] = args.summary
    if args.description is not None:
        fields["description"] = text_to_adf(args.description)
    if "summary" not in fields:
        raise JiraError("Creating an issue needs --summary.")
    res = request(
        "POST", f"{API}/issue", cfg, body={"fields": fields},
        dry_run=args.dry_run,
    )
    if res is not None:
        emit({"key": res.get("key"), "id": res.get("id"), "self": res.get("self")})


def cmd_users(args, cfg):
    res = request(
        "GET", f"{API}/user/search", cfg, query={"query": args.query},
        dry_run=args.dry_run,
    )
    if res is not None:
        emit(
            [
                {
                    "accountId": u.get("accountId"),
                    "displayName": u.get("displayName"),
                    "emailAddress": u.get("emailAddress"),
                }
                for u in res
            ]
        )


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #
def build_parser():
    p = argparse.ArgumentParser(
        prog="jira.py", description="Jira Cloud REST API v3 CLI."
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the request that would be sent, without sending it.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("whoami", help="Show the authenticated user (also tests auth).").set_defaults(func=cmd_whoami)

    g = sub.add_parser("get", help="Fetch a single issue by key.")
    g.add_argument("key")
    g.add_argument("--fields", help="Comma-separated fields, or '*all'.")
    g.add_argument("--expand", help="Comma-separated expand params (e.g. changelog).")
    g.set_defaults(func=cmd_get)

    s = sub.add_parser("search", help="Search issues with JQL.")
    s.add_argument("jql", help='JQL string, e.g. "project = ABC AND status != Done".')
    s.add_argument("--fields", help="Comma-separated fields to return.")
    s.add_argument("--limit", type=int, help="Max issues to return (paginates).")
    s.set_defaults(func=cmd_search)

    c = sub.add_parser("comment", help="Add a comment (plain text -> ADF).")
    c.add_argument("key")
    c.add_argument("body", nargs="?", help="Comment text. Omit to read from stdin.")
    c.add_argument("--adf-file", help="Path to a raw ADF JSON file for rich formatting.")
    c.set_defaults(func=cmd_comment)

    u = sub.add_parser("update", help="Update fields on an issue.")
    u.add_argument("key")
    u.add_argument("--field", action="append",
                   help="key=value (value parsed as JSON if possible). Repeatable.")
    u.add_argument("--summary")
    u.add_argument("--description", help="Plain text; converted to ADF.")
    u.add_argument("--labels", help="Comma-separated labels (replaces existing).")
    u.add_argument("--priority", help="Priority name, e.g. High.")
    u.add_argument("--duedate", help="YYYY-MM-DD.")
    u.set_defaults(func=cmd_update)

    tl = sub.add_parser("transitions", help="List available status transitions.")
    tl.add_argument("key")
    tl.set_defaults(func=cmd_transitions)

    t = sub.add_parser("transition", help="Change status via a transition.")
    t.add_argument("key")
    grp = t.add_mutually_exclusive_group(required=True)
    grp.add_argument("--to", help="Target transition or status name (resolved to id).")
    grp.add_argument("--id", help="Transition id (from `transitions`).")
    t.add_argument("--resolution", help="Set resolution, e.g. Done (if the screen asks).")
    t.add_argument("--comment", help="Add a comment as part of the transition.")
    t.set_defaults(func=cmd_transition)

    a = sub.add_parser("assign", help="Set or clear the assignee.")
    a.add_argument("key")
    a.add_argument("--email", help="Assignee email (resolved to accountId).")
    a.add_argument("--account-id", help="Assignee accountId (skips lookup).")
    a.add_argument("--unassign", action="store_true", help="Clear the assignee.")
    a.set_defaults(func=cmd_assign)

    w = sub.add_parser("watch", help="Add or remove a watcher.")
    w.add_argument("key")
    w.add_argument("--email", help="Watcher email (resolved to accountId).")
    w.add_argument("--account-id", help="Watcher accountId (skips lookup).")
    w.add_argument("--remove", action="store_true", help="Remove instead of add.")
    w.set_defaults(func=cmd_watch)

    ws = sub.add_parser("watchers", help="List watchers on an issue.")
    ws.add_argument("key")
    ws.set_defaults(func=cmd_watchers)

    cr = sub.add_parser("create", help="Create a new issue.")
    cr.add_argument("--project", required=True, help="Project key, e.g. ABC.")
    cr.add_argument("--type", default="Task", help="Issue type name (default: Task).")
    cr.add_argument("--summary", required=True)
    cr.add_argument("--description", help="Plain text; converted to ADF.")
    cr.add_argument("--field", action="append",
                    help="key=value extra fields (JSON-parsed). Repeatable.")
    cr.set_defaults(func=cmd_create)

    us = sub.add_parser("users", help="Search users by email or name.")
    us.add_argument("query")
    us.set_defaults(func=cmd_users)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    cfg = Config()
    try:
        args.func(args, cfg)
    except JiraError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except BrokenPipeError:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
