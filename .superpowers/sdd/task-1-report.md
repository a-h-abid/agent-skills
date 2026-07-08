## Task

Task 1: Configuration and Input-Safety Foundation

## Scope

- Modified `skills/abd-jira-cloud/scripts/jira.py`
- Added `tests/test_jira_cli.py`

## TDD Record

### RED

Ran:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli.ConfigurationTests tests.test_jira_cli.FieldParsingTests -v
```

Observed expected failures:

- `AttributeError` for missing `validate_base_url`
- `TypeError` because `Config` did not accept an environment mapping
- `AttributeError` for missing `path_segment`
- one failing assertion because `parse_kv_json` accepted an empty key

### GREEN

Implemented:

- `validate_base_url(value: str) -> str`
- `path_segment(value: str, label: str) -> str`
- `issue_path(issue_id_or_key: str, suffix: str = "") -> str`
- `Config(environ: Mapping[str, str] | None = None)` with `require(live: bool = True)`
- empty-key rejection in `parse_kv_json`
- encoded issue-path usage for issue-specific commands

Re-ran:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli.ConfigurationTests tests.test_jira_cli.FieldParsingTests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli -v
```

Both passed with 6/6 tests green.

## Verification

Focused task coverage:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli -v
```

Result: 6 tests passed.

Broader repository unittest discovery:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Result:

- new Jira CLI tests passed
- existing repository suite reported 2 unrelated failures in `tests/test_repository_layout.py`
- failures were for `.agents` and `.codex` existing at the repository root in this workspace

These failures were not introduced by the Jira CLI changes and were left untouched.

## Self-Review

- `Config.require(live=False)` now validates only the base URL, which keeps dry-run credential-free while still preventing unsafe destinations.
- `issue_path` centralizes issue key encoding so all issue-scoped commands use a single safety boundary.
- `parse_kv_json` now rejects `=value` inputs early with a targeted CLI error.
- No external dependencies were added; code remains Python 3.8+ stdlib-only.

## Commit Notes

- Commit created after focused verification.
- Broader suite concern documented because full discovery is not clean in this workspace for unrelated reasons.

## Review Fix Addendum

### Scope

- Fixed the dry-run safety boundary so request previews validate `JIRA_BASE_URL` through `Config.require(live=False)` before emitting any JSON.
- Tightened `validate_base_url()` to reject empty subdomain labels before `.atlassian.net`.
- Added focused offline coverage for both behaviors.

### Commands Run

```bash
git status --short
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli.ConfigurationTests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli.ConfigurationTests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli -v
```

### Covering Tests

- `tests.test_jira_cli.ConfigurationTests.test_rejects_unsafe_base_urls`
- `tests.test_jira_cli.ConfigurationTests.test_dry_run_rejects_invalid_base_url_before_emitting_preview`

### Output Summary

- Baseline before the fix: `tests.test_jira_cli -v` passed 6/6 existing tests.
- RED check after adding the new tests: `ConfigurationTests -v` failed 3 checks, covering preview validation and empty-label hostnames (`https://.atlassian.net`, `https://foo..atlassian.net`).
- GREEN verification after the fix: `ConfigurationTests -v` passed 5/5 tests.
- Final focused verification: `tests.test_jira_cli -v` passed 7/7 tests.

## Final Dry-Run Safety Fix

### Scope

- Moved `cmd_transition()` config validation ahead of the dry-run preview print so invalid `JIRA_BASE_URL` values are rejected before any output is emitted.
- Switched the regression test to the exact `transition --dry-run --to ...` path and asserted stdout stays empty.

### Covering Test

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_jira_cli -v
```

### Result

- Passed: `7/7`

### Output Summary

- `test_transition_dry_run_rejects_invalid_base_url_before_emitting_preview` now exercises the real transition command path.
- Invalid `JIRA_BASE_URL` is raised before the preview line can print, and captured stdout remains empty.
