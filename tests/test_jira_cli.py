from __future__ import annotations

import importlib.util
import io
import json
import socket
import tempfile
import unittest
import urllib.error
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "abd-jira-cloud" / "scripts" / "jira.py"
SPEC = importlib.util.spec_from_file_location("abd_jira_cloud_jira", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
jira = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(jira)


class ConfigurationTests(unittest.TestCase):
    def test_accepts_and_canonicalizes_jira_cloud_base_url(self) -> None:
        self.assertEqual(
            jira.validate_base_url("https://Example.atlassian.net/"),
            "https://example.atlassian.net",
        )
        self.assertEqual(
            jira.validate_base_url("https://example.atlassian.net:443"),
            "https://example.atlassian.net",
        )

    def test_rejects_unsafe_base_urls(self) -> None:
        values = (
            "http://example.atlassian.net",
            "https://atlassian.net",
            "https://.atlassian.net",
            "https://foo..atlassian.net",
            "https://example.atlassian.net.evil.test",
            "https://user:token@example.atlassian.net",
            "https://example.atlassian.net/jira",
            "https://example.atlassian.net?x=1",
            "https://example.atlassian.net#fragment",
            "https://example.atlassian.net:8443",
        )
        for value in values:
            with self.subTest(value=value), self.assertRaises(jira.JiraError):
                jira.validate_base_url(value)

    def test_live_config_requires_all_values_but_dry_run_only_needs_url(self) -> None:
        dry = jira.Config({"JIRA_BASE_URL": "https://example.atlassian.net"})
        dry.require(live=False)
        with self.assertRaisesRegex(jira.JiraError, "JIRA_EMAIL, JIRA_API_TOKEN"):
            dry.require(live=True)

    def test_path_values_are_encoded_as_one_segment(self) -> None:
        self.assertEqual(jira.path_segment("ABC/1?x=2", "issue"), "ABC%2F1%3Fx%3D2")
        self.assertEqual(jira.issue_path("ABC/1"), "/rest/api/3/issue/ABC%2F1")
        with self.assertRaises(jira.JiraError):
            jira.path_segment("bad\nkey", "issue")

    def test_transition_dry_run_rejects_invalid_base_url_before_emitting_preview(self) -> None:
        cfg = jira.Config(
            {
                "JIRA_BASE_URL": "https://.atlassian.net",
                "JIRA_EMAIL": "user@example.com",
                "JIRA_API_TOKEN": "token",
            }
        )
        args = SimpleNamespace(
            key="ABC-1",
            to="Done",
            id=None,
            resolution=None,
            comment=None,
            dry_run=True,
        )
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            with self.assertRaisesRegex(
                jira.JiraError, r"JIRA_BASE_URL must be an HTTPS \*\.atlassian\.net"
            ):
                jira.cmd_transition(args, cfg)
        self.assertEqual(stdout.getvalue(), "")


class FieldParsingTests(unittest.TestCase):
    def test_parses_json_and_plain_string_values(self) -> None:
        self.assertEqual(
            jira.parse_kv_json(['priority={"name":"High"}', "summary=Hello"]),
            {"priority": {"name": "High"}, "summary": "Hello"},
        )

    def test_rejects_missing_or_empty_field_names(self) -> None:
        for value in ("summary", "=value"):
            with self.subTest(value=value), self.assertRaises(jira.JiraError):
                jira.parse_kv_json([value])


class FakeResponse:
    def __init__(self, body=b"", status=200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.body


class TransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = jira.Config(
            {
                "JIRA_BASE_URL": "https://example.atlassian.net",
                "JIRA_EMAIL": "person@example.com",
                "JIRA_API_TOKEN": "SENTINEL_API_TOKEN",
            }
        )

    def test_dry_run_redacts_token_and_emits_one_json_value(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = jira.request("GET", "/rest/api/3/myself", self.cfg, dry_run=True)
        document = json.loads(output.getvalue())
        self.assertIsNone(result)
        self.assertEqual(document["headers"]["Authorization"], "Basic <redacted>")
        self.assertNotIn("SENTINEL_API_TOKEN", output.getvalue())

    def test_live_request_uses_timeout_and_parses_json(self) -> None:
        with mock.patch.object(
            jira.HTTP_OPENER, "open", return_value=FakeResponse(b'{"ok":true}')
        ) as opened:
            self.assertEqual(jira.request("GET", "/rest/api/3/myself", self.cfg), {"ok": True})
        self.assertEqual(opened.call_args.kwargs["timeout"], 30)

    def test_empty_success_returns_empty_object(self) -> None:
        with mock.patch.object(jira.HTTP_OPENER, "open", return_value=FakeResponse()):
            self.assertEqual(jira.request("PUT", "/rest/api/3/issue/ABC-1", self.cfg), {})

    def test_http_error_is_bounded_redacted_and_reports_retry_after(self) -> None:
        body = ("SENTINEL_API_TOKEN" + "x" * (jira.ERROR_BODY_LIMIT + 10)).encode()
        error = urllib.error.HTTPError(
            "https://example.atlassian.net/rest/api/3/search/jql",
            429,
            "Too Many Requests",
            {"Retry-After": "7"},
            io.BytesIO(body),
        )
        with mock.patch.object(jira.HTTP_OPENER, "open", side_effect=error):
            with self.assertRaises(jira.JiraError) as raised:
                jira.request("POST", "/rest/api/3/search/jql", self.cfg)
        message = str(raised.exception)
        self.assertIn("Retry-After: 7", message)
        self.assertIn("[truncated]", message)
        self.assertNotIn("SENTINEL_API_TOKEN", message)

    def test_timeout_and_malformed_json_become_jira_errors(self) -> None:
        for effect in (
            socket.timeout("slow"),
            urllib.error.URLError("dns failure"),
            FakeResponse(b"not-json"),
        ):
            with self.subTest(effect=type(effect).__name__):
                context = (
                    mock.patch.object(jira.HTTP_OPENER, "open", side_effect=effect)
                    if isinstance(effect, Exception)
                    else mock.patch.object(jira.HTTP_OPENER, "open", return_value=effect)
                )
                with context, self.assertRaises(jira.JiraError):
                    jira.request("GET", "/rest/api/3/myself", self.cfg)

    def test_redirect_policy_rejects_cross_origin_and_downgrade(self) -> None:
        handler = jira.SameOriginRedirectHandler()
        request = urllib.request.Request("https://example.atlassian.net/rest/api/3/myself")
        for destination in (
            "https://evil.test/steal",
            "http://example.atlassian.net/steal",
        ):
            with self.subTest(destination=destination), self.assertRaises(jira.JiraError):
                handler.redirect_request(request, None, 302, "Found", {}, destination)

    def test_redirect_policy_rejects_credentials_in_redirect_url(self) -> None:
        handler = jira.SameOriginRedirectHandler()
        request = urllib.request.Request("https://example.atlassian.net/rest/api/3/myself")
        with self.assertRaises(jira.JiraError):
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://user:pass@example.atlassian.net/steal",
            )

    def test_redirect_policy_rejects_malformed_redirect_url(self) -> None:
        handler = jira.SameOriginRedirectHandler()
        request = urllib.request.Request("https://example.atlassian.net/rest/api/3/myself")
        with self.assertRaises(jira.JiraError):
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://example.atlassian.net:bad/steal",
            )

    def test_redirect_policy_rejects_explicit_invalid_port_zero(self) -> None:
        handler = jira.SameOriginRedirectHandler()
        request = urllib.request.Request("https://example.atlassian.net/rest/api/3/myself")
        with self.assertRaises(jira.JiraError):
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://example.atlassian.net:0/steal",
            )

    def test_redirect_policy_allows_same_origin_https(self) -> None:
        handler = jira.SameOriginRedirectHandler()
        request = urllib.request.Request("https://example.atlassian.net/rest/api/3/myself")
        redirected = handler.redirect_request(
            request, None, 302, "Found", {}, "/rest/api/3/myself?moved=1"
        )
        self.assertEqual(
            redirected.full_url,
            "https://example.atlassian.net/rest/api/3/myself?moved=1",
        )


class HelperBehaviorTests(unittest.TestCase):
    def test_text_to_adf_handles_empty_lines_and_paragraphs(self) -> None:
        self.assertEqual(
            jira.text_to_adf(""),
            {"type": "doc", "version": 1, "content": [{"type": "paragraph"}]},
        )
        self.assertEqual(
            jira.text_to_adf("one\ntwo\n\nthree")["content"],
            [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "one"},
                        {"type": "hardBreak"},
                        {"type": "text", "text": "two"},
                    ],
                },
                {"type": "paragraph", "content": [{"type": "text", "text": "three"}]},
            ],
        )

    def test_account_resolution_is_exact_or_unambiguous(self) -> None:
        cfg = jira.Config({"JIRA_BASE_URL": "https://example.atlassian.net"})
        exact = [
            {"emailAddress": "other@example.com", "accountId": "other"},
            {"emailAddress": "person@example.com", "accountId": "exact"},
        ]
        with mock.patch.object(jira, "request", return_value=exact):
            self.assertEqual(jira.resolve_account_id(cfg, "PERSON@example.com"), "exact")
        with mock.patch.object(jira, "request", return_value=[{"accountId": "only"}]):
            self.assertEqual(jira.resolve_account_id(cfg, "Only Person"), "only")
        with mock.patch.object(jira, "request", return_value=[]):
            with self.assertRaisesRegex(jira.JiraError, "No user found"):
                jira.resolve_account_id(cfg, "missing")
        ambiguous = [
            {"displayName": "One", "accountId": "one"},
            {"displayName": "Two", "accountId": "two"},
        ]
        with mock.patch.object(jira, "request", return_value=ambiguous):
            with self.assertRaisesRegex(jira.JiraError, "matched 2 users"):
                jira.resolve_account_id(cfg, "person")


class CommandBehaviorTests(unittest.TestCase):
    def invoke(self, argv, responses):
        calls = []
        queue = list(responses)

        def fake_request(method, path, cfg, query=None, body=None, dry_run=False, unverified_identity=False):
            calls.append((method, path, query, body, dry_run))
            return queue.pop(0)

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(jira, "request", side_effect=fake_request):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = jira.main(argv)
        return status, stdout.getvalue(), stderr.getvalue(), calls

    def test_command_request_contracts(self) -> None:
        cases = (
            (["whoami"], [{"accountId": "me"}], "GET", "/rest/api/3/myself", None, None),
            (["get", "ABC-1", "--fields", "summary,status"], [{"key": "ABC-1"}], "GET", "/rest/api/3/issue/ABC-1", {"fields": "summary,status"}, None),
            (["comment", "ABC-1", "hello"], [{"id": "10"}], "POST", "/rest/api/3/issue/ABC-1/comment", None, {"body": jira.text_to_adf("hello")}),
            (["update", "ABC-1", "--summary", "New"], [{}], "PUT", "/rest/api/3/issue/ABC-1", None, {"fields": {"summary": "New"}}),
            (["transitions", "ABC-1"], [{"transitions": []}], "GET", "/rest/api/3/issue/ABC-1/transitions", None, None),
            (["transition", "ABC-1", "--id", "31"], [{}], "POST", "/rest/api/3/issue/ABC-1/transitions", None, {"transition": {"id": "31"}}),
            (["assign", "ABC-1", "--account-id", "acct"], [{}], "PUT", "/rest/api/3/issue/ABC-1/assignee", None, {"accountId": "acct"}),
            (["watch", "ABC-1", "--account-id", "acct"], [{}], "POST", "/rest/api/3/issue/ABC-1/watchers", None, "acct"),
            (["watch", "ABC-1", "--account-id", "acct", "--remove"], [{}], "DELETE", "/rest/api/3/issue/ABC-1/watchers", {"accountId": "acct"}, None),
            (["watchers", "ABC-1"], [{}], "GET", "/rest/api/3/issue/ABC-1/watchers", None, None),
            (["create", "--project", "ABC", "--summary", "New"], [{"key": "ABC-2"}], "POST", "/rest/api/3/issue", None, {"fields": {"project": {"key": "ABC"}, "issuetype": {"name": "Task"}, "summary": "New"}}),
            (["users", "person@example.com"], [[]], "GET", "/rest/api/3/user/search", {"query": "person@example.com"}, None),
        )
        for argv, responses, method, path, query, body in cases:
            with self.subTest(command=argv[0]):
                status, stdout, _, calls = self.invoke(argv, responses)
                self.assertEqual(status, 0)
                self.assertEqual((calls[-1][0], calls[-1][1]), (method, path))
                self.assertEqual(calls[-1][2], query)
                self.assertEqual(calls[-1][3], body)
                json.loads(stdout)

    def test_comment_accepts_stdin_and_adf_file(self) -> None:
        with mock.patch.object(jira.sys, "stdin", io.StringIO("from stdin")):
            status, _, _, calls = self.invoke(["comment", "ABC-1"], [{"id": "10"}])
        self.assertEqual(status, 0)
        self.assertEqual(calls[-1][3], {"body": jira.text_to_adf("from stdin")})

        adf = {"type": "doc", "version": 1, "content": [{"type": "paragraph"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comment.json"
            path.write_text(json.dumps(adf), encoding="utf-8")
            status, _, _, calls = self.invoke(
                ["comment", "ABC-1", "--adf-file", str(path)], [{"id": "11"}]
            )
        self.assertEqual(status, 0)
        self.assertEqual(calls[-1][3], {"body": adf})

    def test_search_defaults_to_100_and_honors_explicit_all(self) -> None:
        status, stdout, _, calls = self.invoke(
            ["search", "project = ABC"],
            [{"issues": [{"key": "ABC-1"}], "isLast": True}],
        )
        self.assertEqual(status, 0)
        self.assertEqual(calls[0][3]["maxResults"], 100)
        self.assertEqual(json.loads(stdout)["count"], 1)

        status, _, _, calls = self.invoke(
            ["search", "project = ABC", "--all"],
            [
                {"issues": [{"key": "ABC-1"}], "nextPageToken": "next", "isLast": False},
                {"issues": [{"key": "ABC-2"}], "isLast": True},
            ],
        )
        self.assertEqual(status, 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][3]["nextPageToken"], "next")

    def test_search_rejects_repeated_page_token(self) -> None:
        status, _, stderr, _ = self.invoke(
            ["search", "project = ABC", "--all"],
            [
                {"issues": [], "nextPageToken": "same", "isLast": False},
                {"issues": [], "nextPageToken": "same", "isLast": False},
            ],
        )
        self.assertEqual(status, 1)
        self.assertIn("repeated page token", stderr)

        status, _, stderr, _ = self.invoke(
            ["search", "project = ABC", "--all"],
            [{"issues": [], "isLast": False}],
        )
        self.assertEqual(status, 1)
        self.assertIn("no next page token", stderr)

    def test_transition_name_must_resolve_uniquely(self) -> None:
        listing = {
            "transitions": [
                {"id": "1", "name": "Close", "to": {"name": "Done"}},
                {"id": "2", "name": "Resolve", "to": {"name": "Done"}},
            ]
        }
        status, _, stderr, calls = self.invoke(
            ["transition", "ABC-1", "--to", "Done"], [listing]
        )
        self.assertEqual(status, 1)
        self.assertIn("matched multiple transitions", stderr)
        self.assertEqual(len(calls), 1)

    def test_parser_rejects_conflicting_identity_and_bad_limits(self) -> None:
        parser = jira.build_parser()
        invalid = (
            ["assign", "ABC-1", "--email", "a@example.com", "--unassign"],
            ["watch", "ABC-1", "--email", "a@example.com", "--account-id", "acct"],
            ["search", "project = ABC", "--limit", "0"],
            ["search", "project = ABC", "--limit", "2", "--all"],
        )
        for argv in invalid:
            with self.subTest(argv=argv), self.assertRaises(SystemExit) as raised:
                parser.parse_args(argv)
            self.assertEqual(raised.exception.code, 2)

    def test_invalid_adf_file_is_a_clean_command_error(self) -> None:
        with self.subTest(case="missing"), redirect_stderr(io.StringIO()):
            status = jira.main(["comment", "ABC-1", "--adf-file", "/missing/adf.json"])
            self.assertEqual(status, 1)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text("not-json", encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                status = jira.main(["comment", "ABC-1", "--adf-file", str(path)])
            self.assertEqual(status, 1)
            self.assertIn("Invalid JSON", stderr.getvalue())

    def test_update_convenience_flags_override_generic_fields(self) -> None:
        status, _, _, calls = self.invoke(
            ["update", "ABC-1", "--field", "summary=Old", "--summary", "New"], [{}]
        )
        self.assertEqual(status, 0)
        self.assertEqual(calls[-1][3], {"fields": {"summary": "New"}})

    def test_whoami_dry_run_emits_one_json_value(self) -> None:
        env = {"JIRA_BASE_URL": "https://example.atlassian.net"}
        output = io.StringIO()
        with mock.patch.dict(jira.os.environ, env, clear=True), redirect_stdout(output):
            self.assertEqual(jira.main(["--dry-run", "whoami"]), 0)
        document = json.loads(output.getvalue())
        self.assertEqual(document["method"], "GET")
        self.assertEqual(document["url"], "https://example.atlassian.net/rest/api/3/myself")

    def test_transition_dry_run_by_name_emits_one_json_value(self) -> None:
        env = {
            "JIRA_BASE_URL": "https://example.atlassian.net",
            "JIRA_EMAIL": "",
            "JIRA_API_TOKEN": "",
        }
        output = io.StringIO()
        with mock.patch.dict(jira.os.environ, env, clear=True), redirect_stdout(output):
            self.assertEqual(jira.main(["--dry-run", "transition", "ABC-1", "--to", "Done"]), 0)
        document = json.loads(output.getvalue())
        self.assertEqual(document["body"]["transition"]["id"], "<resolved:Done>")


class DryRunIdentityResolutionTests(unittest.TestCase):
    ENV = {"JIRA_BASE_URL": "https://example.atlassian.net"}

    def _dry_run(self, argv: list[str]) -> dict:
        output = io.StringIO()
        with mock.patch.dict(jira.os.environ, self.ENV, clear=True), mock.patch.object(
            jira.HTTP_OPENER, "open", side_effect=AssertionError("network call in dry-run")
        ) as opened, redirect_stdout(output):
            self.assertEqual(jira.main(["--dry-run", *argv]), 0)
        self.assertEqual(opened.call_count, 0)
        # json.loads raises on trailing data, so this also asserts the
        # one-JSON-value-per-preview output contract.
        return json.loads(output.getvalue())

    def test_email_assign_and_watch_dry_runs_are_not_mistaken_for_verified_identity_resolution(self) -> None:
        flagged = (
            ["assign", "ABC-1", "--email", "person@example.com"],
            ["watch", "ABC-1", "--email", "person@example.com"],
            ["watch", "ABC-1", "--email", "person@example.com", "--remove"],
        )
        for argv in flagged:
            with self.subTest(argv=argv):
                document = self._dry_run(argv)
                self.assertEqual(
                    document["identity_resolution"], "not verified in dry-run"
                )

        unflagged = (
            ["assign", "ABC-1", "--account-id", "acct"],
            ["assign", "ABC-1", "--unassign"],
            ["watch", "ABC-1", "--account-id", "acct"],
            ["watch", "ABC-1", "--account-id", "acct", "--remove"],
        )
        for argv in unflagged:
            with self.subTest(argv=argv):
                document = self._dry_run(argv)
                self.assertNotIn("identity_resolution", document)


if __name__ == "__main__":
    unittest.main()
