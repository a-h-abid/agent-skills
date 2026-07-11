# Audit Remediation Implementation Plan

> **Status: Executed to completion (2026-07-11)** via subagent-driven
> development; merged to `main` as `a65d327`. Every checkbox is marked except
> Task 1 Step 8 (human-only: observe green CI on the repinned refs after push).
> Post-merge verification on `main`: 57/57 tests OK, `Validated 2 skill(s).`,
> `Packaging dry run passed.` (The "Validated 1 skill(s)." expectations below
> are stale — the repo has two skills; treat "Validated 2 skill(s)." as the
> green output if this plan is reused as a template.)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Execution mode:** Subagent-driven development is the intended mode — dispatch a
> fresh subagent per task. These tasks are mechanical and fully specified, so a
> **lower-cost model is suggested for the implementer subagents** (e.g. pass
> `model: "haiku"` — or `model: "sonnet"` if a task's subagent stumbles — in the
> Agent call); keep review between tasks in the main session on the session model.
>
> **Checkbox discipline:** after a step is done **and its verification observed**
> (command run, expected output seen), edit this file and change that step's
> `- [ ]` to `- [x]` before moving on. Never mark a checkbox on intent.

**Goal:** Implement the three audit remediations RM-001 (SHA-pin GitHub Actions + Dependabot), RM-002 (exclude bytecode from packaged archives), and RM-003 (disclose unverified identity resolution in jira dry-run) from `docs/superpowers/specs/2026-07-11-audit-remediation-design.md`.

**Architecture:** Three surgical, independent edits touching disjoint files — no new shared abstraction. Each behavioral change is test-driven: failing test first, minimal fix, then the roadmap's verification commands with output shown. Order RM-001 → RM-002 → RM-003 (tidiness only; no cross-dependency).

**Tech Stack:** Python 3.12 stdlib only (`unittest`, `zipfile`, `pathlib`), GitHub Actions YAML, Dependabot v2 config. Test runner: `python3 -m unittest`. No third-party dependencies anywhere.

## Global Constraints

- Repo root is the working directory for every command: `~/dev-projects/abd/agent-skills` (or its worktree copy).
- Stdlib only — do not add any dependency, `requirements.txt`, or tool config.
- TDD is mandatory for RM-002/RM-003: run the new test and observe it FAIL before writing implementation code.
- Every commit message ends with a `Co-Authored-By: <model> <email>` sign-off trailer per the repo owner's global instructions. Resolve the **actual full session model name** from session/runtime metadata at commit-execution time — do not copy a name from this plan; if the committing agent cannot determine the exact model identity, omit the trailer entirely rather than guessing.
- Agents must NOT run `git fetch`, `git push`, or `git pull` (globally restricted). Pushing and observing CI is the human partner's step; the plan marks it explicitly.
- Out of scope: `docs/audits/*` documents, `docs/superpowers/plans/2026-07-11-codebase-audit.md`, any unrelated refactoring.
- jira.py dry-run output invariant: exactly **one JSON value** per previewed request, and the preview's `url`/`body` must stay byte-faithful to what a live run would send.
- Full regression trio (run after every task): `python3 -m unittest discover -s tests -v` && `python3 scripts/validate_skills.py` && `python3 scripts/package_skills.py --version v0.0.0 --dry-run`.

---

### Task 1: RM-001 — Pin GitHub Actions to commit SHAs + Dependabot

**Files:**
- Modify: `.github/workflows/ci.yml` (two `uses:` lines)
- Modify: `.github/workflows/release.yml` (two `uses:` lines)
- Create: `.github/dependabot.yml`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: nothing consumed by other tasks (workflow-only change).

- [x] **Step 1: Resolve the current latest upstream releases and their commit SHAs**

The spec resolved these values (re-confirm; a newer patch may have shipped since 2026-07-11):

- `actions/checkout` → tag `v7.0.0`, SHA `9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0`
- `actions/setup-python` → tag `v6.3.0`, SHA `ece7cb06caefa5fff74198d8649806c4678c61a1`

Run (network read-only; this is not git fetch/push/pull):

```bash
gh api repos/actions/checkout/releases/latest --jq '.tag_name + " prerelease=" + (.prerelease|tostring)'
gh api repos/actions/setup-python/releases/latest --jq '.tag_name + " prerelease=" + (.prerelease|tostring)'
```

Expected: a `vN.N.N` tag each, `prerelease=false`. Never pin a release candidate or prerelease. Then resolve each tag to its commit SHA (this endpoint dereferences annotated tags):

```bash
gh api repos/actions/checkout/commits/<TAG> --jq '.sha'
gh api repos/actions/setup-python/commits/<TAG> --jq '.sha'
```

Expected: one 40-hex SHA each. If the tags are still `v7.0.0`/`v6.3.0`, the SHAs must equal the spec values above; on mismatch, stop and report instead of proceeding. If `gh` is unavailable, use `curl -s https://api.github.com/repos/actions/<repo>/commits/<TAG>` and read `.sha`.

Record `<CHECKOUT_SHA>`, `<CHECKOUT_TAG>`, `<SETUP_PYTHON_SHA>`, `<SETUP_PYTHON_TAG>` for the next steps.

Breaking-change check (these pins are major upgrades: checkout v4→v7, setup-python v5→v6): both workflows use each action with default or trivial inputs (`python-version: "3.12"` only), so no breakage is expected. If CI later fails on the new major (Step 8), fall back to pinning the latest release of the currently-used major (`gh api repos/actions/checkout/commits/v4 --jq '.sha'` etc.) — the finding is about pinning, not upgrading.

- [x] **Step 2: Pin both actions in `ci.yml`**

In `.github/workflows/ci.yml`, replace:

```yaml
        uses: actions/checkout@v4
```

with (substitute recorded values):

```yaml
        uses: actions/checkout@<CHECKOUT_SHA> # <CHECKOUT_TAG>
```

and replace:

```yaml
        uses: actions/setup-python@v5
```

with:

```yaml
        uses: actions/setup-python@<SETUP_PYTHON_SHA> # <SETUP_PYTHON_TAG>
```

The comment must be exactly `# vN.N.N` (the roadmap regex requires `v\d+\.\d+\.\d+`). Touch nothing else in the file.

- [x] **Step 3: Pin both actions in `release.yml`**

Apply the identical two replacements in `.github/workflows/release.yml` (same lines, same substituted values). Touch nothing else.

- [x] **Step 4: Create `.github/dependabot.yml`**

Exact content:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    cooldown:
      default-days: 7
```

- [x] **Step 5: Run the roadmap RM-001 regex assertion**

Run (verbatim from the roadmap):

```bash
python3 -c "from pathlib import Path; import re; refs = [match.groups() for path in (Path('.github/workflows/ci.yml'), Path('.github/workflows/release.yml')) for match in re.finditer(r'^\\s*uses:\\s*(actions/[^\\s#]+)(?:\\s+#\\s+([^\\n]+))?\\s*$', path.read_text(), re.MULTILINE)]; config = Path('.github/dependabot.yml').read_text(); assert refs and all(re.fullmatch(r'actions/[A-Za-z0-9_.-]+@[0-9a-f]{40}', ref) and comment and re.fullmatch(r'v\\d+\\.\\d+\\.\\d+', comment.strip()) for ref, comment in refs), refs; assert re.search(r'package-ecosystem:\\s*\"github-actions\"', config) and re.search(r'directory:\\s*\"/\"', config) and re.search(r'schedule:\\s*\\n\\s*interval:\\s*\"(?:daily|weekly|monthly)\"', config), config"
```

Expected: exits 0 with no output. An `AssertionError` prints the offending refs/config — fix and rerun.

- [x] **Step 6: Run the full regression trio**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

Expected: `OK` from unittest; `Validated 1 skill(s).`; `Packaging dry run passed.`

- [x] **Step 7: Commit**

```bash
git add .github/workflows/ci.yml .github/workflows/release.yml .github/dependabot.yml
git commit -m "ci: pin GitHub Actions to commit SHAs and add Dependabot config

RM-001 / AUD-REL-001: replace floating major-version tags with full
commit SHAs plus version comments; add weekly Dependabot github-actions
updates with a 7-day cooldown so bumps arrive as review-gated PRs."
```

Append the sign-off trailer per Global Constraints (resolve the model name at commit time).

- [ ] **Step 8 (human partner, after merge/push): observe a green CI run on the repinned refs**

`release.yml` triggers only on `v*.*.*` tags, so a passing CI run (identical checkout/setup-python steps) is the accepted proxy; the release workflow is finally confirmed by the first tagged release. Agents must not push — flag this step to the human in the task report.

---

### Task 2: RM-002 — Exclude `__pycache__`/`*.pyc`/`*.pyo` from packaged archives

**Files:**
- Modify: `scripts/package_skills.py:33-39` (`source_files`; add `_is_ignorable` above it)
- Test: `tests/test_package_skills.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `_is_ignorable(path: Path, skill: Path) -> bool` (module-private helper) and the filtered `source_files(skill: Path) -> list[Path]`. Both archive builders (`expected_individual_entries`, `expected_collection_entries`) already funnel through `source_files()` — do NOT add per-builder filtering.

- [x] **Step 1: Write the failing tests**

Append to `tests/test_package_skills.py` inside `PackageSkillsTests` (before the `if __name__` block). The suite's existing `write_skill` fixture and imports are already in the file:

```python
    def test_excludes_bytecode_artifacts_from_archives(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            skill = root / "skills" / "abd-alpha"
            cache = skill / "scripts" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "x.cpython-312.pyc").write_bytes(b"\x00fake bytecode")
            (skill / "references" / "stale.pyo").write_bytes(b"\x00stale bytecode")
            output = root / "dist"

            build_packages(root, output, "v1.0.0")

            members: list[str] = []
            for archive_name in ("abd-alpha-v1.0.0.skill", "abd-skills-v1.0.0.zip"):
                with zipfile.ZipFile(output / archive_name) as archive:
                    members.extend(archive.namelist())
            forbidden = [
                name
                for name in members
                if "__pycache__" in name.split("/") or name.endswith((".pyc", ".pyo"))
            ]
            self.assertEqual(forbidden, [])

    def test_ignores_symlinks_inside_bytecode_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            outside = root / "secret.txt"
            outside.write_text("secret\n", encoding="utf-8")
            cache = root / "skills" / "abd-alpha" / "__pycache__"
            cache.mkdir()
            try:
                (cache / "link.pyc").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not supported")

            build_packages(root, root / "dist", "v1.0.0")

            with zipfile.ZipFile(root / "dist" / "abd-alpha-v1.0.0.skill") as archive:
                self.assertEqual(
                    [name for name in archive.namelist() if "__pycache__" in name.split("/")],
                    [],
                )
```

The second test locks in the spec's deliberate side effect: filtering happens **before** the symlink check, so a symlink inside `__pycache__` is silently excluded instead of raising `PackagingError`. The existing `test_rejects_symlinked_source_outside_skill` (non-ignorable paths still raise) must stay green.

- [x] **Step 2: Run the new tests to verify they fail**

```bash
python3 -m unittest tests.test_package_skills.PackageSkillsTests.test_excludes_bytecode_artifacts_from_archives tests.test_package_skills.PackageSkillsTests.test_ignores_symlinks_inside_bytecode_directories -v
```

Expected: BOTH fail — the first with a non-empty `forbidden` list containing `abd-alpha/scripts/__pycache__/x.cpython-312.pyc` (and the `.pyo`), the second with `PackagingError: ... symlink source is not allowed` (or skip where symlinks are unsupported).

- [x] **Step 3: Implement the bytecode filter**

In `scripts/package_skills.py`, replace the current `source_files` (L33-39):

```python
def source_files(skill: Path) -> list[Path]:
    paths = list(skill.rglob("*"))
    for path in paths:
        if path.is_symlink():
            relative = path.relative_to(skill).as_posix()
            raise PackagingError(f"{skill.name}: symlink source is not allowed: {relative}")
    return sorted((path for path in paths if path.is_file()), key=lambda path: path.as_posix())
```

with:

```python
def _is_ignorable(path: Path, skill: Path) -> bool:
    parts = path.relative_to(skill).parts
    return "__pycache__" in parts or path.suffix in (".pyc", ".pyo")


def source_files(skill: Path) -> list[Path]:
    paths = [path for path in skill.rglob("*") if not _is_ignorable(path, skill)]
    for path in paths:
        if path.is_symlink():
            relative = path.relative_to(skill).as_posix()
            raise PackagingError(f"{skill.name}: symlink source is not allowed: {relative}")
    return sorted((path for path in paths if path.is_file()), key=lambda path: path.as_posix())
```

Nothing else changes. This is a deliberately narrow hardcoded filter (YAGNI — no `.gitignore` engine).

- [x] **Step 4: Run the new tests to verify they pass**

```bash
python3 -m unittest tests.test_package_skills.PackageSkillsTests.test_excludes_bytecode_artifacts_from_archives tests.test_package_skills.PackageSkillsTests.test_ignores_symlinks_inside_bytecode_directories -v
```

Expected: PASS (or skip for the symlink test on platforms without symlinks).

- [x] **Step 5: Run the roadmap RM-002 archive-inspection proof**

```bash
env -u PYTHONDONTWRITEBYTECODE python3 -m unittest discover -s tests -v
tmp=$(mktemp -d); env -u PYTHONDONTWRITEBYTECODE python3 scripts/package_skills.py --version v0.0.0 --output "$tmp/dist" && python3 -c "from pathlib import Path; import sys, zipfile; names = [name for archive in Path(sys.argv[1]).glob('*.skill') for name in zipfile.ZipFile(archive).namelist()]; forbidden = [name for name in names if '__pycache__' in name.split('/') or name.endswith(('.pyc', '.pyo'))]; assert not forbidden, forbidden" "$tmp/dist"; status=$?; rm -rf "$tmp"; exit $status
```

Expected: unittest `OK`; the packaging block prints the artifact paths and exits 0 (run `echo $?` to confirm).

- [x] **Step 6: Run the full regression trio**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

Expected: `OK`; `Validated 1 skill(s).`; `Packaging dry run passed.`

- [x] **Step 7: Commit**

```bash
git add scripts/package_skills.py tests/test_package_skills.py
git commit -m "fix: exclude __pycache__ bytecode from packaged skill archives

RM-002 / AUD-CORE-001: filter __pycache__ dirs and .pyc/.pyo files out
of source_files() before the symlink check, so bytecode never reaches
per-skill .skill archives or the collection ZIP regardless of
PYTHONDONTWRITEBYTECODE."
```

Append the sign-off trailer per Global Constraints (resolve the model name at commit time).

---

### Task 3: RM-003 — Disclose unverified identity resolution in jira dry-run

**Files:**
- Modify: `skills/abd-jira-cloud/scripts/jira.py:137-152` (`request`), `:437-451` (`cmd_assign`), `:454-477` (`cmd_watch`)
- Modify: `skills/abd-jira-cloud/SKILL.md:69-70` and `:78-79`
- Test: `tests/test_jira_cli.py` (new class + one fake signature update in `CommandBehaviorTests.invoke`)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `request(method, path, cfg, query=None, body=None, dry_run=False, unverified_identity=False)` — new trailing keyword arg. When `dry_run and unverified_identity`, the emitted preview object carries top-level `"identity_resolution": "not verified in dry-run"`. Contract: caveat present ⟺ dry-run AND email-resolved identity (covers `assign --email`, `watch --email`, `watch --remove --email`). Live behavior unchanged.

- [x] **Step 1: Write the failing test**

Append to `tests/test_jira_cli.py` (before the `if __name__` block; all needed imports already exist in the file):

```python
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
```

The `HTTP_OPENER.open` mock raising `AssertionError` proves dry-run makes no network call at all — which subsumes "no `/user/search` call".

- [x] **Step 2: Run the new test to verify it fails**

```bash
python3 -m unittest tests.test_jira_cli.DryRunIdentityResolutionTests.test_email_assign_and_watch_dry_runs_are_not_mistaken_for_verified_identity_resolution -v
```

Expected: FAIL/ERROR on the flagged cases with `KeyError: 'identity_resolution'` (the preview object has no such key yet). Unflagged subtests pass — that is fine; the test method as a whole must fail.

- [x] **Step 3: Implement disclosure in `request()`, `cmd_assign`, `cmd_watch`**

In `skills/abd-jira-cloud/scripts/jira.py`:

3a. Change the `request` signature (L137) and its dry-run branch (L150-152) from:

```python
def request(method, path, cfg, query=None, body=None, dry_run=False):
```

```python
    if dry_run:
        emit({"method": method, "url": url, "headers": headers, "body": body})
        return None
```

to:

```python
def request(method, path, cfg, query=None, body=None, dry_run=False, unverified_identity=False):
```

```python
    if dry_run:
        preview = {"method": method, "url": url, "headers": headers, "body": body}
        if unverified_identity:
            preview["identity_resolution"] = "not verified in dry-run"
        emit(preview)
        return None
```

3b. Replace `cmd_assign` (L437-451) with:

```python
def cmd_assign(args, cfg):
    email_resolved = False
    if args.unassign:
        account_id = None
    elif args.account_id:
        account_id = args.account_id
    elif args.email:
        account_id = resolve_account_id(cfg, args.email, dry_run=args.dry_run)
        email_resolved = args.dry_run
    else:
        raise JiraError("Pass one of --email, --account-id, or --unassign.")
    res = request(
        "PUT", issue_path(args.key, "/assignee"), cfg,
        body={"accountId": account_id}, dry_run=args.dry_run,
        unverified_identity=email_resolved,
    )
    if res is not None:  # 204 on success
        emit({"assigned": args.key, "accountId": account_id})
```

3c. Replace `cmd_watch` (L454-477) with:

```python
def cmd_watch(args, cfg):
    email_resolved = False
    account_id = args.account_id
    if account_id is None and args.email:
        account_id = resolve_account_id(cfg, args.email, dry_run=args.dry_run)
        email_resolved = args.dry_run
    # Add-watcher takes the accountId as the RAW json body (a bare string),
    # not an object. Remove uses a query param instead.
    if args.remove:
        if account_id is None:
            raise JiraError("--remove needs --email or --account-id.")
        res = request(
            "DELETE", issue_path(args.key, "/watchers"), cfg,
            query={"accountId": account_id}, dry_run=args.dry_run,
            unverified_identity=email_resolved,
        )
        if res is not None:
            emit({"removed_watcher": account_id, "issue": args.key})
        return
    if account_id is None:
        raise JiraError("Pass --email or --account-id (or --remove to drop one).")
    res = request(
        "POST", issue_path(args.key, "/watchers"), cfg,
        body=account_id, dry_run=args.dry_run,
        unverified_identity=email_resolved,
    )
    if res is not None:
        emit({"added_watcher": account_id, "issue": args.key})
```

Detection is the explicit `email_resolved = args.dry_run` flag on the email-resolution branch — never string-sniff the `<accountId-resolved-from:...>` placeholder. `resolve_account_id()` itself is untouched (live path still raises on zero/multiple matches). The preview's `url`/`body` are unchanged — the caveat is a sibling top-level key only.

3d. `cmd_assign`/`cmd_watch` now always pass `unverified_identity=`, so update the fake in `tests/test_jira_cli.py` `CommandBehaviorTests.invoke` from:

```python
        def fake_request(method, path, cfg, query=None, body=None, dry_run=False):
```

to:

```python
        def fake_request(method, path, cfg, query=None, body=None, dry_run=False, unverified_identity=False):
```

(the `calls` tuple it records stays the same).

- [x] **Step 4: Run the new test to verify it passes, plus the guarded invariants**

```bash
python3 -m unittest tests.test_jira_cli.DryRunIdentityResolutionTests.test_email_assign_and_watch_dry_runs_are_not_mistaken_for_verified_identity_resolution -v
python3 -m unittest tests.test_jira_cli -v
```

Expected: new test PASS; entire `test_jira_cli` module `OK` — in particular `test_account_resolution_is_exact_or_unambiguous`, `test_dry_run_redacts_token_and_emits_one_json_value`, `test_whoami_dry_run_emits_one_json_value`, `test_transition_dry_run_by_name_emits_one_json_value`, and `test_command_request_contracts` all still green.

- [x] **Step 5: Update `SKILL.md` to match the new behavior**

In `skills/abd-jira-cloud/SKILL.md`, make exactly two edits:

5a. Replace the dry-run note (L69-70):

```markdown
Dry-run a write when its scope or payload needs confirmation. Do not publish
dry-run output to shared logs because request bodies may contain issue content.
```

with:

```markdown
Dry-run a write when its scope or payload needs confirmation. A dry-run of
`assign`/`watch` with `--email` does not verify identity resolution: the
preview carries `identity_resolution: "not verified in dry-run"`, and the
email is resolved — or rejected as unmatched or ambiguous — only on the live
run. Do not publish dry-run output to shared logs because request bodies may
contain issue content.
```

5b. Replace the constraint bullet (L78-79):

```markdown
- Users are identified by `accountId`. Email lookup must resolve exactly or
  unambiguously; otherwise request an account ID.
```

with:

```markdown
- Users are identified by `accountId`. On live runs, email lookup must resolve
  exactly or unambiguously; otherwise request an account ID. Dry-run skips the
  lookup and marks the preview with `identity_resolution`.
```

Operating rule 2 (L21-23) stays unchanged — the two edits above carry the disclosure.

- [x] **Step 6: Run the full regression trio**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

Expected: `OK`; `Validated 1 skill(s).`; `Packaging dry run passed.`

- [x] **Step 7: Commit**

```bash
git add skills/abd-jira-cloud/scripts/jira.py skills/abd-jira-cloud/SKILL.md tests/test_jira_cli.py
git commit -m "fix: disclose unverified identity resolution in jira dry-run previews

RM-003 / AUD-JIRA-001: dry-run assign/watch by --email now emits a
top-level identity_resolution caveat in the (single) preview object;
--account-id/--unassign paths carry no caveat, live resolution is
unchanged, and SKILL.md documents the dry-run limitation."
```

Append the sign-off trailer per Global Constraints (resolve the model name at commit time).

---

### Task 4: Cross-cutting verification (evidence before claims)

**Files:**
- None modified — verification only.

**Interfaces:**
- Consumes: all three prior tasks committed.
- Produces: pasted command output proving all acceptance criteria; the task report to the human.

- [x] **Step 1: Run the full regression set and show output**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

Expected: `OK` (test count higher than the pre-plan baseline by 3 new tests); `Validated 1 skill(s).`; `Packaging dry run passed.` Paste actual output — do not summarize it away.

- [x] **Step 2: Re-run both roadmap focused assertions**

Run the Task 1 Step 5 regex command and the Task 2 Step 5 archive-inspection command once more, verbatim. Expected: both exit 0.

- [x] **Step 3: Confirm clean tree and report**

```bash
git status --short
git log --oneline -4
```

Expected: no unstaged changes to source/test/workflow files; the three remediation commits on top. Report to the human: implementation complete, and the remaining human-only step is pushing and observing a green CI run on the repinned actions (Task 1 Step 8).
