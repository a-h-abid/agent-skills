# Full Codebase Audit and Remediation Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a complete, evidence-backed audit of the immutable 40-file tree at `8605a17c906d715c58b9c1a2511b8d0079446a4a`, a finalized Codex Security scan bundle, and a prioritized remediation roadmap without changing product code or external systems.

**Architecture:** Keep the live repository as the writable control/output tree and create a disposable local clone whose `main` branch points at the pinned commit for all source inspection, baseline commands, proofs, and security scanning. Independent review lanes write machine-readable coverage receipts and candidates under the system temporary directory; the primary reviewer alone reconciles those records into the main audit report and roadmap.

**Tech Stack:** Git, Bash, Python 3.8+ standard library and `unittest`, Markdown, GitHub Actions YAML, and Codex Security plugin `0.1.11`.

## Global Constraints

- Audit exactly `8605a17c906d715c58b9c1a2511b8d0079446a4a`, whose canonical tree contains exactly 40 tracked files and two published skills.
- Generate the canonical inventory with `git ls-tree -r --name-only 8605a17c906d715c58b9c1a2511b8d0079446a4a`; resolve every source quotation and line number against that immutable revision.
- Record later commits and working-tree changes as drift. Do not silently absorb them into audit scope.
- Treat the current revised audit design as the controlling administrative input. Give the older pinned copy of that design its own contextual coverage receipt.
- Enumerate audit-start ignored/generated content with both `git status --ignored --porcelain` and `git ls-files --others --ignored --exclude-standard`. Give every expanded entry an `included` or `not applicable` receipt and take a second snapshot after verification.
- Historical specifications and implementation plans receive contextual contract-drift review, not line-by-line production review.
- Do not change product code or tests. Repository writes are limited to `docs/audits/2026-07-10-codebase-audit.md` and `docs/audits/2026-07-10-remediation-roadmap.md`; all work ledgers, logs, and proofs live under the system temporary directory.
- Do not make any live Jira call. Do not write to any external system or publish a package, tag, release, branch, or pull request.
- Do not install dependencies merely to expand tool coverage. Inventory locally available tools and run only safe, offline checks that are already installed.
- Never expose credentials or private Jira content in logs, proofs, reports, or scan artifacts. Run Jira tests with `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` unset.
- Re-run `python3 -m unittest discover -s tests -v`, `python3 scripts/validate_skills.py`, and `python3 scripts/package_skills.py --version v0.0.0 --dry-run` in the pinned clone with `PYTHONDONTWRITEBYTECODE=1`.
- A failed check does not silently narrow scope: record the command, exit status, failure, affected coverage, and safe alternatives attempted.
- No tool output becomes a finding until contextual validation establishes behavior, a violated contract, or a concrete security, reliability, compatibility, or maintenance cost.
- Passing tests are evidence only for exercised behavior, not proof that adjacent behavior is safe.
- Review executable code, tests, and public contracts for boundary conditions, unsafe filesystem behavior, resource exhaustion, error handling, compatibility, test quality, documentation drift, and unnecessary coupling.
- Treat instruction-only skills as executable behavior and review trigger conditions, tool advice, safety gates, output contracts, reference routing, clarity, and consistency.
- Inspect repository history when intent affects a candidate and cite the relevant commit or blame evidence.
- Do not report stylistic preference without a concrete maintenance cost.
- Use Codex Security plugin `0.1.11` and its `codex-security:security-scan` repository workflow. Preserve its threat-model, discovery, validation, attack-path, and finalization phases in order.
- The security threat model must prioritize agent prompt injection and confused-deputy behavior, Jira credential confinement and local-data egress, packaging path and symlink handling, CI/release token exposure and artifact provenance, and resource/output privacy.
- A security candidate is reportable only with a plausible evidenced attack path. Every candidate reaching validation or attack-path analysis keeps the receipts required by the plugin contract, even if later suppressed or deferred.
- Codex Security canonical JSON uses its native severity, confidence, and coverage vocabularies. The main report independently calibrates `Blocking`, `Should fix`, `Worth considering`, or `Nit` and `confirmed`, `likely`, or `unverified` with an explicit rationale; never use a mechanical mapping.
- Candidate closure is exactly one of `reportable`, `suppressed`, `not applicable`, or `deferred`. Every non-reportable closure names exact counterevidence or missing proof.
- An `unverified` candidate cannot be `Blocking`. Present it only as a bounded investigation item or defer it with the missing proof named.
- Keep independently reachable security instances separate through final reporting. Root-cause grouping is summary prose and must retain every instance ID and affected location.
- Roadmap priority is independent of finding severity: `P0` immediate containment/release blocking, `P1` next focused material-risk change, `P2` planned hardening/compatibility/maintainability, and `P3` optional hygiene/future-scale work.
- Roadmap effort uses `S` for at most one focused engineering day, `M` for two to five focused days, and `L` for more than five days or coordinated multi-component work.
- If a Blocking/P0 issue appears, report it to the user as release-blocking without changing code or notifying third parties; continue only safe evidence collection.
- Verify temporally current external contracts only when a conclusion depends on them, using authoritative primary sources and recording the URL plus access date.
- Preserve all unrelated user files and working-tree changes.
- Do not run `git fetch`, `git pull`, or `git push`. Ask before any `git merge`, `git squash`, or `git rebase`; this plan requires none of them.
- Every commit must include `Co-Authored-By: GPT-5 Codex <noreply@openai.com>` as a trailer.
- When using `superpowers:subagent-driven-development`, dispatch every implementer and per-task reviewer with `model: sonnet`; `model: haiku` is allowed only for trivial mechanical checks. Dispatch the final whole-branch reviewer with `model: inherit` and never `model: opus`.
- Before claiming completion, invoke and follow `superpowers:verification-before-completion`.

## File and Responsibility Map

### Repository outputs

- Create `docs/audits/2026-07-10-codebase-audit.md`: canonical audit metadata, baseline results, candidate closure ledger, reader-oriented findings, security-bundle reference, limitations, strengths, and the 40-file `Coverage Inventory` appendix.
- Create `docs/audits/2026-07-10-remediation-roadmap.md`: dependency-ordered P0-P3 remediation items with effort, affected files, acceptance criteria, and executable verification commands.

### Administrative artifacts outside the repository

- Create `$SYSTEM_TEMP/agent-skills-audit-8605a17c906d715c58b9c1a2511b8d0079446a4a/audit-context.env`: safely quoted paths, start revision, timestamps, and immutable target identity shared by fresh task workers.
- Create `$AUDIT_ROOT/evidence/`: start/end drift snapshots, ignored/generated inventories, baseline logs, tool inventory, review-lane JSONL, proof artifacts, and reconciliation output.
- Create `$AUDIT_ROOT/agent-skills/`: disposable local clone with local branch `main` pointing at the pinned commit. This avoids the false failure that a detached checkout would cause in `tests/test_repository_layout.py:63-73`.
- Generate `$SYSTEM_TEMP/codex-security-scans/agent-skills/$SCAN_ID/` through Codex Security finalization; do not author its `report.md` manually.

### Disjoint pinned-tree review ownership

- Core runtime/test lane, 7 files: `scripts/package_skills.py`, `scripts/validate_skills.py`, and all five files under `tests/`.
- Jira lane, 4 files: `skills/abd-jira-cloud/README.md`, `SKILL.md`, `references/api-notes.md`, and `scripts/jira.py`.
- Instruction lane, 16 files: `skills/abd-code-review/README.md`, `SKILL.md`, and all 14 files under `references/`.
- Release/contract lane, 13 files: `.gitattributes`, `.gitignore`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `README.md`, both GitHub workflows, and the five historical plan/spec documents.
- Security lane: the Codex Security workflow scans all 40 pinned files and produces surface-level coverage separate from the main report's file inventory.

## Shared Interfaces

### Persisted audit context

Every task after Task 1 begins with:

~~~bash
set -euo pipefail
AUDIT_TARGET="8605a17c906d715c58b9c1a2511b8d0079446a4a"
SYSTEM_TEMP="$(python3 -c 'import tempfile; print(tempfile.gettempdir())')"
AUDIT_ROOT="$SYSTEM_TEMP/agent-skills-audit-$AUDIT_TARGET"
source "$AUDIT_ROOT/audit-context.env"
test "$AUDIT_TARGET" = "8605a17c906d715c58b9c1a2511b8d0079446a4a"
test "$(git -C "$AUDIT_CHECKOUT" rev-parse HEAD)" = "$AUDIT_TARGET"
test "$(git -C "$AUDIT_CHECKOUT" branch --show-current)" = "main"
~~~

The context exports `SOURCE_REPO`, `AUDIT_TARGET`, `AUDIT_ROOT`, `AUDIT_CHECKOUT`, `EVIDENCE_DIR`, `HEAD_AT_START`, and `STARTED_AT`. It contains no credentials.

### Evidence notation

- Source evidence uses `8605a17c906d715c58b9c1a2511b8d0079446a4a:path/to/file:Lstart-Lend`.
- Command receipts record the exact command, integer exit status, log path below `$EVIDENCE_DIR`, concise result, and affected coverage when the command fails.
- Authoritative external-contract receipts record the primary-source URL, UTC access date, contract checked, and conclusion.

### Coverage JSONL

Each review lane produces one JSON object per owned pinned file. Task 2 also produces one object per expanded ignored/generated path:

~~~json
{
  "path": "scripts/package_skills.py",
  "scope": "pinned tracked",
  "role": "packaging",
  "risk": "high",
  "receipt": "8605a17c906d715c58b9c1a2511b8d0079446a4a:scripts/package_skills.py:L1-L184; full-file review plus recorded baseline/proof evidence",
  "disposition": "reviewed",
  "candidate_ids": ["AUD-CORE-001"]
}
~~~

Allowed `scope` values are `pinned tracked` and `ignored/generated`. Pinned dispositions are `reviewed`, `contextual`, or `not applicable`; ignored/generated dispositions are `included` or `not applicable`. Allowed roles are `runtime`, `packaging`, `instruction`, `reference`, `test`, `workflow`, `metadata`, `policy`, `public documentation`, and `historical context`. Allowed risks are `high`, `medium`, `low`, and `contextual`.

### Candidate JSONL

Each discovered candidate is written once and retains its ID through reconciliation:

~~~json
{
  "id": "AUD-CORE-001",
  "lane": "core",
  "category": "correctness",
  "title": "Concrete behavior under review",
  "locations": [
    {
      "revision": "8605a17c906d715c58b9c1a2511b8d0079446a4a",
      "path": "scripts/package_skills.py",
      "start_line": 33,
      "end_line": 39
    }
  ],
  "behavior": "Observed behavior stated without speculation",
  "impact": "Concrete user, release, security, reliability, or maintenance cost",
  "entry_point": null,
  "control": null,
  "sink": null,
  "validation": [
    {
      "command": "exact non-destructive command",
      "exit_code": 0,
      "evidence_path": "absolute path below the audit evidence directory",
      "result": "Observed result"
    }
  ],
  "counterevidence": [],
  "confidence": "confirmed",
  "disposition": "reportable",
  "closure_reason": "Why the evidence supports this final disposition",
  "severity": "Should fix",
  "remediation": "Specific change strategy without changing code during the audit",
  "verification_commands": ["exact command to prove the future remediation"],
  "security_refs": [],
  "aliases": [],
  "summary_group": null,
  "root_cause_key": "stable normalized root-cause phrase"
}
~~~

Lane ID prefixes are `AUD-CORE-`, `AUD-JIRA-`, `AUD-INSTR-`, `AUD-REL-`, and `AUD-SEC-` with three-digit counters. A lane owns its counter and never reuses an ID. Security crosswalk IDs are assigned by sorted canonical plugin finding/candidate ID. A reportable candidate requires a non-null main severity; other dispositions use `null` severity but still include a concrete closure reason and remediation decision.

Allowed `lane` values are `core`, `jira`, `instruction`, `release`, and `security`. Allowed `category` values are `correctness`, `maintainability`, `security`, `release`, `documentation`, and `instruction supply chain`. Task 2 reserves any generated-content `AUD-CORE-NNN` IDs first; Task 3 reads that ledger, starts after its highest counter, and never reassigns those IDs.

For a security-category candidate, `entry_point`, `control`, and `sink` are non-empty and `security_refs` names its plugin candidate ledger, validation report, and attack-path report. Reconciliation chooses one canonical ID for a duplicate root cause, moves the other stable IDs into `aliases`, and never merges independently reachable security instances.

### Main-report and security crosswalk

- Canonical security `reported` maps to candidate closure `reportable`.
- Canonical security `rejected` maps to `suppressed`.
- Canonical security `not_applicable` maps to `not applicable`.
- Canonical security `needs_follow_up` maps to `deferred`.
- Canonical security `no_issue_found` is a coverage result, not a candidate.
- Preserve plugin severity and confidence verbatim in the crosswalk. Add independently reasoned main severity and confidence beside them.
- The main report summarizes exact security evidence and links the detailed bundle artifacts; it does not duplicate full vulnerability write-ups or the security coverage ledger.

### Roadmap-seed JSONL

Task 8 writes one seed per future remediation item:

~~~json
{
  "traceability": ["AUD-CORE-001"],
  "title": "Concrete remediation outcome",
  "priority": "P1",
  "effort": "S",
  "dependencies": [],
  "affected_files": ["scripts/package_skills.py"],
  "why_now": "Risk and sequencing rationale",
  "acceptance_criteria": ["Observable behavior after remediation"],
  "verification_commands": ["exact focused command", "exact regression command"]
}
~~~

`traceability` contains reportable candidate IDs or explicitly defined `HARDENING-NNN` IDs. All strings are non-empty, every file is repository-relative, and dependencies are resolved to `RM-NNN` IDs when Task 10 assigns final roadmap order.

### Security-crosswalk JSONL

Task 8 writes one row per security candidate with these exact keys: `audit_id`, `plugin_candidate_id`, `finding_id`, `plugin_disposition`, `plugin_severity`, `plugin_confidence`, `main_disposition`, `main_severity`, `main_confidence`, `candidate_ledger`, `validation_report`, and `attack_path_report`. Optional plugin values use JSON `null`; artifact paths are absolute regular-file paths below `$SCAN_DIR`. Main values follow the candidate enums in this plan and include the calibration rationale in the corresponding candidate record.

---

### Task 1: Establish the Immutable Audit Workspace and Contracts

**Files:**
- Create: `$AUDIT_ROOT/audit-context.env`
- Create: `$EVIDENCE_DIR/start/source-status.txt`
- Create: `$EVIDENCE_DIR/start/ignored-status.txt`
- Create: `$EVIDENCE_DIR/start/ignored-files.txt`
- Create: `$EVIDENCE_DIR/start/committed-drift.txt`
- Create: `$EVIDENCE_DIR/inventory/pinned-tracked-files.txt`
- Create: `$EVIDENCE_DIR/inventory/pinned-tracked-files.sha256`
- Create: `$AUDIT_CHECKOUT/` as a disposable local clone
- Modify: none in the source repository

**Interfaces:**
- Consumes: current repository path and immutable target `8605a17c906d715c58b9c1a2511b8d0079446a4a`.
- Produces: the persisted audit context and exact 40-path inventory consumed by every later task.

- [x] **Step 1: Capture the live repository identity before audit writes**

Run from the live repository:

~~~bash
set -euo pipefail
AUDIT_TARGET="8605a17c906d715c58b9c1a2511b8d0079446a4a"
SOURCE_REPO="$(git rev-parse --show-toplevel)"
SYSTEM_TEMP="$(python3 -c 'import tempfile; print(tempfile.gettempdir())')"
AUDIT_ROOT="$SYSTEM_TEMP/agent-skills-audit-$AUDIT_TARGET"
AUDIT_CHECKOUT="$AUDIT_ROOT/agent-skills"
EVIDENCE_DIR="$AUDIT_ROOT/evidence"
mkdir -p "$AUDIT_ROOT" "$EVIDENCE_DIR/start" "$EVIDENCE_DIR/inventory" "$EVIDENCE_DIR/baseline" "$EVIDENCE_DIR/reviews" "$EVIDENCE_DIR/proofs" "$EVIDENCE_DIR/reconciliation"

if test -f "$AUDIT_ROOT/audit-context.env"; then
  source "$AUDIT_ROOT/audit-context.env"
  test "$SOURCE_REPO" = "$(git rev-parse --show-toplevel)"
else
  HEAD_AT_START="$(git -C "$SOURCE_REPO" rev-parse HEAD)"
  STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  {
    printf 'SOURCE_REPO=%q\n' "$SOURCE_REPO"
    printf 'AUDIT_TARGET=%q\n' "$AUDIT_TARGET"
    printf 'AUDIT_ROOT=%q\n' "$AUDIT_ROOT"
    printf 'AUDIT_CHECKOUT=%q\n' "$AUDIT_CHECKOUT"
    printf 'EVIDENCE_DIR=%q\n' "$EVIDENCE_DIR"
    printf 'HEAD_AT_START=%q\n' "$HEAD_AT_START"
    printf 'STARTED_AT=%q\n' "$STARTED_AT"
  } > "$AUDIT_ROOT/audit-context.env"
fi
~~~

Expected: the context file exists, names the full target SHA, and preserves the original source HEAD and UTC audit-start time across resumed tasks.

- [x] **Step 2: Snapshot drift and ignored/generated state**

Run:

~~~bash
git -C "$SOURCE_REPO" status --short --untracked-files=all > "$EVIDENCE_DIR/start/source-status.txt"
git -C "$SOURCE_REPO" status --ignored --porcelain > "$EVIDENCE_DIR/start/ignored-status.txt"
git -C "$SOURCE_REPO" ls-files --others --ignored --exclude-standard > "$EVIDENCE_DIR/start/ignored-files.txt"
git -C "$SOURCE_REPO" diff --name-status "$AUDIT_TARGET"..HEAD > "$EVIDENCE_DIR/start/committed-drift.txt"
git -C "$SOURCE_REPO" diff --stat "$AUDIT_TARGET"..HEAD > "$EVIDENCE_DIR/start/committed-drift-stat.txt"
~~~

Expected: the files record the source state without altering it. The current known drift is the post-pin revision of `docs/superpowers/specs/2026-07-10-codebase-audit-design.md`; execution must record whatever is actually present at audit start.

- [x] **Step 3: Create or validate the pinned local clone on branch main**

Run:

~~~bash
if test -d "$AUDIT_CHECKOUT/.git"; then
  test "$(git -C "$AUDIT_CHECKOUT" rev-parse HEAD)" = "$AUDIT_TARGET"
  test "$(git -C "$AUDIT_CHECKOUT" branch --show-current)" = "main"
  test -z "$(git -C "$AUDIT_CHECKOUT" status --porcelain)"
else
  test ! -e "$AUDIT_CHECKOUT"
  git clone --no-hardlinks --no-checkout "$SOURCE_REPO" "$AUDIT_CHECKOUT"
  git -C "$AUDIT_CHECKOUT" update-ref refs/heads/main "$AUDIT_TARGET"
  git -C "$AUDIT_CHECKOUT" checkout main
fi
~~~

Expected: `HEAD` equals the full target SHA, the local branch is `main`, and the disposable clone is clean. The source repository's branches and worktree are untouched.

- [x] **Step 4: Generate and verify the canonical inventory**

Run:

~~~bash
git -C "$AUDIT_CHECKOUT" ls-tree -r --name-only "$AUDIT_TARGET" > "$EVIDENCE_DIR/inventory/pinned-tracked-files.txt"
sha256sum "$EVIDENCE_DIR/inventory/pinned-tracked-files.txt" > "$EVIDENCE_DIR/inventory/pinned-tracked-files.sha256"
AUDIT_CHECKOUT="$AUDIT_CHECKOUT" python3 - <<'PY'
import os
import subprocess

target = "8605a17c906d715c58b9c1a2511b8d0079446a4a"
expected = """
.gitattributes
.github/workflows/ci.yml
.github/workflows/release.yml
.gitignore
CHANGELOG.md
CONTRIBUTING.md
LICENSE
README.md
docs/superpowers/plans/2026-07-07-agent-skills-repository.md
docs/superpowers/plans/2026-07-08-abd-jira-cloud-refinement.md
docs/superpowers/specs/2026-07-07-agent-skills-repository-design.md
docs/superpowers/specs/2026-07-08-abd-jira-cloud-refinement-design.md
docs/superpowers/specs/2026-07-10-codebase-audit-design.md
scripts/package_skills.py
scripts/validate_skills.py
skills/abd-code-review/README.md
skills/abd-code-review/SKILL.md
skills/abd-code-review/references/database.md
skills/abd-code-review/references/dependencies.md
skills/abd-code-review/references/dotnet.md
skills/abd-code-review/references/go.md
skills/abd-code-review/references/infra-cicd.md
skills/abd-code-review/references/java-spring.md
skills/abd-code-review/references/kotlin-android.md
skills/abd-code-review/references/node-ts.md
skills/abd-code-review/references/php-laravel.md
skills/abd-code-review/references/python.md
skills/abd-code-review/references/react-next.md
skills/abd-code-review/references/rust.md
skills/abd-code-review/references/shell-config.md
skills/abd-code-review/references/vue-nuxt.md
skills/abd-jira-cloud/README.md
skills/abd-jira-cloud/SKILL.md
skills/abd-jira-cloud/references/api-notes.md
skills/abd-jira-cloud/scripts/jira.py
tests/test_jira_cli.py
tests/test_package_skills.py
tests/test_repository_layout.py
tests/test_validate_skills.py
tests/test_workflows.py
""".strip().splitlines()
actual = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", target],
    cwd=os.environ["AUDIT_CHECKOUT"],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()
assert actual == expected, (set(expected) - set(actual), set(actual) - set(expected))
assert len(actual) == len(set(actual)) == 40
print("verified exact pinned inventory: 40 unique paths")
PY
~~~

Expected: `verified exact pinned inventory: 40 unique paths`.

- [x] **Step 5: Verify the task produced administrative evidence only**

Run:

~~~bash
test -z "$(git -C "$AUDIT_CHECKOUT" status --porcelain)"
test "$(git -C "$SOURCE_REPO" rev-parse HEAD)" = "$HEAD_AT_START"
git -C "$SOURCE_REPO" status --short --untracked-files=all
~~~

Expected: the pinned clone is clean, source HEAD has not moved, and source status is unchanged from `$EVIDENCE_DIR/start/source-status.txt`.

---

### Task 2: Run the Baseline and Classify Ignored/Generated Inputs

**Files:**
- Create: `$EVIDENCE_DIR/baseline/unit-tests.log` and `unit-tests.exit`
- Create: `$EVIDENCE_DIR/baseline/validate-skills.log` and `validate-skills.exit`
- Create: `$EVIDENCE_DIR/baseline/package-dry-run.log` and `package-dry-run.exit`
- Create: `$EVIDENCE_DIR/baseline/tools.tsv` and applicable tool logs
- Create: `$EVIDENCE_DIR/reviews/generated-coverage.jsonl`
- Create: `$EVIDENCE_DIR/reviews/generated-candidates.jsonl`
- Create: targeted proof artifacts below `$EVIDENCE_DIR/proofs/` when generated skill content is present
- Modify: none in the source repository

**Interfaces:**
- Consumes: Task 1 context, ignored-file snapshot, and pinned checkout.
- Produces: baseline receipts and one coverage row for every expanded ignored/generated entry; candidate IDs use the `AUD-CORE-` lane because packaging owns generated-content behavior.

- [x] **Step 1: Run all documented baseline commands and preserve failures**

Run:

~~~bash
set -euo pipefail
AUDIT_TARGET="8605a17c906d715c58b9c1a2511b8d0079446a4a"
SYSTEM_TEMP="$(python3 -c 'import tempfile; print(tempfile.gettempdir())')"
AUDIT_ROOT="$SYSTEM_TEMP/agent-skills-audit-$AUDIT_TARGET"
source "$AUDIT_ROOT/audit-context.env"

run_check() {
  name="$1"
  shift
  set +e
  (
    cd "$AUDIT_CHECKOUT"
    env -u JIRA_BASE_URL -u JIRA_EMAIL -u JIRA_API_TOKEN \
      PYTHONDONTWRITEBYTECODE=1 "$@"
  ) > "$EVIDENCE_DIR/baseline/$name.log" 2>&1
  status=$?
  set -e
  printf '%s\n' "$status" > "$EVIDENCE_DIR/baseline/$name.exit"
  sed -n '1,240p' "$EVIDENCE_DIR/baseline/$name.log"
}

run_check unit-tests python3 -m unittest discover -s tests -v
run_check validate-skills python3 scripts/validate_skills.py
run_check package-dry-run python3 scripts/package_skills.py --version v0.0.0 --dry-run
~~~

Documented expectation: 54 tests pass, two skills validate, and the packaging dry run passes. Record actual output even when it differs; a nonzero exit creates a validation candidate or explicit limitation rather than erasing coverage.

- [x] **Step 2: Inventory locally available static/workflow tools**

Run:

~~~bash
printf 'tool\tpath\n' > "$EVIDENCE_DIR/baseline/tools.tsv"
for tool in actionlint bandit gitleaks mypy ruff semgrep shellcheck; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%s\t%s\n' "$tool" "$(command -v "$tool")" >> "$EVIDENCE_DIR/baseline/tools.tsv"
  else
    printf '%s\t%s\n' "$tool" "not installed" >> "$EVIDENCE_DIR/baseline/tools.tsv"
  fi
done
sed -n '1,40p' "$EVIDENCE_DIR/baseline/tools.tsv"
~~~

Run an installed tool only when it can operate offline without adding configuration or dependencies. Record its exact invocation, exit status, and output under `$EVIDENCE_DIR/baseline/`; treat results as candidates requiring source validation.

- [x] **Step 3: Classify every audit-start ignored/generated file**

Read `$EVIDENCE_DIR/start/ignored-status.txt` and `ignored-files.txt`. Write one `generated-coverage.jsonl` row per expanded path using the shared coverage schema:

- `included` when the path can be read by validation, packaging, tests, or publication;
- `not applicable` only with a concrete reason showing it cannot affect those behaviors.

At plan-authoring time, the live tree contains Python bytecode under `scripts/__pycache__/`, `skills/abd-jira-cloud/scripts/__pycache__/`, and `tests/__pycache__/`. Re-enumeration at audit start controls. Any regular ignored file below `skills/` is mandatory `included` evidence because `scripts/package_skills.py:33-39` recursively collects regular files without consulting `.gitignore`.

Create empty `generated-coverage.jsonl` and `generated-candidates.jsonl` files even when the corresponding inventory or candidate set is empty, so later tasks can parse them without guessing whether work ran.

- [x] **Step 4: Run a non-destructive workflow-order package-composition proof**

Run the CI order in a fresh temporary clone without suppressing bytecode, then inspect the produced Jira skill archive:

~~~bash
PROOF_ROOT="$EVIDENCE_DIR/proofs/generated-skill-content"
test ! -e "$PROOF_ROOT"
mkdir -p "$PROOF_ROOT"
git clone --no-hardlinks "$AUDIT_CHECKOUT" "$PROOF_ROOT/source"
(
  cd "$PROOF_ROOT/source"
  env -u PYTHONDONTWRITEBYTECODE python3 -m unittest discover -s tests -v
  env -u PYTHONDONTWRITEBYTECODE python3 scripts/validate_skills.py
  env -u PYTHONDONTWRITEBYTECODE python3 scripts/package_skills.py \
    --version v0.0.0 \
    --output "$PROOF_ROOT/dist"
) > "$PROOF_ROOT/workflow-order.log" 2>&1

PROOF_ROOT="$PROOF_ROOT" python3 - <<'PY'
import os
from pathlib import Path
import zipfile

root = Path(os.environ["PROOF_ROOT"])
archive_path = root / "dist" / "abd-jira-cloud-v0.0.0.skill"
with zipfile.ZipFile(archive_path) as archive:
    generated = [
        name
        for name in archive.namelist()
        if "/__pycache__/" in name or name.endswith((".pyc", ".pyo"))
    ]
print(f"generated_members={generated}")
print(f"archive={archive_path}")
PY
~~~

Expected: the proof prints the exact generated archive members observed after the real test/validate/package order. Promote the behavior only after checking packaging intent, public release claims, and downstream impact. Do not create bytecode or artifacts in the source repository or pinned clone.

- [x] **Step 5: Validate baseline receipts and clone cleanliness**

Run:

~~~bash
for name in unit-tests validate-skills package-dry-run; do
  test -s "$EVIDENCE_DIR/baseline/$name.log"
  test "$(wc -l < "$EVIDENCE_DIR/baseline/$name.exit")" -eq 1
done
test "$(wc -l < "$EVIDENCE_DIR/reviews/generated-coverage.jsonl")" -eq "$(wc -l < "$EVIDENCE_DIR/start/ignored-files.txt")"
test -z "$(git -C "$AUDIT_CHECKOUT" status --porcelain)"
~~~

Expected: each baseline has a log and status, every expanded ignored/generated file has a receipt, and the pinned checkout remains clean.

---

### Task 3: Review Core Runtime, Packaging, Validation, and Tests

**Files:**
- Inspect: `scripts/package_skills.py:1-184`
- Inspect: `scripts/validate_skills.py:1-169`
- Inspect: `tests/test_jira_cli.py:1-447`
- Inspect: `tests/test_package_skills.py:1-186`
- Inspect: `tests/test_repository_layout.py:1-77`
- Inspect: `tests/test_validate_skills.py:1-158`
- Inspect: `tests/test_workflows.py:1-29`
- Create: `$EVIDENCE_DIR/reviews/core-coverage.jsonl`
- Create: `$EVIDENCE_DIR/reviews/core-candidates.jsonl`
- Modify: none in the source repository

**Interfaces:**
- Consumes: Task 1 inventory and Task 2 baseline/generated-content evidence.
- Produces: exactly seven coverage rows and zero or more `AUD-CORE-NNN` candidates, continuing after any IDs reserved by Task 2.

- [x] **Step 1: Review the packaging boundary end to end**

Read `scripts/package_skills.py` and `tests/test_package_skills.py` in full at the pinned revision. Trace discovery, symlink checks, file selection, archive naming, permissions, timestamp normalization, checksum generation, dry-run behavior, replacement/rollback, and exception handling. Cross-check every public deterministic/package-purity claim against an assertion; record exact source/test line pairs.

- [x] **Step 2: Review the validation boundary end to end**

Read `scripts/validate_skills.py` and `tests/test_validate_skills.py` in full. Check frontmatter parsing, folded/multiline scalar handling, reference extraction, path containment, symlink resolution, URI handling, unreadable/oversized inputs, discovery rules, and diagnostic contracts. Verify each accepted/rejected input class against tests or a safe proof.

- [x] **Step 3: Review repository-layout and workflow test strength**

Read `tests/test_repository_layout.py` and `tests/test_workflows.py` with their production consumers. Separate structural substring evidence from YAML semantics, action provenance, permissions, release behavior, and clean-checkout assumptions. Record gaps only when they leave a concrete contract or release risk unverified.

- [x] **Step 4: Review Jira tests as an offline trust-boundary harness**

Read `tests/test_jira_cli.py` without re-reviewing Jira production behavior reserved for Task 4. Check sentinel credential handling, redirect and timeout mocks, bounded error bodies, pagination termination, command contracts, parser rejection, dry-run output, and whether tests can make network calls. Record test-quality candidates in this lane and behavior candidates in Task 4.

- [x] **Step 5: Validate each core candidate safely**

For each candidate, either cite an existing test and exact production line, create a minimal proof below `$EVIDENCE_DIR/proofs/AUD-CORE-NNN/` using an exported copy of the pinned tree, or close it as `suppressed`, `not applicable`, or `deferred` with exact counterevidence or missing proof. Never add a regression test or modify production code. Use `PYTHONDONTWRITEBYTECODE=1` and record each exact proof command in candidate JSON.

- [x] **Step 6: Write and validate the lane records**

Write seven coverage JSON objects and all candidates using the shared schemas. Then run:

~~~bash
EVIDENCE_DIR="$EVIDENCE_DIR" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["EVIDENCE_DIR"]) / "reviews"
coverage = [json.loads(line) for line in (root / "core-coverage.jsonl").read_text().splitlines()]
candidates = [json.loads(line) for line in (root / "core-candidates.jsonl").read_text().splitlines() if line.strip()]
expected = {
    "scripts/package_skills.py",
    "scripts/validate_skills.py",
    "tests/test_jira_cli.py",
    "tests/test_package_skills.py",
    "tests/test_repository_layout.py",
    "tests/test_validate_skills.py",
    "tests/test_workflows.py",
}
assert {row["path"] for row in coverage} == expected
assert len(coverage) == 7
assert all(row["scope"] == "pinned tracked" for row in coverage)
assert all(candidate["id"].startswith("AUD-CORE-") for candidate in candidates)
print(f"verified core lane: {len(coverage)} files, {len(candidates)} candidates")
PY
~~~

Expected: exactly seven unique files and parseable, lane-owned candidates.

---

### Task 4: Review the Jira Credential, Data-Egress, and Mutation Boundary

**Files:**
- Inspect: `skills/abd-jira-cloud/README.md:1-64`
- Inspect: `skills/abd-jira-cloud/SKILL.md:1-84`
- Inspect: `skills/abd-jira-cloud/references/api-notes.md:1-176`
- Inspect: `skills/abd-jira-cloud/scripts/jira.py:1-643`
- Create: `$EVIDENCE_DIR/reviews/jira-coverage.jsonl`
- Create: `$EVIDENCE_DIR/reviews/jira-candidates.jsonl`
- Modify: none in the source repository

**Interfaces:**
- Consumes: Task 2 baseline and Task 3 test-strength evidence.
- Produces: exactly four coverage rows and zero or more `AUD-JIRA-NNN` candidates.

- [x] **Step 1: Review configuration and destination confinement**

Trace `JIRA_BASE_URL` validation, hostname and port normalization, path-segment encoding, Basic-auth construction, redirect policy, request timeouts, token redaction, bounded HTTP diagnostics, JSON parsing, and error normalization from input to transport sink. Confirm every security statement against exact code and offline tests.

- [x] **Step 2: Review read and pagination behavior**

Trace `whoami`, `get`, `search`, `users`, and `watchers` through parser, request payload, pagination token handling, output emission, limits, and private-data exposure. Check empty/malformed response handling, repeated tokens, explicit `--all` behavior, result bounds, and request-field minimization.

- [x] **Step 3: Review every mutation and dry-run path**

Trace `create`, `comment`, `update`, `transition`, `assign`, and `watch`. Check single versus multi-step writes, ambiguous identity/transition resolution, ADF/file/stdin ingestion, payload precedence, write retry behavior, dry-run destination validation, secret redaction, and whether a preview can disclose issue content.

- [x] **Step 4: Reconcile all four public contracts**

Build a matrix across frontmatter, `SKILL.md`, README, API notes, parser help, and implementation for supported commands, Python floor, dependency policy, auth mode, URL constraint, pagination bound, timeout, retry policy, sensitive-output handling, unsupported Jira variants, and mutation confirmation rules. A contradiction is a candidate only when it can mislead an agent or user concretely.

- [x] **Step 5: Validate without credentials or network**

Run:

~~~bash
set +e
(
  cd "$AUDIT_CHECKOUT"
  env -u JIRA_BASE_URL -u JIRA_EMAIL -u JIRA_API_TOKEN \
    PYTHONDONTWRITEBYTECODE=1 \
    python3 -m unittest tests.test_jira_cli -v
) > "$EVIDENCE_DIR/reviews/jira-tests.log" 2>&1
status=$?
set -e
printf '%s\n' "$status" > "$EVIDENCE_DIR/reviews/jira-tests.exit"
~~~

Use mocked or temporary-file proofs only. Do not run the documented live `whoami` smoke test. When a conclusion depends on current Atlassian behavior, use only linked official Atlassian documentation and record URL/access date.

- [x] **Step 6: Write and validate the lane records**

Write four coverage JSON objects and candidate records, then run:

~~~bash
EVIDENCE_DIR="$EVIDENCE_DIR" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["EVIDENCE_DIR"]) / "reviews"
coverage = [json.loads(line) for line in (root / "jira-coverage.jsonl").read_text().splitlines()]
candidates = [json.loads(line) for line in (root / "jira-candidates.jsonl").read_text().splitlines() if line.strip()]
expected = {
    "skills/abd-jira-cloud/README.md",
    "skills/abd-jira-cloud/SKILL.md",
    "skills/abd-jira-cloud/references/api-notes.md",
    "skills/abd-jira-cloud/scripts/jira.py",
}
assert {row["path"] for row in coverage} == expected
assert len(coverage) == 4
assert all(candidate["id"].startswith("AUD-JIRA-") for candidate in candidates)
print(f"verified Jira lane: {len(coverage)} files, {len(candidates)} candidates")
PY
~~~

Expected: exactly four unique files and no live-call evidence.

---

### Task 5: Review the `abd-code-review` Instruction Supply Chain

**Files:**
- Inspect: `skills/abd-code-review/README.md:1-31`
- Inspect: `skills/abd-code-review/SKILL.md:1-262`
- Inspect: `skills/abd-code-review/references/database.md:1-46`
- Inspect: `skills/abd-code-review/references/dependencies.md:1-34`
- Inspect: `skills/abd-code-review/references/dotnet.md:1-48`
- Inspect: `skills/abd-code-review/references/go.md:1-63`
- Inspect: `skills/abd-code-review/references/infra-cicd.md:1-43`
- Inspect: `skills/abd-code-review/references/java-spring.md:1-45`
- Inspect: `skills/abd-code-review/references/kotlin-android.md:1-53`
- Inspect: `skills/abd-code-review/references/node-ts.md:1-57`
- Inspect: `skills/abd-code-review/references/php-laravel.md:1-56`
- Inspect: `skills/abd-code-review/references/python.md:1-40`
- Inspect: `skills/abd-code-review/references/react-next.md:1-49`
- Inspect: `skills/abd-code-review/references/rust.md:1-49`
- Inspect: `skills/abd-code-review/references/shell-config.md:1-56`
- Inspect: `skills/abd-code-review/references/vue-nuxt.md:1-58`
- Create: `$EVIDENCE_DIR/reviews/instruction-coverage.jsonl`
- Create: `$EVIDENCE_DIR/reviews/instruction-candidates.jsonl`
- Modify: none in the source repository

**Interfaces:**
- Consumes: Task 1 inventory and Task 2 validation/package evidence.
- Produces: exactly 16 coverage rows and zero or more `AUD-INSTR-NNN` candidates.

- [x] **Step 1: Review trigger, target-selection, and authorization behavior**

Read README and `SKILL.md` in full. Check when the skill triggers, what target it chooses without one, whether Git/GitHub commands match the claimed portability, whether reads and writes are clearly separated, and whether instructions can cause unintended repository or external mutation.

- [x] **Step 2: Review review-depth, evidence, and output contracts**

Check size-based coverage rules, confidence/severity calibration, source verification, call-site/history guidance, deduplication, limitations, line-reference accuracy, and the output template. Identify contradictions that could cause a missed defect, false accusation, secret exposure, or unsafe tool use.

- [x] **Step 3: Review every routing edge**

Build a routing matrix from the `SKILL.md` signal table to all 14 reference files. Confirm each referenced path exists, every bundled reference is reachable for an appropriate signal, overlapping stacks load all necessary cross-cutting references, and README/catalog claims match the actual set.

- [x] **Step 4: Review all stack references in bounded batches**

Review:

- backend/runtime: Go, Python, Java/Spring, PHP/Laravel, Node/TypeScript, Rust, and .NET;
- client: Kotlin/Android, React/Next, and Vue/Nuxt;
- cross-cutting: database, dependencies, infra/CI-CD, and shell/config.

For each file, check advice for technical correctness, safety of suggested commands, outdated absolute claims, missing high-impact checks, duplicated/conflicting rules, and prompt-injection/confused-deputy resistance. A stack not used by this repository is still distributed executable instruction and receives a full instruction receipt, not a silent skip.

- [x] **Step 5: Validate current external claims only when necessary**

Use official language/framework/security documentation only when the finding depends on a temporally changeable contract. Record the exact claim, source URL, and UTC access date; otherwise keep the review offline.

- [x] **Step 6: Write and validate the lane records**

Write 16 coverage JSON objects and candidate records, then run:

~~~bash
EVIDENCE_DIR="$EVIDENCE_DIR" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["EVIDENCE_DIR"]) / "reviews"
coverage = [json.loads(line) for line in (root / "instruction-coverage.jsonl").read_text().splitlines()]
candidates = [json.loads(line) for line in (root / "instruction-candidates.jsonl").read_text().splitlines() if line.strip()]
expected = {
    "skills/abd-code-review/README.md",
    "skills/abd-code-review/SKILL.md",
    "skills/abd-code-review/references/database.md",
    "skills/abd-code-review/references/dependencies.md",
    "skills/abd-code-review/references/dotnet.md",
    "skills/abd-code-review/references/go.md",
    "skills/abd-code-review/references/infra-cicd.md",
    "skills/abd-code-review/references/java-spring.md",
    "skills/abd-code-review/references/kotlin-android.md",
    "skills/abd-code-review/references/node-ts.md",
    "skills/abd-code-review/references/php-laravel.md",
    "skills/abd-code-review/references/python.md",
    "skills/abd-code-review/references/react-next.md",
    "skills/abd-code-review/references/rust.md",
    "skills/abd-code-review/references/shell-config.md",
    "skills/abd-code-review/references/vue-nuxt.md",
}
assert {row["path"] for row in coverage} == expected
assert len(coverage) == 16
assert all(candidate["id"].startswith("AUD-INSTR-") for candidate in candidates)
print(f"verified instruction lane: {len(coverage)} files, {len(candidates)} candidates")
PY
~~~

Expected: all 14 references plus README and `SKILL.md` have receipts.

---

### Task 6: Review Repository Policy, Historical Context, and Release Supply Chain

**Files:**
- Inspect: `.gitattributes:1-40`
- Inspect: `.gitignore:1-9`
- Inspect: `CHANGELOG.md:1-12`
- Inspect: `CONTRIBUTING.md:1-23`
- Inspect: `LICENSE:1-21`
- Inspect: `README.md:1-30`
- Inspect: `.github/workflows/ci.yml:1-30`
- Inspect: `.github/workflows/release.yml:1-43`
- Contextual inspect: `docs/superpowers/plans/2026-07-07-agent-skills-repository.md:1-1251`
- Contextual inspect: `docs/superpowers/plans/2026-07-08-abd-jira-cloud-refinement.md:1-1335`
- Contextual inspect: `docs/superpowers/specs/2026-07-07-agent-skills-repository-design.md:1-145`
- Contextual inspect: `docs/superpowers/specs/2026-07-08-abd-jira-cloud-refinement-design.md:1-318`
- Contextual inspect: `docs/superpowers/specs/2026-07-10-codebase-audit-design.md:1-220`
- Create: `$EVIDENCE_DIR/reviews/release-coverage.jsonl`
- Create: `$EVIDENCE_DIR/reviews/release-candidates.jsonl`
- Modify: none in the source repository

**Interfaces:**
- Consumes: Task 2 baseline, Task 3 package/validator evidence, and Tasks 4-5 public-skill matrices.
- Produces: exactly 13 coverage rows and zero or more `AUD-REL-NNN` candidates.

- [x] **Step 1: Review root public and policy contracts**

Cross-check README, CONTRIBUTING, CHANGELOG, LICENSE, `.gitattributes`, and `.gitignore` against actual supported skills, Python compatibility, validation commands, generated-file policy, installation layout, release artifacts, checksums, and licensing. Verify hidden files explicitly because ordinary file searches can omit them.

- [x] **Step 2: Review CI as a clean-checkout execution path**

Trace checkout, Python setup, permissions, test order, validation, and package dry run. Determine what the substring workflow tests prove and what they do not. Check action references, untrusted pull-request behavior, generated files between steps, shell semantics, and least privilege.

- [x] **Step 3: Review release integrity end to end**

Trace tag filtering, exact version validation, test/validation order, artifact build, archive composition, checksums, token exposure, `gh release create` arguments, tag verification, artifact provenance, overwrite behavior, and deterministic-build claims. Reuse Task 3 evidence instead of running a publishing command.

- [x] **Step 4: Give each historical document a contextual receipt**

Read titles, goals, constraints, completion claims, and current-contract statements rather than line-reviewing every implementation snippet. Report only contradictions that make a present public contract, security claim, or operational instruction inaccurate. For the pinned audit design, record that the 2026-07-11 revision governs execution and appears as post-pin drift.

- [x] **Step 5: Check catalog-to-package completeness**

Compare direct skill directories, validator discovery, root catalog entries, README files, release collection members, changelog entries, and workflow upload glob. Record the exact set at each boundary and explain any mismatch.

- [x] **Step 6: Write and validate the lane records**

Write 13 coverage JSON objects and candidate records, then run:

~~~bash
EVIDENCE_DIR="$EVIDENCE_DIR" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["EVIDENCE_DIR"]) / "reviews"
coverage = [json.loads(line) for line in (root / "release-coverage.jsonl").read_text().splitlines()]
candidates = [json.loads(line) for line in (root / "release-candidates.jsonl").read_text().splitlines() if line.strip()]
expected = {
    ".gitattributes",
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    ".gitignore",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "docs/superpowers/plans/2026-07-07-agent-skills-repository.md",
    "docs/superpowers/plans/2026-07-08-abd-jira-cloud-refinement.md",
    "docs/superpowers/specs/2026-07-07-agent-skills-repository-design.md",
    "docs/superpowers/specs/2026-07-08-abd-jira-cloud-refinement-design.md",
    "docs/superpowers/specs/2026-07-10-codebase-audit-design.md",
}
assert {row["path"] for row in coverage} == expected
assert len(coverage) == 13
assert all(candidate["id"].startswith("AUD-REL-") for candidate in candidates)
print(f"verified release lane: {len(coverage)} files, {len(candidates)} candidates")
PY
~~~

Expected: six root contracts, two workflows, and five contextual documents have explicit receipts.

---

### Task 7: Run and Finalize the Codex Security `0.1.11` Repository Scan

**Files:**
- Read and follow: `/home/abid/.codex/plugins/cache/openai-curated-remote/codex-security/0.1.11/skills/security-scan/SKILL.md`
- Generate: `$SYSTEM_TEMP/codex-security-scans/agent-skills/$SCAN_ID/scan-manifest.json`
- Generate: `$SCAN_DIR/findings.json`
- Generate: `$SCAN_DIR/coverage.json`
- Generate through finalization: `$SCAN_DIR/report.md`
- Generate: `$SCAN_DIR/artifacts/01_context/security_guidance.md` and `threat_model.md`
- Generate: `$SCAN_DIR/artifacts/02_discovery/finding_discovery_report.md`
- Generate when applicable: `rank_input.jsonl`, `rank_shards/rank-shard-NNNN.input.jsonl` and matching output files, `rank_worker_assignments.json`, `rank_output.jsonl`, `deep_review_input.jsonl`, `work_ledger.jsonl`, and `raw_candidates.jsonl` under `artifacts/02_discovery/`
- Generate: `$SCAN_DIR/artifacts/03_coverage/repository_coverage_ledger.md` and, when applicable, `reviewed_surfaces.md`
- Generate when applicable: `$SCAN_DIR/artifacts/04_reconciliation/dedupe_report.md` and `deduped_candidates.jsonl`
- Generate for each candidate: `$SCAN_DIR/artifacts/05_findings/$CANDIDATE_ID/candidate_ledger.jsonl`, `validation_report.md`, validation artifacts, and `attack_path_analysis_report.md`
- Generate for each reportable finding: `$SCAN_DIR/findings/$SLUG/$SLUG.md` and applicable proof files below `poc/`
- Generate when findings are reportable: `$SCAN_DIR/hardening/hardening.md` and `hardening.json`
- Create: `$EVIDENCE_DIR/security-scan-dir.txt`
- Create: `$EVIDENCE_DIR/security-scan-id.txt`
- Create: `$EVIDENCE_DIR/reviews/security-candidates.jsonl`
- Modify: none in the source repository

**Interfaces:**
- Consumes: the clean pinned clone and exact security focus from Global Constraints.
- Produces: one finalized standard repository-scan bundle and main-report crosswalk candidates with `AUD-SEC-NNN` IDs.
- Path variables: `$CANDIDATE_ID` is the plugin-assigned candidate ID recorded in its ledger; `$SLUG` is the schema-valid finding slug recorded in `writeup.reportPath`; `$SCAN_ID` and `$SCAN_DIR` are returned by the top-level scan workflow.

- [x] **Step 1: Verify target and capability before substantive scan work**

Run the shared context block, verify the clone is clean and at the pinned commit, then invoke `codex-security:security-scan` version `0.1.11` for repository scope `.` at `$AUDIT_CHECKOUT`. Supply this exact user context:

~~~text
Audit the immutable Git revision 8605a17c906d715c58b9c1a2511b8d0079446a4a. Prioritize agent prompt injection and confused-deputy behavior; Jira credential confinement and local-data egress; packaging path and symlink handling; CI/release token exposure and artifact provenance; and resource/output privacy. Do not make live Jira calls, publish releases, install dependencies, or modify the repository.
~~~

Follow the skill's host routing and `security_scan` capability preflight. If version `0.1.11` or a required capability is blocked, stop this task with the exact preflight evidence; do not substitute a different version or claim completion.

- [x] **Step 2: Complete the repository threat model**

Compile and read resolved security guidance, write the repository-scoped threat model, copy it unchanged to `artifacts/01_context/threat_model.md`, and end it with the plugin-required repository target identity and pinned version. Do not inspect ahead into later phase skills until the threat-model phase is complete.

- [x] **Step 3: Complete finding discovery and coverage closure**

Run the discovery phase against all 40 pinned files. Produce the ranked runtime-surface worklist and repository coverage ledger, close every applicable high-impact and seeded root-control row, and preserve raw candidate-local validation and attack-path facts before deduplication. Instruction files are executable behavior and remain in scan scope.

- [x] **Step 4: Complete candidate validation**

Validate every discovered candidate and every open seeded/root-control row. Each candidate must have a discovery receipt before validation and a validation receipt before later reporting. Use safe local proofs only; no Jira network call or release action.

- [x] **Step 5: Complete attack-path and severity analysis**

For every candidate or closure row that reaches this phase, record entry point, controls, sink, reachability, concrete impact, policy/severity reasoning, and an attack-path receipt even when the final decision is suppression or deferral.

- [x] **Step 6: Assemble canonical JSON and finalize once**

Assemble `scan-manifest.json`, `findings.json`, and `coverage.json` last. Generate one detailed vulnerability write-up per reportable finding and one hardening portfolio over the complete reportable set. Skip hardening and omit its manifest link when there are no reportable findings. Let the workflow finalizer generate `report.md`; never write it by hand.

- [x] **Step 7: Persist and verify the scan directory**

Write the canonical absolute scan path returned by the workflow:

~~~bash
SCAN_ID="$(basename "$SCAN_DIR")"
printf '%s\n' "$SCAN_DIR" > "$EVIDENCE_DIR/security-scan-dir.txt"
printf '%s\n' "$SCAN_ID" > "$EVIDENCE_DIR/security-scan-id.txt"
~~~

Then run:

~~~bash
EVIDENCE_DIR="$EVIDENCE_DIR" AUDIT_TARGET="$AUDIT_TARGET" python3 - <<'PY'
import json
import os
from pathlib import Path

scan_dir = Path((Path(os.environ["EVIDENCE_DIR"]) / "security-scan-dir.txt").read_text().strip())
required = (
    "scan-manifest.json",
    "findings.json",
    "coverage.json",
    "report.md",
    "artifacts/01_context/security_guidance.md",
    "artifacts/01_context/threat_model.md",
    "artifacts/02_discovery/finding_discovery_report.md",
    "artifacts/03_coverage/repository_coverage_ledger.md",
)
for relative in required:
    path = scan_dir / relative
    assert path.is_file() and not path.is_symlink(), relative

manifest = json.loads((scan_dir / "scan-manifest.json").read_text())
findings = json.loads((scan_dir / "findings.json").read_text())
coverage = json.loads((scan_dir / "coverage.json").read_text())
assert manifest["documentType"] == "codex-security.scan-manifest"
assert findings["documentType"] == "codex-security.findings"
assert coverage["documentType"] == "codex-security.coverage"
assert manifest["schemaVersion"] == findings["schemaVersion"] == coverage["schemaVersion"] == "1.0"
assert manifest["scan"]["status"] == "completed"
assert manifest["scan"]["producer"]["version"] == "0.1.11"
assert manifest["scan"]["target"]["kind"] == "git_revision"
assert manifest["scan"]["target"]["revision"] == os.environ["AUDIT_TARGET"]
assert coverage["mode"] == "repository"
assert coverage["completeness"] == "complete"

if findings["findings"]:
    assert (scan_dir / "hardening/hardening.md").is_file()
    assert (scan_dir / "hardening/hardening.json").is_file()
    for finding in findings["findings"]:
        report = finding.get("writeup", {}).get("reportPath")
        assert report and (scan_dir / report).is_file(), finding["findingId"]
print(f"verified finalized security scan: {scan_dir}")
PY
~~~

Expected: the manifest is completed, its target revision is the full pinned SHA, coverage is complete, and conditional finding artifacts exist.

- [x] **Step 8: Build the lossless main-report crosswalk**

Create one `AUD-SEC-NNN` candidate record for every plugin candidate requiring audit-level closure. Preserve canonical `findingId`, candidate IDs, severity, confidence, locations, ledger path, validation report, and attack-path report in `security_refs`. Independently derive main severity/confidence with written rationale and keep separately reachable sibling findings distinct.

---

### Task 8: Reconcile Coverage and Close Every Candidate

**Files:**
- Read: all `$EVIDENCE_DIR/reviews/*-coverage.jsonl`
- Read: all `$EVIDENCE_DIR/reviews/*-candidates.jsonl`
- Read: finalized security bundle
- Create: `$EVIDENCE_DIR/reconciliation/coverage.jsonl`
- Create: `$EVIDENCE_DIR/reconciliation/candidates.jsonl`
- Create: `$EVIDENCE_DIR/reconciliation/security-crosswalk.jsonl`
- Create: `$EVIDENCE_DIR/reconciliation/roadmap-seeds.jsonl`
- Modify: none in the source repository

**Interfaces:**
- Consumes: Tasks 2-7 receipts, candidates, proofs, and canonical security output.
- Produces: the only canonical inputs allowed for Tasks 9-10.

- [x] **Step 1: Prove the manual lanes form an exact partition**

Run:

~~~bash
EVIDENCE_DIR="$EVIDENCE_DIR" AUDIT_CHECKOUT="$AUDIT_CHECKOUT" AUDIT_TARGET="$AUDIT_TARGET" python3 - <<'PY'
import json
import os
import subprocess
from pathlib import Path

reviews = Path(os.environ["EVIDENCE_DIR"]) / "reviews"
files = (
    "core-coverage.jsonl",
    "jira-coverage.jsonl",
    "instruction-coverage.jsonl",
    "release-coverage.jsonl",
)
rows = []
for name in files:
    rows.extend(json.loads(line) for line in (reviews / name).read_text().splitlines())
actual = [row["path"] for row in rows]
expected = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", os.environ["AUDIT_TARGET"]],
    cwd=os.environ["AUDIT_CHECKOUT"],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()
assert len(actual) == len(set(actual)) == 40
assert set(actual) == set(expected)
print("verified review partition: every pinned path exactly once")
PY
~~~

Expected: 40 unique manual receipts with no missing or duplicate path.

- [x] **Step 2: Normalize coverage without replacing file receipts with security surfaces**

Concatenate the four pinned coverage ledgers and the generated-content ledger into `reconciliation/coverage.jsonl`. Preserve the security ledger as a linked surface-level artifact; do not turn its surface rows into file rows or use it to fill a missing manual receipt.

- [x] **Step 3: Reconcile duplicate candidates by root cause**

Compare `root_cause_key`, affected behavior, controls, sinks, and locations across all lanes. Choose one canonical audit ID, retain every other stable ID in `aliases`, preserve every affected location, and link every security artifact. Write `security-crosswalk.jsonl` using the shared crosswalk keys. Do not merge independently reachable security instances; use `summary_group` for shared prose instead.

- [x] **Step 4: Close every candidate**

For each candidate, confirm:

- exact pinned file/line evidence;
- concrete impact or counterevidence;
- recorded validation command/test;
- `confirmed`, `likely`, or `unverified` confidence;
- one allowed final disposition;
- main severity for reportable items;
- entry/control/sink and plugin receipts for security items;
- specific remediation and future verification commands.

If proof is missing, use `deferred` and name the missing proof. If behavior is disproved, use `suppressed`. Never silently drop a candidate.

- [x] **Step 5: Calibrate findings and roadmap seeds**

Order reportable candidates by `Blocking`, `Should fix`, `Worth considering`, then `Nit`, and by stable ID within a severity. Create roadmap seeds for every reportable finding and any explicit `HARDENING-NNN` defense-in-depth goal. Preserve plugin severity/confidence in the security crosswalk and explain every main-label choice.

- [x] **Step 6: Validate reconciliation types and closure**

Run:

~~~bash
EVIDENCE_DIR="$EVIDENCE_DIR" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["EVIDENCE_DIR"]) / "reconciliation"
coverage = [json.loads(line) for line in (root / "coverage.jsonl").read_text().splitlines()]
candidates = [json.loads(line) for line in (root / "candidates.jsonl").read_text().splitlines() if line.strip()]
roadmap_seeds = [json.loads(line) for line in (root / "roadmap-seeds.jsonl").read_text().splitlines() if line.strip()]
crosswalk = [json.loads(line) for line in (root / "security-crosswalk.jsonl").read_text().splitlines() if line.strip()]
assert len([row for row in coverage if row["scope"] == "pinned tracked"]) == 40
assert len({row["path"] for row in coverage if row["scope"] == "pinned tracked"}) == 40
all_candidate_ids = [candidate["id"] for candidate in candidates]
all_candidate_ids.extend(alias for candidate in candidates for alias in candidate["aliases"])
assert len(set(all_candidate_ids)) == len(all_candidate_ids)

closures = {"reportable", "suppressed", "not applicable", "deferred"}
severities = {"Blocking", "Should fix", "Worth considering", "Nit"}
confidences = {"confirmed", "likely", "unverified"}
lanes = {"core", "jira", "instruction", "release", "security"}
categories = {"correctness", "maintainability", "security", "release", "documentation", "instruction supply chain"}
for row in coverage:
    assert row["scope"] in {"pinned tracked", "ignored/generated"}
    if row["scope"] == "pinned tracked":
        assert row["disposition"] in {"reviewed", "contextual", "not applicable"}
    else:
        assert row["disposition"] in {"included", "not applicable"}
for candidate in candidates:
    assert candidate["lane"] in lanes
    assert candidate["category"] in categories
    assert candidate["disposition"] in closures
    assert candidate["confidence"] in confidences
    assert candidate["closure_reason"]
    assert candidate["remediation"]
    assert candidate["verification_commands"]
    if candidate["disposition"] == "reportable":
        assert candidate["severity"] in severities
    else:
        assert candidate["severity"] is None
    if candidate["category"] == "security":
        assert candidate["entry_point"] and candidate["control"] and candidate["sink"]
        assert candidate["security_refs"]
    assert not (candidate["confidence"] == "unverified" and candidate["severity"] == "Blocking")
for seed in roadmap_seeds:
    assert seed["traceability"]
    assert seed["priority"] in {"P0", "P1", "P2", "P3"}
    assert seed["effort"] in {"S", "M", "L"}
    assert seed["affected_files"]
    assert seed["acceptance_criteria"]
    assert seed["verification_commands"]
crosswalk_keys = {
    "audit_id", "plugin_candidate_id", "finding_id", "plugin_disposition",
    "plugin_severity", "plugin_confidence", "main_disposition", "main_severity",
    "main_confidence", "candidate_ledger", "validation_report", "attack_path_report",
}
for row in crosswalk:
    assert set(row) == crosswalk_keys
print(f"verified reconciliation: {len(coverage)} coverage rows, {len(candidates)} closed candidates, {len(roadmap_seeds)} roadmap seeds, {len(crosswalk)} security mappings")
PY
~~~

Expected: exact pinned coverage and no open, malformed, or duplicate candidate ID.

---

### Task 9: Write and Verify the Main Audit Report

**Files:**
- Create: `docs/audits/2026-07-10-codebase-audit.md`
- Read: `$EVIDENCE_DIR/reconciliation/coverage.jsonl`
- Read: `$EVIDENCE_DIR/reconciliation/candidates.jsonl`
- Read: `$EVIDENCE_DIR/security-scan-dir.txt`

**Interfaces:**
- Consumes: Task 8 canonical reconciliation only.
- Produces: the canonical reader-facing report and stable finding/hardening IDs consumed by Task 10.

- [x] **Step 1: Create the report with the exact section order**

Use `apply_patch` to create the report with these literal headings:

~~~markdown
# Full Codebase Audit: `agent-skills`

## Executive Verdict

## Audit Identity and Scope

## Drift from the Pinned Tree

## Method and Evidence

## Baseline and Available Tooling

## Coverage Overview

## Candidate Disposition Ledger

<!-- candidate-ledger:start -->
| Candidate ID | Category | Final disposition | Confidence | Main severity | Security IDs | Closure evidence |
|---|---|---|---|---|---|---|
<!-- candidate-ledger:end -->

## Findings

### Blocking

### Should fix

### Worth considering

### Nit

## Security Scan Bundle

## Limitations and Deferred Work

## Strengths Worth Preserving

## Hardening Goals

## Appendix A: Coverage Inventory

<!-- coverage-inventory:start -->
| Path | Scope | Role | Risk | Review receipt | Disposition | Candidate IDs |
|---|---|---|---|---|---|---|
<!-- coverage-inventory:end -->
~~~

Populate every section from named evidence artifacts. Use `No findings.` in an empty severity subsection, `No candidates were discovered.` when the candidate ledger is empty, `No deferred work.` when applicable, and `No standalone hardening goals.` when every roadmap seed traces to a finding.

- [x] **Step 2: Write audit identity, drift, baseline, and limitations**

Name the full pinned SHA, 40-file count, source HEAD at start, UTC start/end, current working-tree state, committed drift, ignored/generated snapshots, exact baseline commands/statuses, available/unavailable tools, failed checks and alternatives, and the stricter no-live-Jira rule. Explain that the current revised design controls execution while the pinned design blob is contextual evidence.

- [x] **Step 3: Write the complete candidate ledger and findings**

Give every canonical candidate one ledger row with ID, aliases, category, disposition, confidence, main severity when reportable, security IDs when applicable, and closure evidence. Mention every alias in its canonical row so no discovered candidate disappears during deduplication. Each reportable finding heading is `#### AUD-LANE-NNN — Concrete title` and includes:

- main severity/confidence with rationale;
- exact pinned locations;
- behavior and concrete impact;
- entry/control/sink for security;
- validation commands/results and counterevidence;
- practical remediation and verification criteria;
- links to detailed security artifacts without copying the full write-up.

Order findings by the four literal severity headings. Keep grouped root-cause prose lossless through aliases, instances, and affected locations.

- [x] **Step 4: Write the security bundle reference and retention limitation**

Read `$SCAN_DIR` from `security-scan-dir.txt` and `$SCAN_ID` from `security-scan-id.txt`. Record both the resolved absolute path and portable form `$SYSTEM_TEMP/codex-security-scans/agent-skills/$SCAN_ID/`. Link canonical JSON, generated `report.md`, threat model, discovery report, coverage ledger, and applicable candidate/write-up/hardening artifacts. Render `security-crosswalk.jsonl` as a table with audit ID, plugin candidate/finding IDs, both taxonomies, final disposition, and three receipt links. State that system-temporary retention is environment-dependent and the bundle must remain intact for the report to be fully verifiable.

- [x] **Step 5: Populate every coverage row**

Render exactly 40 `pinned tracked` rows from reconciliation plus one `ignored/generated` row per audit-start expanded ignored file. Wrap each path in Markdown code spans so the mechanical parser can identify it. Receipts cite the pinned revision, exact lines or full-file range, review method, and candidate IDs. Historical documents use `contextual` with the contradiction check performed; ignored entries use `included` or `not applicable` with a concrete reason. Escape any literal table-cell pipe as `\|`. Link the security coverage ledger once in the appendix introduction rather than duplicating its surface rows.

- [x] **Step 6: Validate the report mechanically**

Run:

~~~bash
SOURCE_REPO="$SOURCE_REPO" AUDIT_CHECKOUT="$AUDIT_CHECKOUT" AUDIT_TARGET="$AUDIT_TARGET" EVIDENCE_DIR="$EVIDENCE_DIR" python3 - <<'PY'
import json
import os
import re
import subprocess
from pathlib import Path

source = Path(os.environ["SOURCE_REPO"])
report_path = source / "docs/audits/2026-07-10-codebase-audit.md"
report = report_path.read_text(encoding="utf-8")
target = os.environ["AUDIT_TARGET"]
assert target in report

required_headings = (
    "## Executive Verdict",
    "## Audit Identity and Scope",
    "## Drift from the Pinned Tree",
    "## Baseline and Available Tooling",
    "## Candidate Disposition Ledger",
    "## Findings",
    "## Security Scan Bundle",
    "## Limitations and Deferred Work",
    "## Strengths Worth Preserving",
    "## Appendix A: Coverage Inventory",
)
for heading in required_headings:
    assert heading in report, heading

block = report.split("<!-- coverage-inventory:start -->", 1)[1].split("<!-- coverage-inventory:end -->", 1)[0]
rows = []
for line in block.splitlines():
    if not line.startswith("| `"):
        continue
    cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
    rows.append((cells[0].strip("`"), cells[1], cells[5]))

expected = set(subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", target],
    cwd=os.environ["AUDIT_CHECKOUT"],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines())
pinned = [path for path, scope, _ in rows if scope == "pinned tracked"]
assert len(pinned) == len(set(pinned)) == 40
assert set(pinned) == expected

ignored_expected = set((Path(os.environ["EVIDENCE_DIR"]) / "start/ignored-files.txt").read_text().splitlines())
ignored_actual = {path for path, scope, _ in rows if scope == "ignored/generated"}
assert ignored_actual == ignored_expected

candidates = [
    json.loads(line)
    for line in (Path(os.environ["EVIDENCE_DIR"]) / "reconciliation/candidates.jsonl").read_text().splitlines()
    if line.strip()
]
for candidate in candidates:
    assert candidate["id"] in report
    for alias in candidate["aliases"]:
        assert alias in report
    if candidate["disposition"] == "reportable":
        assert re.search(rf"^#### {re.escape(candidate['id'])}\b", report, re.MULTILINE)

scan_dir = (Path(os.environ["EVIDENCE_DIR"]) / "security-scan-dir.txt").read_text().strip()
assert scan_dir in report
print(f"verified audit report: {len(pinned)} pinned rows, {len(ignored_actual)} generated rows, {len(candidates)} candidates")
PY
~~~

Expected: exact coverage equality, every candidate accounted for, and the finalized scan linked.

- [x] **Step 7: Commit the main audit report**

Run:

~~~bash
git -C "$SOURCE_REPO" add docs/audits/2026-07-10-codebase-audit.md
git -C "$SOURCE_REPO" commit -m "docs: add full codebase audit" \
  -m "Co-Authored-By: GPT-5 Codex <noreply@openai.com>"
~~~

Expected: only the main audit report is committed.

---

### Task 10: Write and Verify the Remediation Roadmap

**Files:**
- Create: `docs/audits/2026-07-10-remediation-roadmap.md`
- Read: `docs/audits/2026-07-10-codebase-audit.md`
- Read: `$EVIDENCE_DIR/reconciliation/roadmap-seeds.jsonl`

**Interfaces:**
- Consumes: finalized canonical findings and explicit hardening goals from Task 9.
- Produces: dependency-ordered `RM-NNN` items; every item traces to at least one `AUD-*` or `HARDENING-NNN` ID.

- [x] **Step 1: Create the roadmap with the exact section order**

Use `apply_patch` to create:

~~~markdown
# Codebase Audit Remediation Roadmap

## Scope and Prioritization

## Dependency and Sequencing Summary

## P0 — Immediate Containment or Release Blocking

## P1 — Next Focused Material-Risk Changes

## P2 — Planned Hardening, Compatibility, and Maintainability

## P3 — Optional Hygiene and Future-Scale Improvements

## Remediation Items

<!-- roadmap-items:start -->
<!-- roadmap-items:end -->

## Deferred Investigation Items

## Verification Matrix
~~~

Use `None.` under an empty priority section and `No remediation items.` between the markers when there are no reportable findings or explicit hardening goals.

- [x] **Step 2: Define dependency order and effort**

Assign `RM-001` onward in actual implementation order, not severity order. Every item states one priority, `S`/`M`/`L` effort under the Global Constraints scale, dependencies by roadmap ID or `None`, exact affected files, and why the sequence avoids unsafe partial remediation.

- [x] **Step 3: Write implementation-ready items**

Each item uses this literal field order:

~~~markdown
### RM-001 — Concise action title

- **Priority:** P1
- **Traceability:** AUD-CORE-001
- **Effort:** S
- **Dependencies:** None
- **Affected files:** `exact/repository/path`
- **Why now:** Concrete risk and sequencing rationale.
- **Acceptance criteria:**
  - Observable post-remediation behavior.
- **Verification commands:**
  - `exact command`
~~~

Replace the sample values with reconciled IDs, real repository paths, concrete acceptance behavior, and commands that would fail before remediation and pass afterward. Do not include broad implementation advice without a measurable acceptance condition.

- [x] **Step 4: Preserve deferred work and hardening traceability**

Carry every deferred candidate into `Deferred Investigation Items` with missing proof, safe next command, and the condition for promotion/suppression. Explicit defense-in-depth work uses `HARDENING-NNN` IDs defined in the audit report. Do not invent roadmap work unrelated to a finding or labeled hardening goal.

- [x] **Step 5: Build the verification matrix**

For each `RM-NNN`, repeat its traceability IDs, acceptance-criterion summary, exact focused command, and broader regression commands. Include the three repository baseline commands for any item that can change packaged content, validation, tests, or workflows.

- [x] **Step 6: Validate roadmap traceability**

Run:

~~~bash
SOURCE_REPO="$SOURCE_REPO" EVIDENCE_DIR="$EVIDENCE_DIR" python3 - <<'PY'
import json
import os
import re
from pathlib import Path

source = Path(os.environ["SOURCE_REPO"])
report = (source / "docs/audits/2026-07-10-codebase-audit.md").read_text()
roadmap = (source / "docs/audits/2026-07-10-remediation-roadmap.md").read_text()
candidates = [
    json.loads(line)
    for line in (Path(os.environ["EVIDENCE_DIR"]) / "reconciliation/candidates.jsonl").read_text().splitlines()
    if line.strip()
]
reportable = {item["id"] for item in candidates if item["disposition"] == "reportable"}
hardening = set(re.findall(r"\bHARDENING-\d{3}\b", report))
roadmap_ids = re.findall(r"^### (RM-\d{3})\b", roadmap, re.MULTILINE)
assert len(roadmap_ids) == len(set(roadmap_ids))
assert roadmap_ids == [f"RM-{number:03d}" for number in range(1, len(roadmap_ids) + 1)]

traces = set(re.findall(r"\b(?:AUD-(?:CORE|JIRA|INSTR|REL|SEC)-\d{3}|HARDENING-\d{3})\b", roadmap))
assert traces <= reportable | hardening
assert reportable <= traces
for roadmap_id in roadmap_ids:
    start = roadmap.index(f"### {roadmap_id}")
    next_start = roadmap.find("\n### RM-", start + 1)
    body = roadmap[start: next_start if next_start != -1 else len(roadmap)]
    for field in ("Priority", "Traceability", "Effort", "Dependencies", "Affected files", "Why now", "Acceptance criteria", "Verification commands"):
        assert f"**{field}:**" in body, (roadmap_id, field)
print(f"verified roadmap: {len(roadmap_ids)} items, {len(reportable)} reportable findings")
PY
~~~

Expected: sequential roadmap IDs, complete required fields, no orphan item, and every reportable finding traced.

- [x] **Step 7: Commit the remediation roadmap**

Run:

~~~bash
git -C "$SOURCE_REPO" add docs/audits/2026-07-10-remediation-roadmap.md
git -C "$SOURCE_REPO" commit -m "docs: add codebase remediation roadmap" \
  -m "Co-Authored-By: GPT-5 Codex <noreply@openai.com>"
~~~

Expected: only the remediation roadmap is committed.

---

### Task 11: Run the Fresh Completion Gate

**Files:**
- Verify: `docs/audits/2026-07-10-codebase-audit.md`
- Verify: `docs/audits/2026-07-10-remediation-roadmap.md`
- Verify: finalized `$SCAN_DIR` bundle
- Verify read-only: all 40 pinned files
- Modify only if a gate exposes a report/roadmap defect: the two audit documents

**Interfaces:**
- Consumes: every prior task output.
- Produces: evidence that all design completion criteria hold and no product/external mutation occurred.

- [x] **Step 1: Invoke the completion-verification workflow**

Invoke `superpowers:verification-before-completion` and use fresh command output from this task. Do not rely on earlier green logs for the final claim.

- [x] **Step 2: Re-run the repository baseline in the pinned clone**

Run:

~~~bash
(
  cd "$AUDIT_CHECKOUT"
  env -u JIRA_BASE_URL -u JIRA_EMAIL -u JIRA_API_TOKEN \
    PYTHONDONTWRITEBYTECODE=1 \
    python3 -m unittest discover -s tests -v
  env PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_skills.py
  env PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --version v0.0.0 --dry-run
)
~~~

Expected documented baseline: 54 passing tests, two validated skills, and a passing packaging dry run. If fresh output differs, update the report with the failure and affected coverage before continuing.

- [x] **Step 3: Re-run Tasks 7, 9, and 10 mechanical validators**

Run the finalized security-bundle check, report coverage/candidate check, and roadmap traceability check exactly as written in those tasks. Expected: all three pass with the same scan directory and candidate counts.

- [x] **Step 4: Take the end-state ignored/generated snapshot**

Run:

~~~bash
git -C "$SOURCE_REPO" status --ignored --porcelain > "$EVIDENCE_DIR/end-ignored-status.txt"
git -C "$SOURCE_REPO" ls-files --others --ignored --exclude-standard > "$EVIDENCE_DIR/end-ignored-files.txt"
diff -u "$EVIDENCE_DIR/start/ignored-files.txt" "$EVIDENCE_DIR/end-ignored-files.txt" \
  > "$EVIDENCE_DIR/ignored-drift.diff" || true
~~~

Record any new entry and give it a coverage receipt before completion. Audit-created files must be limited to the two repository documents and the documented temporary roots.

- [x] **Step 5: Prove no product file changed**

Run:

~~~bash
git -C "$SOURCE_REPO" diff --check "$HEAD_AT_START"..HEAD
git -C "$SOURCE_REPO" diff --name-only "$HEAD_AT_START"..HEAD > "$EVIDENCE_DIR/repository-files-changed-by-audit.txt"
EVIDENCE_DIR="$EVIDENCE_DIR" python3 - <<'PY'
import os
from pathlib import Path

allowed = {
    "docs/audits/2026-07-10-codebase-audit.md",
    "docs/audits/2026-07-10-remediation-roadmap.md",
}
path = Path(os.environ["EVIDENCE_DIR"]) / "repository-files-changed-by-audit.txt"
actual = set(path.read_text().splitlines())
assert actual <= allowed, sorted(actual - allowed)
print(f"verified repository mutation boundary: {sorted(actual)}")
PY
test -z "$(git -C "$AUDIT_CHECKOUT" status --porcelain)"
~~~

Expected: only the two audit documents changed since `HEAD_AT_START` and the pinned clone is clean.

- [x] **Step 6: Perform the primary reviewer's semantic closure**

Read the current design again and point every completion criterion to report text or a verified artifact:

- target and drift named;
- 40 pinned receipts plus every ignored/generated receipt;
- every candidate reportable, suppressed, not applicable, or deferred;
- every reportable security issue backed by validation and attack-path receipts;
- finalized scan linked;
- baseline rerun and recorded;
- audit and roadmap internally consistent;
- every roadmap item traced;
- no product or external-system mutation.

Correct any report-only gap with `apply_patch` and re-run all affected validators.

- [x] **Step 7: Commit only verified document corrections, when present**

Run:

~~~bash
if ! git -C "$SOURCE_REPO" diff --quiet -- docs/audits/2026-07-10-codebase-audit.md docs/audits/2026-07-10-remediation-roadmap.md; then
  git -C "$SOURCE_REPO" add docs/audits/2026-07-10-codebase-audit.md docs/audits/2026-07-10-remediation-roadmap.md
  git -C "$SOURCE_REPO" commit -m "docs: close codebase audit evidence gaps" \
    -m "Co-Authored-By: GPT-5 Codex <noreply@openai.com>"
fi
git -C "$SOURCE_REPO" status --short
~~~

Expected: no uncommitted audit-document changes and no unrelated path staged or committed.
