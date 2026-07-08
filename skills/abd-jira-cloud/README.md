# abd-jira-cloud

A dependency-free Python 3.8+ CLI skill for personal Jira Cloud issue work:
reads, JQL search, issue creation, comments, field updates, transitions,
assignees, and watchers.

## Install

Copy or symlink this directory into the skills directory supported by your
agent. Keep `SKILL.md`, `scripts/`, and `references/` together.

## Configure

Set `JIRA_BASE_URL` to the HTTPS root of your `*.atlassian.net` site, then set
the Atlassian account email and a dedicated, revocable API token:

```bash
export JIRA_BASE_URL="https://your-site.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="value-from-your-secret-manager"
```

Do not commit tokens, paste them into chat, echo them while debugging, or place
them in command arguments. The token acts with the Jira permissions of its
account, so use the least privilege practical for your work.

## Examples

Resolve `scripts/jira.py` from the installed skill directory, then run:

```bash
python3 scripts/jira.py whoami
python3 scripts/jira.py get ABC-123 --fields summary,status,assignee
python3 scripts/jira.py search "project = ABC ORDER BY updated DESC" --limit 50
python3 scripts/jira.py comment ABC-123 "Deployment completed."
python3 scripts/jira.py transition ABC-123 --to "In Progress"
python3 scripts/jira.py --dry-run update ABC-123 --summary "Previewed title"
```

Search returns at most 100 issues unless `--limit` changes the bound. `--all`
explicitly requests every page. Dry-run redacts authorization but can expose
private request URLs and bodies, so treat its output as sensitive.

## Compatibility and scope

- Python 3.8 or newer; no third-party packages.
- Jira Cloud REST API v3 at an HTTPS `*.atlassian.net` site.
- Basic auth with account email and an API token for personal/ad-hoc use.
- Not Jira Server/Data Center, OAuth, scoped-token global routing, or Jira
  Software board/sprint administration.

## Verify

Automated tests are offline:

```bash
python3 -m unittest tests.test_jira_cli -v
```

With credentials configured, `python3 scripts/jira.py whoami` is the optional
live smoke test.

See [SKILL.md](SKILL.md) for agent behavior and
[references/api-notes.md](references/api-notes.md) for Jira API details.
