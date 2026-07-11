# Full Codebase Audit: `agent-skills`

## Executive Verdict

This is a read-only audit of the pinned revision `8605a17c906d715c58b9c1a2511b8d0079446a4a` of the `agent-skills` repository — exactly 40 tracked files, publishing 2 skills (`abd-code-review`, `abd-jira-cloud`). The codebase is small, well-tested, and disciplined: 54 unit tests pass, both skills validate against the packaging schema, and a packaging dry run succeeds cleanly. No Blocking or Should-fix findings were confirmed. Three "Worth considering" findings were confirmed with direct evidence: a packaging hygiene defect that ships stale `__pycache__` bytecode into the public `.skill` archive (`AUD-CORE-001`), a documentation/behavior gap where Jira dry-run cannot detect ambiguous email identity resolution for `assign`/`watch` even though `SKILL.md` implies it should (`AUD-JIRA-001`), and a supply-chain hardening gap where CI/release workflows pin third-party GitHub Actions by floating major-version tag rather than commit SHA (`AUD-REL-001`). The completed Codex Security 0.1.11 bundle found zero reportable findings; it did validate a top-level skill-directory symlink archive-boundary defect, retained here as `AUD-SEC-001` / `PKG-SYMLINK-ROOT-001`, but final attack-path policy suppresses it because only a privileged source/release actor can exploit it. Overall the repository is in a shippable, well-guarded state, with three small, well-scoped hardening items recommended before or shortly after the next tagged release.

## Audit Identity and Scope

- **Pinned target revision:** `8605a17c906d715c58b9c1a2511b8d0079446a4a` — the full, immutable subject of this audit. All findings, coverage rows, and receipts cite paths and line ranges as they exist at this exact revision.
- **Tracked file count at the pinned revision:** exactly 40 files (verified via `git ls-tree -r --name-only 8605a17c906d715c58b9c1a2511b8d0079446a4a`), covering root docs/config, `.github/workflows/`, `scripts/`, `tests/`, and the two published skill directories under `skills/`.
- **Published skills:** `abd-code-review` and `abd-jira-cloud` (2 skills).
- **Source repository HEAD at audit start:** `e1a48c680711c773755507bddf8d8d1c3670bc9b` (from `audit-context.env`, `HEAD_AT_START`). The pinned revision `8605a17c906d715c58b9c1a2511b8d0079446a4a` is an ancestor of this HEAD; the audit deliberately reviews the pinned tree, not the moving HEAD.
- **Audit start timestamp (UTC):** `2026-07-10T19:55:28Z` (`STARTED_AT` in `audit-context.env`).
- **Audit checkout:** a dedicated read-only clone at `/tmp/agent-skills-audit-8605a17c906d715c58b9c1a2511b8d0079446a4a/agent-skills`, isolated from the live working repository at `/home/abid/dev-projects/abd/agent-skills` where this report is committed.
- **Working-tree state at audit start:** the source repository's working tree was clean relative to its own HEAD (`evidence/start/source-status.txt` is empty — no uncommitted changes); the only ignored, untracked paths present were `.superpowers/`, `scripts/__pycache__/`, `skills/abd-jira-cloud/scripts/__pycache__/`, and `tests/__pycache__/` (`evidence/start/ignored-status.txt`).
- **Governing design document:** execution of this audit is governed by the **revised** `docs/superpowers/plans/2026-07-11-codebase-audit.md` plan (dated one day after the pinned revision's tree), not by the pinned tree's `docs/superpowers/specs/2026-07-10-codebase-audit-design.md`. The pinned design document is treated strictly as **contextual, historical evidence** of intent as of the pin date — its content is cross-checked for contradictions but does not control how this audit is actually executed. See "Drift from the Pinned Tree" for the mechanics of how this appears as apparent post-pin drift in the live repository.

## Drift from the Pinned Tree

The live repository (`/home/abid/dev-projects/abd/agent-skills`, where this report is written and committed) has diverged from the pinned tree `8605a17c906d715c58b9c1a2511b8d0079446a4a` by two committed changes (evidence: `$EVIDENCE_DIR/start/committed-drift.txt` and `$EVIDENCE_DIR/start/committed-drift-stat.txt`):

```
A	docs/superpowers/plans/2026-07-11-codebase-audit.md
M	docs/superpowers/specs/2026-07-10-codebase-audit-design.md
```

```
 .../superpowers/plans/2026-07-11-codebase-audit.md | 1517 ++++++++++++++++++++
 .../specs/2026-07-10-codebase-audit-design.md      |   77 +-
 2 files changed, 1577 insertions(+), 17 deletions(-)
```

Interpretation: the added file, `docs/superpowers/plans/2026-07-11-codebase-audit.md`, is the **revised audit design that governs this very audit's execution** (see "Audit Identity and Scope"). It was authored and committed to the live repository one day after the pinned revision, which is why it does not exist in the pinned tree and appears as an `A` (added) row of post-pin drift rather than as part of the 40-file pinned inventory. The modified file, `docs/superpowers/specs/2026-07-10-codebase-audit-design.md`, is the **original, pinned design document being superseded/refined** by the revised plan; its post-pin edits reflect that refinement process, not a change to the subject matter under audit. Neither drifted file is itself part of the audited 40-file pinned tree's *behavior* — both are audit-process artifacts, not application code, and neither affects any finding, candidate, or coverage row in this report. The pinned copy of `docs/superpowers/specs/2026-07-10-codebase-audit-design.md`, as it existed at the pin, is still reviewed and included as a normal `contextual` row in the Coverage Inventory (see Appendix A) with its content cross-checked against the revised plan for contradictions — none were found that affect audit scope or findings.

## Method and Evidence

Every reviewed file was read against the exact pinned blob at `8605a17c906d715c58b9c1a2511b8d0079446a4a`, using a dedicated read-only checkout so the live repository (where this report is written) was never used as an audit source. Findings and coverage receipts cite exact line ranges or full-file ranges as read at the pin. All reconciliation inputs consumed by this task are treated as final and canonical:

- `$EVIDENCE_DIR/reconciliation/coverage.jsonl` — 49 rows (40 `pinned tracked` + 9 `ignored/generated`), one per audited path.
- `$EVIDENCE_DIR/reconciliation/candidates.jsonl` — 4 canonical candidates: 3 reportable and 1 confirmed-but-suppressed candidate with alias `PKG-SYMLINK-ROOT-001`.
- `$EVIDENCE_DIR/reconciliation/roadmap-seeds.jsonl` — 3 roadmap seeds, each tracing 1:1 to one of the three findings (no standalone hardening goals).
- `$EVIDENCE_DIR/reconciliation/security-crosswalk.jsonl` — 1 reconciled Codex Security candidate receipt, linking `AUD-SEC-001` to `PKG-SYMLINK-ROOT-001` and its validation and attack-path artifacts.

No source file was re-reviewed outside these canonical reconciliation inputs; this report is a synthesis and presentation layer over already-finalized review evidence, not a fresh pass over the source tree.

## Baseline and Available Tooling

Baseline commands were run against the pinned checkout before any review began, to establish that the pinned revision is in a healthy, working state (evidence: `$EVIDENCE_DIR/baseline/`):

| Check | Command | Exit code | Result |
|---|---|---|---|
| Unit tests | `python3 -m unittest discover -s tests -v` | 0 | 54 tests pass (`unit-tests.log`, `unit-tests.exit`) |
| Skill validation | `python3 scripts/validate_skills.py` | 0 | "Validated 2 skill(s)." (`validate-skills.log`, `validate-skills.exit`) |
| Packaging dry run | `python3 scripts/package_skills.py --dry-run ...` | 0 | "Packaging dry run passed." (`package-dry-run.log`, `package-dry-run.exit`) |
| Shell linting | `shellcheck` over `*.sh` | 0 | No `.sh` files found in the repository; shellcheck has no applicable targets (`shellcheck.log`, `shellcheck.exit`) |

**Tool availability** (evidence: `$EVIDENCE_DIR/baseline/tools.tsv`):

| Tool | Status |
|---|---|
| shellcheck | installed (`/usr/bin/shellcheck`) |
| actionlint | not installed |
| bandit | not installed |
| gitleaks | not installed |
| mypy | not installed |
| ruff | not installed |
| semgrep | not installed |

Six of the seven candidate static-analysis/linting tools were unavailable in the audit execution environment and are recorded here as unavailable rather than silently skipped; no finding in this report depended on any of them, and no claim of tool-based coverage is made for actionlint, bandit, gitleaks, mypy, ruff, or semgrep. All Jira-related review in this audit used the offline test harness and dry-run flag only; the stricter no-live-Jira rule was followed throughout — no live Jira Cloud instance was contacted at any point in this audit (all Jira evidence, including the `AUD-JIRA-001` validation command, uses a dummy `JIRA_API_TOKEN` value and `--dry-run`).

## Coverage Overview

Every one of the 40 pinned tracked files at revision `8605a17c906d715c58b9c1a2511b8d0079446a4a` was read and reviewed; the 9 ignored/generated paths present in the working tree at audit start (all `__pycache__`/`.pyc` artifacts plus the `.superpowers/sdd/progress.md` process file) were separately accounted for rather than silently skipped. Full per-path detail, including receipts and candidate linkage, is in Appendix A: Coverage Inventory. Five files (the historical `docs/superpowers/` plan/spec documents) are marked `contextual` — reviewed for contradictions against the revised governing plan, not as subjects of a behavioral finding.

## Candidate Disposition Ledger

<!-- candidate-ledger:start -->
| Candidate ID | Category | Final disposition | Confidence | Main severity | Security IDs | Closure evidence |
|---|---|---|---|---|---|---|
| AUD-CORE-001 | release | reportable | confirmed | Worth considering | — | Reproduced via fresh-clone workflow-order proof (`$EVIDENCE_DIR/proofs/generated-skill-content/workflow-order.log`): `generated_members=['abd-jira-cloud/scripts/__pycache__/jira.cpython-312.pyc']` present in the published archive under the real CI test/validate/package order with `PYTHONDONTWRITEBYTECODE` unset. |
| AUD-JIRA-001 | documentation | reportable | confirmed | Worth considering | — | Direct execution (`$EVIDENCE_DIR/proofs/AUD-JIRA-001/dry_run_assign_email_output.json`) shows a dry-run `assign --email` with an ambiguous email returns a clean placeholder preview with no `/user/search` call and no ambiguity error; live path independently confirmed to enforce exact-or-unambiguous resolution via `tests/test_jira_cli.py::HelperBehaviorTests::test_account_resolution_is_exact_or_unambiguous`. |
| AUD-REL-001 | security | reportable | confirmed | Worth considering | Fresh finalized Codex Security 0.1.11 bundle has zero canonical findings; its sole candidate is `PKG-SYMLINK-ROOT-001`, so no plugin finding corresponds to this independently validated release-lane finding. | Direct `grep -n 'uses: actions/' .github/workflows/ci.yml .github/workflows/release.yml` confirms both workflows reference `actions/checkout@v4` and `actions/setup-python@v5` by floating major-version tag, with no SHA pin in either file. |
| AUD-SEC-001 (`PKG-SYMLINK-ROOT-001`) | security | suppressed | confirmed | — | `PKG-SYMLINK-ROOT-001` (plugin taxonomy: `ignore`, low, high confidence); see the finalized bundle validation and attack-path reports. | Pinned `build_packages()` reproduction places `abd-linked/private.txt` in a `.skill` archive, but the attack path requires a privileged source-tree writer and maintainer-controlled release path, with no lower-privileged trigger evidenced. |
<!-- candidate-ledger:end -->

`AUD-SEC-001` retains the discovered alias `PKG-SYMLINK-ROOT-001`; no aliases were discovered or merged for the other three candidates.

## Findings

### Blocking

No findings.

### Should fix

No findings.

### Worth considering

#### AUD-CORE-001 — Packaging includes stale Python `__pycache__` bytecode in published `.skill` archive

- **Severity / confidence:** Worth considering; confidence confirmed — reproduced by direct execution against the pinned revision, not inferred from code reading alone.
- **Pinned locations:** `scripts/package_skills.py:33-39` (revision `8605a17c906d715c58b9c1a2511b8d0079446a4a`).
- **Behavior and impact:** `scripts/package_skills.py`'s file-collection step (`source_files`, L33-39) recursively collects every regular file under each skill directory without consulting `.gitignore`, so an existing `skills/abd-jira-cloud/scripts/__pycache__/jira.cpython-312.pyc` bytecode cache is packaged into the `abd-jira-cloud-v0.0.0.skill` archive whenever it happens to be present on disk at packaging time. This makes the published archive's contents non-deterministic and interpreter-version-dependent (the `.pyc` filename embeds `cpython-312`), and ships unnecessary compiled bytes in a package that is otherwise pure source and markdown — a compiled-artifact provenance concern for a public release archive.
- **Validation:** `env -u PYTHONDONTWRITEBYTECODE python3 -m unittest discover -s tests -v && env -u PYTHONDONTWRITEBYTECODE python3 scripts/validate_skills.py && env -u PYTHONDONTWRITEBYTECODE python3 scripts/package_skills.py --version v0.0.0 --output "$PROOF_ROOT/dist"` — exit 0; `generated_members=['abd-jira-cloud/scripts/__pycache__/jira.cpython-312.pyc']` (`$EVIDENCE_DIR/proofs/generated-skill-content/workflow-order.log`). No counterevidence was found or recorded against this candidate.
- **Remediation:** Exclude `__pycache__/` directories and `*.pyc`/`*.pyo` files when `scripts/package_skills.py` collects skill directory contents, rather than relying on `PYTHONDONTWRITEBYTECODE=1` at CI time to mask the root cause.
- **Verification criteria:** Re-run the Step-4 workflow-order proof (fresh clone, `env -u PYTHONDONTWRITEBYTECODE`, real test/validate/package order) and assert `generated_members == []` for every packaged skill; `tests/test_package_skills.py`'s existing 54-test suite must continue to pass.

#### AUD-JIRA-001 — Dry-run cannot detect ambiguous/zero-match email identity resolution for assign/watch, contradicting SKILL.md's confirm-before-ambiguous-write rule

- **Severity / confidence:** Worth considering; confidence confirmed — reproduced by direct dry-run execution against the pinned revision.
- **Pinned locations:** `skills/abd-jira-cloud/scripts/jira.py:209-232` (`resolve_account_id`), `skills/abd-jira-cloud/scripts/jira.py:437-477` (`cmd_assign`, `cmd_watch`), `skills/abd-jira-cloud/SKILL.md:19-23` (revision `8605a17c906d715c58b9c1a2511b8d0079446a4a`).
- **Behavior and impact:** `resolve_account_id()` performs the `/user/search` lookup and raises `JiraError` on zero or multiple matches only on a live call; when `--dry-run` is set it short-circuits (L215-216) and returns the literal placeholder string `<accountId-resolved-from:EMAIL>` with no network call and no ambiguity check. Both `cmd_assign` and `cmd_watch` call `resolve_account_id` with `dry_run=args.dry_run` when `--email` is used, so a dry-run `assign`/`watch` by email always "succeeds" and emits a normal-looking preview body, even for an email that does not resolve or that matches multiple accounts. `SKILL.md`'s Operating rule instructs the agent to "dry-run and confirm ambiguous, inferred, broad, or multi-issue writes" — but for `--email`-based assign/watch, the exact ambiguity this rule targets (identity resolution) is precisely what the dry-run path cannot check. An agent following this documented safety guidance sees a clean, plausible preview and may report the write as confirmed-safe, only to have the live run fail with "matched N users" or silently resolve to the wrong account if the caller doesn't re-check. This is a false-confidence/documentation-behavior mismatch, not a credential leak or an incorrect live mutation.
- **Validation:** `JIRA_BASE_URL=https://example.atlassian.net JIRA_EMAIL=user@example.com JIRA_API_TOKEN=dummy-token python3 scripts/jira.py --dry-run assign ABC-1 --email ambiguous@example.com` — exit 0; output is a full PUT preview with body `{"accountId": "<accountId-resolved-from:ambiguous@example.com>"}`, no `/user/search` call, no ambiguity error (`$EVIDENCE_DIR/proofs/AUD-JIRA-001/dry_run_assign_email_output.json`). **Counterevidence:** `SKILL.md:69` ("Dry-run a write when its scope or payload needs confirmation") is satisfied for `--account-id` writes (no resolution step needed) and most other mutation shapes — the gap is narrow, limited to `--email`-based assign/watch identity resolution; and the live (non-dry-run) path does correctly raise `JiraError` on 0 or >1 matches, verified by `tests/test_jira_cli.py::HelperBehaviorTests::test_account_resolution_is_exact_or_unambiguous` — no incorrect mutation is ever silently applied, the gap is confined to preview fidelity.
- **Remediation:** In `cmd_assign`/`cmd_watch`, when `--dry-run` and `--email` are combined, either (a) still perform the read-only `/user/search` lookup (safe under dry-run since it's a GET, not a mutation) so ambiguity is genuinely checked, or (b) print an explicit caveat in the dry-run JSON (e.g. an `identity_resolution: "not verified in dry-run"` field) so the preview cannot be mistaken for a validated confirmation.
- **Verification criteria:** Re-run `JIRA_BASE_URL=https://example.atlassian.net JIRA_EMAIL=user@example.com JIRA_API_TOKEN=dummy-token python3 skills/abd-jira-cloud/scripts/jira.py --dry-run assign ABC-1 --email ambiguous@example.com` and confirm either a surfaced ambiguity error or an explicit `identity_resolution` caveat field is present; existing `tests/test_jira_cli.py` suite must continue to pass.

#### AUD-REL-001 — CI and release workflows pin third-party GitHub Actions to floating major-version tags instead of commit SHAs

- **Severity / confidence:** Worth considering; confidence confirmed — reproduced by direct grep of both workflow files.
- **Pinned locations:** `.github/workflows/ci.yml:16-21`, `.github/workflows/release.yml:16-21` (revision `8605a17c906d715c58b9c1a2511b8d0079446a4a`).
- **Entry point:** GitHub Actions workflow trigger — push to a `vMAJOR.MINOR.PATCH` tag for `release.yml`; push to `main` or any pull request for `ci.yml`.
- **Control:** `actions/checkout@v4` and `actions/setup-python@v5` are resolved by GitHub Actions at run time to whatever commit the `v4`/`v5` tag currently points to; no SHA pin or lockfile constrains this resolution in either workflow file.
- **Sink:** the release job's execution context, which carries `permissions: contents: write` and an ephemeral `github.token`, and which builds and publishes real GitHub Release artifacts (per-skill `.skill` archives, collection ZIP, `SHA256SUMS`) prior to checksum computation (`release.yml`); the CI job's execution context, `permissions: contents: read` only, carries an analogous but lower-blast-radius risk on every push/PR (`ci.yml`).
- **Behavior and impact:** Both workflows reference `actions/checkout@v4` and `actions/setup-python@v5` by mutable major-version tag rather than by pinned commit SHA. A tag like `@v4` can be moved by the action's maintainer — or, in a compromise scenario, by an attacker who gains control of the `actions/checkout` or `actions/setup-python` repository/tag — to point at a different commit without any change to this repository's workflow files. If an upstream action tag were repointed to a malicious commit, the next tag push would execute attacker-controlled code inside the release job with write access to repository contents and the ability to influence published release artifacts before checksums are computed.
- **Validation:** `grep -n 'uses: actions/' .github/workflows/ci.yml .github/workflows/release.yml` — exit 0; confirms both workflows use `@v4`/`@v5` floating tags with no SHA pins present in either file. The fresh finalized Codex Security bundle's discovery and reconciliation records contain only `PKG-SYMLINK-ROOT-001`; therefore it neither duplicates nor contradicts this independently validated release-lane finding.
- **Remediation:** Pin `actions/checkout` and `actions/setup-python` to a specific commit SHA (e.g. `actions/checkout@<sha> # v4.x.x`) and keep the pin current via Dependabot's `github-actions` ecosystem or a periodic manual bump, per GitHub's supply-chain hardening guidance for Actions.
- **Verification criteria:** Re-run `grep -n 'uses: actions/' .github/workflows/ci.yml .github/workflows/release.yml` and confirm every `uses: actions/...` line is a full commit SHA with a version comment; CI and release workflows must continue to pass after repinning.

### Nit

No findings.

## Security Scan Bundle

The finalized Codex Security 0.1.11 repository scan completed at `2026-07-11T03:35:00Z` with scan ID `8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z`. Its resolved absolute bundle path is `/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z`; the portable form is `$SYSTEM_TEMP/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/`. The scan covers all 40 tracked files at the pinned revision and records zero reportable canonical findings.

Canonical bundle artifacts are [`scan-manifest.json`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/scan-manifest.json), [`findings.json`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/findings.json), generated [`report.md`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/report.md), [`threat_model.md`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/threat_model.md), [`finding discovery report`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/02_discovery/finding_discovery_report.md), and [`coverage ledger`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/03_coverage/repository_coverage_ledger.md). The sole candidate, `PKG-SYMLINK-ROOT-001`, is retained as `AUD-SEC-001` in the main reconciliation and linked to its [`candidate ledger`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/05_findings/PKG-SYMLINK-ROOT-001/candidate_ledger.jsonl), [`validation report`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/05_findings/PKG-SYMLINK-ROOT-001/validation_report.md), and [`attack-path analysis`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/05_findings/PKG-SYMLINK-ROOT-001/attack_path_analysis_report.md). There are no applicable standalone security write-up or hardening artifacts because the final disposition is suppression.

**Security crosswalk:**

| Audit ID | Plugin candidate/finding IDs | Plugin taxonomy | Main taxonomy | Final disposition | Candidate ledger | Validation receipt | Attack-path receipt |
|---|---|---|---|---|---|---|---|
| AUD-SEC-001 | `PKG-SYMLINK-ROOT-001` / — | ignore; low; high confidence | suppressed; —; confirmed | suppressed | [ledger](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/05_findings/PKG-SYMLINK-ROOT-001/candidate_ledger.jsonl) | [validation](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/05_findings/PKG-SYMLINK-ROOT-001/validation_report.md) | [attack path](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/05_findings/PKG-SYMLINK-ROOT-001/attack_path_analysis_report.md) |

The bundle is stored in a system-temporary location; retention is environment-dependent. It must remain intact for this report and its artifact links to remain fully verifiable.

## Limitations and Deferred Work

- **Temporary scan-bundle retention:** The completed Codex Security bundle is in a system-temporary directory. Preserve the bundle or archive its contents before environment cleanup; otherwise its detailed receipts and this report's links cannot be re-verified.
- **Static analysis tooling unavailable:** actionlint, bandit, gitleaks, mypy, ruff, and semgrep were not installed in the audit environment (`$EVIDENCE_DIR/baseline/tools.tsv`); no finding in this report depended on them, but their absence means no automated secret-scanning, type-checking, or workflow-linting pass was run beyond manual code reading and targeted `grep`.
- **No live Jira Cloud access:** per the stricter no-live-Jira rule governing this audit, all Jira-related validation (including the `AUD-JIRA-001` proof) used `--dry-run` and a dummy API token against the offline test harness only; no live Jira Cloud instance was contacted, and no live-path behavior beyond what the existing offline test suite already exercises was independently re-verified.
- **Historical design documents reviewed as contextual only:** the five `docs/superpowers/` plan/spec files in the pinned tree were reviewed for contradiction against the revised governing plan, not evaluated as behavioral subjects; no findings were filed against them.

## Strengths Worth Preserving

- **Strong offline Jira test harness:** `tests/test_jira_cli.py` (447 lines, fully read) mocks every network-touching path via `HTTP_OPENER.open`, asserts a 30-second timeout, bounds and redacts error-body disclosure (`ERROR_BODY_LIMIT`), verifies pagination termination on both repeated-token and missing-token-with-not-`isLast` conditions, and confirms `SameOriginRedirectHandler` rejects cross-origin/downgrade/credential/malformed-port redirects — no unmocked network-capable code path was found in this file.
- **Same-origin redirect enforcement and token redaction:** `skills/abd-jira-cloud/scripts/jira.py`'s `validate_base_url` restricts `JIRA_BASE_URL` to HTTPS, default port 443, no embedded credentials, and a hostname that must end in the literal `.atlassian.net`; `SameOriginRedirectHandler` and `_redact`-based token redaction in dry-run and error output are covered by the offline test harness and the completed security scan's Jira credential/data review.
- **Least-privilege CI permissions:** `.github/workflows/ci.yml` runs with `permissions: contents: read` only and never triggers on `pull_request_target`; `.github/workflows/release.yml`'s elevated `contents: write` permission is scoped to an ephemeral `github.token` passed only via the `GH_TOKEN` environment variable to `gh release create`, never interpolated into a shell string, with the release tag validated by regex before use.
- **Deterministic packaging with checksums, atomic replace, and `--verify-tag`:** `scripts/package_skills.py` uses a validate-then-discover-then-stage-then-atomic-replace flow with backup/rollback on `os.replace` failure, fixed archive timestamps/modes/compression for reproducibility, SHA-256 checksums with self-verification, and a dry-run short circuit before any publish step — all independently exercised by 54 passing tests including `test_output_is_deterministic`, `test_replacement_failure_restores_existing_output_and_cleans_backup`, and `test_rejects_symlinked_source_outside_skill`.

## Hardening Goals

No standalone hardening goals. All 3 roadmap seeds in `$EVIDENCE_DIR/reconciliation/roadmap-seeds.jsonl` trace 1:1 to the three findings above (`AUD-CORE-001`, `AUD-REL-001`, `AUD-JIRA-001`); their remediation and verification criteria are folded into each finding's entry rather than repeated as separate hardening goals.

## Appendix A: Coverage Inventory

Every one of the 40 pinned tracked files at revision `8605a17c906d715c58b9c1a2511b8d0079446a4a` is listed below with its review receipt, plus one row per of the 9 audit-start ignored/generated paths. The security review's own coverage is recorded once, in full, in the finalized [`security coverage ledger`](/tmp/codex-security-scans/agent-skills/8605a17c906d715c58b9c1a2511b8d0079446a4a_20260711T031439Z/artifacts/03_coverage/repository_coverage_ledger.md) and is not duplicated as separate appendix rows here.

<!-- coverage-inventory:start -->
| Path | Scope | Role | Risk | Review receipt | Disposition | Candidate IDs |
|---|---|---|---|---|---|---|
| `scripts/package_skills.py` | pinned tracked | packaging | medium | `8605a17c906d715c58b9c1a2511b8d0079446a4a:scripts/package_skills.py:L1-L184` read in full; traced descendant-symlink rejection (L33-39), but the completed security bundle reproduced that a direct symlinked skill root can still enter `source.read_bytes()` and an archive; this is `AUD-SEC-001` / `PKG-SYMLINK-ROOT-001`, suppressed after attack-path analysis. Also traced fixed timestamp/mode/compression (L42-51), archive traversal check (L74-83), checksums (L86-91,129-139), atomic-replace flow (L94-159), and dry-run (L107-113,141-142). | reviewed | AUD-CORE-001 |
| `scripts/validate_skills.py` | pinned tracked | runtime | low | `8605a17c906d715c58b9c1a2511b8d0079446a4a:scripts/validate_skills.py:L1-L169` read in full; traced `discover_skills` hidden-dir exclusion (L21-27), `parse_frontmatter` line-oriented parsing (L30-57), `local_references` extraction with remote-URI skip (L60-69), `normalize_scalar` quote stripping (L72-76), `validate_skill` containment guard against absolute-path and `..` escapes (L127-135), `validate_collection` empty-dir contract (L143-152); manual proof that an absolute-path markdown link is rejected; cross-checked against `tests/test_validate_skills.py`'s 13 tests. | reviewed | — |
| `tests/test_jira_cli.py` | pinned tracked | test | low | `8605a17c906d715c58b9c1a2511b8d0079446a4a:tests/test_jira_cli.py:L1-L447` read in full as offline trust-boundary harness; verified token never appears in output, `HTTP_OPENER.open` mocked in every network-touching test, 30s timeout asserted, error-body bound/truncation, pagination termination, `SameOriginRedirectHandler` behavior, parser rejection of conflicting identity flags; no unmocked network path found. | reviewed | — |
| `tests/test_package_skills.py` | pinned tracked | test | low | Full read; source of the 54 baseline tests validating packaging determinism, atomic replace/rollback, symlink rejection, and dry-run short circuit; re-run at baseline with exit 0 (`$EVIDENCE_DIR/baseline/unit-tests.log`). | reviewed | — |
| `tests/test_repository_layout.py` | pinned tracked | test | low | Full read; validates repository-level structural invariants; part of the 54-test baseline suite (exit 0). | reviewed | — |
| `tests/test_validate_skills.py` | pinned tracked | test | low | Full read; 13 tests covering valid skill, missing files, frontmatter errors, discovery sort/hidden exclusion, main() stdout/stderr contract, reference escaping, remote URI forms; part of the 54-test baseline suite. | reviewed | — |
| `tests/test_workflows.py` | pinned tracked | test | low | Full read; exercises `.github/workflows/ci.yml` and `release.yml` structural/behavioral expectations used to corroborate `AUD-REL-001`'s workflow-order proof; part of the 54-test baseline suite. | reviewed | — |
| `skills/abd-jira-cloud/README.md` | pinned tracked | documentation | low | Full read; cross-checked against `SKILL.md`'s ambiguous-write guidance for the `AUD-JIRA-001` documentation/behavior mismatch. | reviewed | AUD-JIRA-001 |
| `skills/abd-jira-cloud/SKILL.md` | pinned tracked | documentation | low | `8605a17c906d715c58b9c1a2511b8d0079446a4a:skills/abd-jira-cloud/SKILL.md:L19-23,L69` read in full; Operating rule on dry-running ambiguous writes identified as the documented guarantee contradicted by `AUD-JIRA-001`. | reviewed | AUD-JIRA-001 |
| `skills/abd-jira-cloud/references/api-notes.md` | pinned tracked | documentation | low | Full read; corroborating API reference for the Jira CLI, no independent findings. | reviewed | — |
| `skills/abd-jira-cloud/scripts/jira.py` | pinned tracked | runtime | medium | `8605a17c906d715c58b9c1a2511b8d0079446a4a:skills/abd-jira-cloud/scripts/jira.py` read in full; `resolve_account_id` (L209-232), `cmd_assign`/`cmd_watch` (L437-477), `validate_base_url`, `SameOriginRedirectHandler`, `_redact`, `ERROR_BODY_LIMIT`, and pagination guards traced; direct dry-run execution proof for `AUD-JIRA-001` (`$EVIDENCE_DIR/proofs/AUD-JIRA-001/dry_run_assign_email_output.json`). | reviewed | AUD-JIRA-001 |
| `skills/abd-code-review/README.md` | pinned tracked | documentation | low | Full read; describes the code-review skill's invocation and scope; no findings. | reviewed | — |
| `skills/abd-code-review/SKILL.md` | pinned tracked | documentation | low | Full read; confirmed diff/PR/commit content is treated strictly as data, never executed as instructions; no prompt-injection/confused-deputy issue found. | reviewed | — |
| `skills/abd-code-review/references/database.md` | pinned tracked | documentation | low | Full read; language/stack-specific review guidance, no executable code, no findings. | reviewed | — |
| `skills/abd-code-review/references/dependencies.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/dotnet.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/go.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/infra-cicd.md` | pinned tracked | documentation | low | Full read plus targeted grep for injection/secrets-hygiene guidance; no findings. | reviewed | — |
| `skills/abd-code-review/references/java-spring.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/kotlin-android.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/node-ts.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/php-laravel.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/python.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/react-next.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/rust.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/shell-config.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `skills/abd-code-review/references/vue-nuxt.md` | pinned tracked | documentation | low | Full read; review guidance content only, no findings. | reviewed | — |
| `.gitattributes` | pinned tracked | policy | low | Full read; line-ending/attribute policy, no findings. | reviewed | — |
| `.gitignore` | pinned tracked | policy | low | Full read; ignores `.superpowers/`, `dist/`, `__pycache__/`, `*.py[cod]`, `.venv/`, `.DS_Store`, `tmp/`, `logs/`, `*.log`; cross-checked against `AUD-CORE-001` — the root cause of that finding is the packager not consulting this policy, not a defect in the policy file itself. | reviewed | — |
| `CHANGELOG.md` | pinned tracked | documentation | low | Full read; release history, no findings. | reviewed | — |
| `CONTRIBUTING.md` | pinned tracked | documentation | low | Full read; matches `.gitignore`'s claim that generated `dist/` files are local artifacts and must not be committed. | reviewed | — |
| `LICENSE` | pinned tracked | policy | low | Full read; standard license text, no findings. | reviewed | — |
| `README.md` | pinned tracked | documentation | low | Full read; top-level repository documentation, no findings. | reviewed | — |
| `.github/workflows/ci.yml` | pinned tracked | ci | medium | `8605a17c906d715c58b9c1a2511b8d0079446a4a:.github/workflows/ci.yml:L16-21` read in full; `permissions: contents: read`, no `pull_request_target` trigger, no secrets interpolated into `run:` strings; floating `actions/checkout@v4`/`actions/setup-python@v5` tags identified as `AUD-REL-001`. | reviewed | AUD-REL-001 |
| `.github/workflows/release.yml` | pinned tracked | ci | medium | `8605a17c906d715c58b9c1a2511b8d0079446a4a:.github/workflows/release.yml:L16-21` read in full; `permissions: contents: write` scoped to ephemeral `github.token` via `GH_TOKEN` env var only, release tag regex-validated; floating action tags identified as `AUD-REL-001`. | reviewed | AUD-REL-001 |
| `docs/superpowers/plans/2026-07-07-agent-skills-repository.md` | pinned tracked | historical plan | low | Full read; cross-checked against the revised governing plan for contradictions — none found affecting scope or findings. | contextual | — |
| `docs/superpowers/plans/2026-07-08-abd-jira-cloud-refinement.md` | pinned tracked | historical plan | low | Full read; cross-checked against the revised governing plan for contradictions — none found affecting scope or findings. | contextual | — |
| `docs/superpowers/specs/2026-07-07-agent-skills-repository-design.md` | pinned tracked | historical spec | low | Full read; cross-checked against the revised governing plan for contradictions — none found affecting scope or findings. | contextual | — |
| `docs/superpowers/specs/2026-07-08-abd-jira-cloud-refinement-design.md` | pinned tracked | historical spec | low | Full read; cross-checked against the revised governing plan for contradictions — none found affecting scope or findings. | contextual | — |
| `docs/superpowers/specs/2026-07-10-codebase-audit-design.md` | pinned tracked | historical spec | low | Full read (pinned copy, pre-drift); cross-checked against the revised governing plan `docs/superpowers/plans/2026-07-11-codebase-audit.md` for contradictions — none found; see "Drift from the Pinned Tree" for the live-repository relationship between these two documents. | contextual | — |
| `.superpowers/sdd/progress.md` | ignored/generated | audit process log | low | Not part of the audited application; is the in-progress audit's own execution ledger, gitignored by design. | not applicable | — |
| `scripts/__pycache__/package_skills.cpython-312.pyc` | ignored/generated | compiled bytecode cache | low | Gitignored interpreter-generated artifact; not tracked at the pin, not shipped in any release archive (only the `abd-jira-cloud` skill's own `__pycache__` is shipped — see `AUD-CORE-001`). | not applicable | — |
| `scripts/__pycache__/validate_skills.cpython-312.pyc` | ignored/generated | compiled bytecode cache | low | Gitignored interpreter-generated artifact; not tracked at the pin, not shipped in any release archive. | not applicable | — |
| `skills/abd-jira-cloud/scripts/__pycache__/jira.cpython-312.pyc` | ignored/generated | compiled bytecode cache | medium | Gitignored interpreter-generated artifact that IS reproducibly included in the published `.skill` archive by the packaging defect; this is the exact artifact traced in `AUD-CORE-001`'s validation evidence. | included | AUD-CORE-001 |
| `tests/__pycache__/test_jira_cli.cpython-312.pyc` | ignored/generated | compiled bytecode cache | low | Gitignored interpreter-generated artifact; test-directory cache, never packaged into any skill archive (packaging only walks `skills/` subdirectories). | not applicable | — |
| `tests/__pycache__/test_package_skills.cpython-312.pyc` | ignored/generated | compiled bytecode cache | low | Gitignored interpreter-generated artifact; test-directory cache, never packaged into any skill archive. | not applicable | — |
| `tests/__pycache__/test_repository_layout.cpython-312.pyc` | ignored/generated | compiled bytecode cache | low | Gitignored interpreter-generated artifact; test-directory cache, never packaged into any skill archive. | not applicable | — |
| `tests/__pycache__/test_validate_skills.cpython-312.pyc` | ignored/generated | compiled bytecode cache | low | Gitignored interpreter-generated artifact; test-directory cache, never packaged into any skill archive. | not applicable | — |
| `tests/__pycache__/test_workflows.cpython-312.pyc` | ignored/generated | compiled bytecode cache | low | Gitignored interpreter-generated artifact; test-directory cache, never packaged into any skill archive. | not applicable | — |
<!-- coverage-inventory:end -->
