Task 2 Report: Harden HTTP Transport and Dry-Run Output

Scope
- Modified `skills/abd-jira-cloud/scripts/jira.py`
- Modified `tests/test_jira_cli.py`
- Left all other files untouched

Requirements Implemented
- Added `SameOriginRedirectHandler`
- Added module-level `HTTP_OPENER`
- Hardened `request(method, path, cfg, query=None, body=None, dry_run=False)`
- Updated `cmd_whoami` so dry-run behavior matches the other command handlers

TDD Record
- Added the Task 2 transport tests first in `tests/test_jira_cli.py`
- Ran `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli.TransportTests -v`
- Verified RED:
  - missing `HTTP_OPENER`
  - missing `SameOriginRedirectHandler`
  - focused suite exited non-zero with 8 errors across the new transport cases
- Implemented the minimal production changes in `jira.py`
- Re-ran `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli.TransportTests -v`
- Verified GREEN:
  - 7 tests ran
  - all passed

Behavior Changes
- Dry-run requests now emit exactly one JSON document through `emit(...)`
- Dry-run Authorization is always `Basic <redacted>`
- Live requests now go through a shared opener with a same-origin HTTPS-only redirect policy
- Live requests use `REQUEST_TIMEOUT`
- Empty successful responses return `{}`
- HTTP errors now:
  - bound body reads to `ERROR_BODY_LIMIT + 1`
  - redact the configured API token from the reported body
  - append `[truncated]` when the body exceeds the limit
  - include `Retry-After` when present
- Network timeouts and URL reachability failures now raise `JiraError`
- Invalid JSON responses now raise `JiraError`

Verification Run
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli -v`
  - Result: 14 tests ran, all passed
- `git diff --check`
  - Result: clean

Coverage Note
- Attempted `python3 -m coverage --version`
- Environment result: `/usr/bin/python3: No module named coverage`
- Because `coverage` is not installed here, I could not produce a coverage report without leaving the stdlib-only/offline boundary

Self-Review
- Confirmed changes stay within the two user-owned files only
- Confirmed query encoding now uses `doseq=True`, which preserves multi-value query support without affecting current tests
- Confirmed `cmd_whoami` no longer emits `{}` during dry-run and now matches the existing command pattern

Concerns
- No code concerns from the scoped Task 2 implementation
- Only environment concern: `coverage` is unavailable in this sandbox
