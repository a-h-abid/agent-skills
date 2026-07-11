# Codebase Audit Remediation Roadmap

## Scope and Prioritization

This roadmap operationalizes the three "Worth considering" findings confirmed in `docs/audits/2026-07-10-codebase-audit.md` for the pinned revision `8605a17c906d715c58b9c1a2511b8d0079446a4a` of `agent-skills`. No Blocking or Should-fix findings were confirmed, so there is no P0 or P1 remediation work. All three reportable findings (`AUD-CORE-001`, `AUD-JIRA-001`, `AUD-REL-001`) are traced 1:1 by the three roadmap items below (`RM-001`–`RM-003`), consistent with the audit's `roadmap-seeds.jsonl` (3 seeds, no standalone hardening goals). The completed Codex Security 0.1.11 bundle recorded by the audit has zero canonical reportable findings; its reproduced top-level-symlink candidate is confirmed but suppressed after attack-path analysis, so it creates neither a remediation item nor a standalone hardening goal. Priority is assigned independently of severity: all three findings share "Worth considering" severity, but each is bucketed into P2 or P3 based on release-integrity impact and urgency, not on how the finding was discovered.

## Dependency and Sequencing Summary

The three remediations are independent — they touch disjoint files (`.github/workflows/*.yml`, `scripts/package_skills.py`, `skills/abd-jira-cloud/scripts/jira.py` + `SKILL.md`) with no shared state, so none blocks another and each lists `Dependencies: None`. RM IDs are still assigned in a deliberate implementation order rather than arbitrarily:

1. **RM-001** (pin CI/release Actions to SHA, `AUD-REL-001`) is sequenced first because it hardens the release pipeline itself — the same pipeline that will publish the artifact touched by RM-002. Doing supply-chain hardening before packaging changes ensures every subsequent release (including the one that ships RM-002's fix) already benefits from pinned, non-mutable action references.
2. **RM-002** (exclude `__pycache__`/`*.pyc` from packaged archives, `AUD-CORE-001`) follows, fixing the packaging hygiene defect so the next tagged release (now built on a hardened pipeline) produces deterministic, clean archives.
3. **RM-003** (fix dry-run identity-resolution trust gap for `--email` assign/watch, `AUD-JIRA-001`) is last: it is scoped to a single skill's documentation/behavior mismatch, is lowest priority (P3), and has no interaction with the release or packaging pipeline, so it carries no sequencing risk relative to RM-001/RM-002.

No item depends on partial completion of another; all three can also be implemented in parallel without any unsafe intermediate state.

## P0 — Immediate Containment or Release Blocking

None.

## P1 — Next Focused Material-Risk Changes

None.

## P2 — Planned Hardening, Compatibility, and Maintainability

- RM-001 — Pin third-party GitHub Actions to commit SHAs in CI and release workflows
- RM-002 — Exclude `__pycache__`/`*.pyc` from published `.skill` archives

## P3 — Optional Hygiene and Future-Scale Improvements

- RM-003 — Make dry-run assign/watch by `--email` validate or disclose unverified identity resolution

## Remediation Items

<!-- roadmap-items:start -->

### RM-001 — Pin third-party GitHub Actions to commit SHAs in CI and release workflows

- **Priority:** P2
- **Traceability:** AUD-REL-001
- **Effort:** S
- **Dependencies:** None
- **Affected files:** `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `.github/dependabot.yml`
- **Why now:** `release.yml` runs with `permissions: contents: write` and an ephemeral `github.token`, publishing real GitHub Release artifacts (per-skill `.skill` archives, collection ZIP, `SHA256SUMS`) on every tag push. Both workflows currently reference `actions/checkout@v4` and `actions/setup-python@v5` by mutable major-version tag rather than a pinned commit SHA, so a repointed upstream tag could execute unreviewed code with write access before checksums are computed. This is standard, low-effort supply-chain hardening (per GitHub's own guidance) and is sequenced first because it hardens the same release pipeline that will publish the artifact affected by RM-002.
- **Acceptance criteria:**
  - Every `uses: actions/...` reference in `ci.yml` and `release.yml` is pinned to a full commit SHA with a version comment (e.g. `actions/checkout@<sha> # v4.x.x`).
  - `.github/dependabot.yml` configures Dependabot's `github-actions` ecosystem for the repository root with a recurring schedule, so SHA pins receive update pull requests.
  - CI and release workflows continue to pass after repinning.
- **Verification commands:**
  - `python3 -c "from pathlib import Path; import re; refs = [match.groups() for path in (Path('.github/workflows/ci.yml'), Path('.github/workflows/release.yml')) for match in re.finditer(r'^\\s*uses:\\s*(actions/[^\\s#]+)(?:\\s+#\\s+([^\\n]+))?\\s*$', path.read_text(), re.MULTILINE)]; config = Path('.github/dependabot.yml').read_text(); assert refs and all(re.fullmatch(r'actions/[A-Za-z0-9_.-]+@[0-9a-f]{40}', ref) and comment and re.fullmatch(r'v\\d+\\.\\d+\\.\\d+', comment.strip()) for ref, comment in refs), refs; assert re.search(r'package-ecosystem:\\s*\"github-actions\"', config) and re.search(r'directory:\\s*\"/\"', config) and re.search(r'schedule:\\s*\\n\\s*interval:\\s*\"(?:daily|weekly|monthly)\"', config), config"`
  - `python3 -m unittest discover -s tests -v`
  - `python3 scripts/validate_skills.py`
  - `python3 scripts/package_skills.py --version v0.0.0 --dry-run`

### RM-002 — Exclude `__pycache__`/`*.pyc` from published `.skill` archives

- **Priority:** P2
- **Traceability:** AUD-CORE-001
- **Effort:** S
- **Dependencies:** None
- **Affected files:** `scripts/package_skills.py`
- **Why now:** `scripts/package_skills.py`'s file-collection step (`source_files`, L33-39) recursively collects every regular file under a skill directory without consulting `.gitignore`, so stale interpreter-specific bytecode (e.g. `skills/abd-jira-cloud/scripts/__pycache__/jira.cpython-312.pyc`) can leak into published `.skill` archives whenever it happens to be present on disk at packaging time. This makes archive contents non-deterministic and interpreter-version-dependent, and ships unnecessary compiled bytes in a package that otherwise contains only source and markdown. Not exploitable and not release-blocking, but cheap to fix and worth doing before the next tagged release to keep archives clean and reproducible; sequenced after RM-001 so the fix ships through an already-hardened release pipeline.
- **Acceptance criteria:**
  - `package_skills.py`'s file-collection step skips `__pycache__` directories and `*.pyc`/`*.pyo` files regardless of whether `PYTHONDONTWRITEBYTECODE` is set.
  - Re-running the Step-4 workflow-order proof (fresh clone, `env -u PYTHONDONTWRITEBYTECODE`, real test/validate/package order) yields `generated_members == []` for every packaged skill.
  - Existing packaging test suite (`tests/test_package_skills.py`) continues to pass.
- **Verification commands:**
  - `env -u PYTHONDONTWRITEBYTECODE python3 -m unittest discover -s tests -v`
  - `tmp=$(mktemp -d); env -u PYTHONDONTWRITEBYTECODE python3 scripts/package_skills.py --version v0.0.0 --output "$tmp/dist" && python3 -c "from pathlib import Path; import sys, zipfile; names = [name for archive in Path(sys.argv[1]).glob('*.skill') for name in zipfile.ZipFile(archive).namelist()]; forbidden = [name for name in names if '__pycache__' in name.split('/') or name.endswith(('.pyc', '.pyo'))]; assert not forbidden, forbidden" "$tmp/dist"; status=$?; rm -rf "$tmp"; exit $status`
  - `python3 -m unittest discover -s tests -v`
  - `python3 scripts/validate_skills.py`
  - `python3 scripts/package_skills.py --version v0.0.0 --dry-run`

### RM-003 — Make dry-run assign/watch by `--email` validate or disclose unverified identity resolution

- **Priority:** P3
- **Traceability:** AUD-JIRA-001
- **Effort:** S
- **Dependencies:** None
- **Affected files:** `skills/abd-jira-cloud/scripts/jira.py`, `skills/abd-jira-cloud/SKILL.md`
- **Why now:** `SKILL.md`'s Operating rule instructs dry-running ambiguous writes before confirming them, but for `--email`-based `assign`/`watch`, `resolve_account_id()` (jira.py:209-232) short-circuits under `--dry-run` and returns a placeholder `accountId` without ever performing the read-only `/user/search` lookup, so an agent following the documented safety practice sees a clean preview even when the email is ambiguous or unmatched. The live path already enforces correctness (verified by `tests/test_jira_cli.py::HelperBehaviorTests::test_account_resolution_is_exact_or_unambiguous`), so this is a documentation/UX trust gap rather than a live-data risk — lowest priority of the three findings, with no interaction with the release or packaging pipeline, so it is sequenced last.
- **Acceptance criteria:**
  - Dry-run `assign`/`watch` with `--email` either performs the read-only `/user/search` lookup and surfaces zero-match/multi-match ambiguity, or the dry-run JSON output explicitly flags `identity_resolution` as not verified in dry-run.
  - `SKILL.md`'s guidance about dry-running ambiguous writes is updated if needed to accurately describe the `--email` dry-run behavior.
  - Existing `jira.py` test suite continues to pass.
- **Verification commands:**
  - `python3 -m unittest tests.test_jira_cli.DryRunIdentityResolutionTests.test_email_assign_and_watch_dry_runs_are_not_mistaken_for_verified_identity_resolution`
  - `python3 -m unittest discover -s tests -v`
  - `python3 scripts/validate_skills.py`
  - `python3 scripts/package_skills.py --version v0.0.0 --dry-run`

<!-- roadmap-items:end -->

## Deferred Investigation Items

None. The formerly deferred Codex Security scan completed as bundle `8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z`, whose canonical `findings.json` is empty. The only reconciled security candidate has reproducible proof and completed validation/attack-path receipts but is suppressed: the demonstrated path requires a privileged source-tree writer and maintainer-controlled release, with no lower-privileged trigger evidenced. It is retained in the audit for traceability, not deferred for promotion, and has no associated hardening goal or roadmap item.

## Verification Matrix

| RM ID | Traceability | Acceptance-criterion summary | Focused command | Broader regression commands |
|---|---|---|---|---|
| RM-001 | AUD-REL-001 | All `actions/checkout` and `actions/setup-python` references in `ci.yml`/`release.yml` pinned to full commit SHAs with version comments; `.github/dependabot.yml` configures recurring root-level `github-actions` updates; workflows continue to pass. | `python3 -c "from pathlib import Path; import re; refs = [match.groups() for path in (Path('.github/workflows/ci.yml'), Path('.github/workflows/release.yml')) for match in re.finditer(r'^\\s*uses:\\s*(actions/[^\\s#]+)(?:\\s+#\\s+([^\\n]+))?\\s*$', path.read_text(), re.MULTILINE)]; config = Path('.github/dependabot.yml').read_text(); assert refs and all(re.fullmatch(r'actions/[A-Za-z0-9_.-]+@[0-9a-f]{40}', ref) and comment and re.fullmatch(r'v\\d+\\.\\d+\\.\\d+', comment.strip()) for ref, comment in refs), refs; assert re.search(r'package-ecosystem:\\s*\"github-actions\"', config) and re.search(r'directory:\\s*\"/\"', config) and re.search(r'schedule:\\s*\\n\\s*interval:\\s*\"(?:daily|weekly|monthly)\"', config), config"` | `python3 -m unittest discover -s tests -v`; `python3 scripts/validate_skills.py`; `python3 scripts/package_skills.py --version v0.0.0 --dry-run` |
| RM-002 | AUD-CORE-001 | `package_skills.py` excludes `__pycache__`/`*.pyc`/`*.pyo` from collected skill files; workflow-order proof yields `generated_members == []`; packaging test suite passes. | `tmp=$(mktemp -d); env -u PYTHONDONTWRITEBYTECODE python3 scripts/package_skills.py --version v0.0.0 --output "$tmp/dist" && python3 -c "from pathlib import Path; import sys, zipfile; names = [name for archive in Path(sys.argv[1]).glob('*.skill') for name in zipfile.ZipFile(archive).namelist()]; forbidden = [name for name in names if '__pycache__' in name.split('/') or name.endswith(('.pyc', '.pyo'))]; assert not forbidden, forbidden" "$tmp/dist"; status=$?; rm -rf "$tmp"; exit $status` | `env -u PYTHONDONTWRITEBYTECODE python3 -m unittest discover -s tests -v`; `python3 -m unittest discover -s tests -v`; `python3 scripts/validate_skills.py`; `python3 scripts/package_skills.py --version v0.0.0 --dry-run` |
| RM-003 | AUD-JIRA-001 | Dry-run `--email` assign/watch either performs the `/user/search` lookup and surfaces ambiguity, or explicitly flags `identity_resolution` as unverified; `SKILL.md` updated to match actual behavior; jira.py test suite passes. | `python3 -m unittest tests.test_jira_cli.DryRunIdentityResolutionTests.test_email_assign_and_watch_dry_runs_are_not_mistaken_for_verified_identity_resolution` | `python3 -m unittest discover -s tests -v`; `python3 scripts/validate_skills.py`; `python3 scripts/package_skills.py --version v0.0.0 --dry-run` |
