# Audit Remediation Design

> **Status: Implemented (2026-07-11).** All three remediations landed on `main`
> via merge commit `a65d327` (commits `d211cf3` RM-001, `5a3d1bd` RM-002,
> `64978c3` RM-003). Final whole-branch review: Ready to merge, no
> Critical/Important findings. Outstanding: observe a green CI run on the
> repinned action refs after push (see plan Task 1 Step 8).

## Purpose

Remediate the three confirmed "Worth considering" findings from
`docs/audits/2026-07-10-codebase-audit.md`, operationalized as `RM-001`–`RM-003`
in `docs/audits/2026-07-10-remediation-roadmap.md`. Each finding is small,
independently scoped, and touches disjoint files. This spec covers all three in a
single implementation cycle.

The three findings:

- **RM-001 / AUD-REL-001** — CI and release workflows pin third-party GitHub
  Actions by floating major-version tag instead of commit SHA.
- **RM-002 / AUD-CORE-001** — the packager ships stale `__pycache__` bytecode
  into published `.skill` archives.
- **RM-003 / AUD-JIRA-001** — dry-run `assign`/`watch` by `--email` fakes
  identity resolution with a placeholder and cannot surface ambiguity, giving an
  agent false confidence that contradicts `SKILL.md`'s dry-run-ambiguous-writes
  rule.

## Approach

Three surgical, independent edits — no new shared abstraction. The roadmap
confirms the fixes touch disjoint files (`.github/workflows/*.yml` +
`.github/dependabot.yml`, `scripts/package_skills.py`,
`skills/abd-jira-cloud/scripts/jira.py` + `SKILL.md`) with no shared state.
Test-driven: each behavioral change gets a failing test first, then the fix, then
the roadmap's verification commands run with output shown.

Implementation order is RM-001 → RM-002 → RM-003 (harden the release pipeline
first, then packaging hygiene, then the isolated skill fix). The order is for
tidiness; the items are independent and carry no cross-dependency.

Out of scope: the audit and roadmap documents themselves, and the uncommitted
`docs/superpowers/plans/2026-07-11-codebase-audit.md` audit-process artifact.
No unrelated refactoring.

## RM-001 — Pin GitHub Actions to commit SHAs

### Change

In both `.github/workflows/ci.yml` and `.github/workflows/release.yml`, replace
each floating action reference with a full 40-character commit SHA plus a
version comment:

- `actions/checkout@v4` → `actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0`
- `actions/setup-python@v5` → `actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6.3.0`

The SHAs above were resolved from the upstream release tags via the GitHub API
(`repos/actions/checkout/git/ref/tags/v7.0.0` and
`repos/actions/setup-python/git/ref/tags/v6.3.0`). At implementation time,
re-confirm these are still the latest `v7.x.x` (checkout) and `v6.3.x`
(setup-python) releases and re-resolve the SHA from the tag if a newer patch has
shipped. Pin to a published, battle-tested release — never a release candidate.

Note that these pins are also **major-version upgrades** (checkout v4 → v7,
setup-python v5 → v6), not a pure pin-in-place of the versions currently in use.
Before implementing, skim both upstream release notes for breaking changes
relevant to these workflows (runner/Node runtime requirements, changed default
inputs). Both workflows use each action with default or trivial inputs
(`python-version: "3.12"` only), so no breakage is expected — but a green CI run
on the repinned workflow is required evidence, and if the major upgrade does
break, fall back to pinning the latest release of the currently-used major
instead (the finding is about pinning, not upgrading).

### New file: `.github/dependabot.yml`

Configure Dependabot's `github-actions` ecosystem so the SHA pins receive
review-gated update PRs, with a cooldown so a freshly-published (and potentially
bad, later-yanked) version is not proposed until it has been public for a week:

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

Dependabot bumps arrive as pull requests, never auto-merged; each is
human-reviewed and must pass CI before reaching `main`. SHA-pinning makes the
pinned commit immutable and the bump diff reviewable — it does not by itself
vet a version, it guarantees a human sees every version change.

### Security rationale (why SHA + cooldown + review gate)

- **Pinning now:** the SHA is verified to belong to the claimed release tag of
  the real first-party upstream action, so the workflow runs exactly the commit
  a human vetted and a moved tag cannot silently repoint it.
- **Future bumps:** the 7-day cooldown avoids the window in which a bad release
  is still public before being yanked; the PR-only, review-gated flow means no
  new version enters the pipeline without human review and passing CI.

### Acceptance criteria

- Every `uses: actions/...` reference in `ci.yml` and `release.yml` is a full
  40-hex commit SHA with a `# vN.N.N` version comment.
- `.github/dependabot.yml` configures the `github-actions` ecosystem at
  `directory: "/"` with a recurring `weekly` schedule and a `cooldown` block.
- CI and release workflows continue to pass after repinning.

### Verification

- Roadmap RM-001 regex assertion (all `uses: actions/...` are `@<40-hex>` with a
  `vN.N.N` comment; dependabot.yml has the `github-actions` ecosystem, `/`
  directory, and a `daily|weekly|monthly` schedule). The added `cooldown` block
  does not affect this assertion.
- `python3 -m unittest discover -s tests -v`
- `python3 scripts/validate_skills.py`
- `python3 scripts/package_skills.py --version v0.0.0 --dry-run`

Verification limitation: `release.yml` triggers only on `v*.*.*` tag pushes, so
it cannot be exercised end-to-end before the next release. Its action steps
(checkout, setup-python) are identical to `ci.yml`'s, so a passing CI run on the
repinned refs is the accepted proxy; the "release workflow continues to pass"
criterion is finally confirmed by the first tagged release after merge.

## RM-002 — Exclude `__pycache__`/`*.pyc` from packaged archives

### Change

In `scripts/package_skills.py`, `source_files()` (currently L33-39) walks
`skill.rglob("*")` and collects every regular file, so any bytecode cache present
on disk at packaging time leaks into the archive. Add a bytecode filter that
drops ignorable paths **before** both the symlink check and the file collection,
so `__pycache__` directories and compiled files never reach the symlink check or
`read_bytes()`, regardless of whether `PYTHONDONTWRITEBYTECODE` is set:

```python
def _is_ignorable(path: Path, skill: Path) -> bool:
    parts = path.relative_to(skill).parts
    return "__pycache__" in parts or path.suffix in (".pyc", ".pyo")
```

This is a deliberately narrow, hardcoded filter for bytecode artifacts — not a
general `.gitignore`-driven exclusion engine (YAGNI; the finding is scoped to
`__pycache__`/`.pyc`/`.pyo`).

Filtering **before** the symlink check has a deliberate side effect: a symlink
inside a `__pycache__` directory (or one named `*.pyc`/`*.pyo`) no longer raises
`PackagingError` — it is silently excluded along with the rest of the ignorable
path. This is intended: ignorable paths are wholly outside packaging concern,
and the symlink policy exists to keep symlinks out of *archives*, which the
filter already guarantees for these paths. The existing
`test_rejects_symlinked_source_outside_skill` behavior for non-ignorable paths
must remain unchanged.

Both archive builders (`expected_individual_entries` and
`expected_collection_entries`) funnel through `source_files()`, so the single
filter covers the per-skill `.skill` archives and the collection ZIP alike — do
not add per-builder filtering.

### Acceptance criteria

- `source_files()` skips `__pycache__` directories and `*.pyc`/`*.pyo` files
  whether or not `PYTHONDONTWRITEBYTECODE` is set.
- The roadmap's fresh-clone, `env -u PYTHONDONTWRITEBYTECODE`, real
  test/validate/package workflow-order proof yields no `__pycache__`/`.pyc`/
  `.pyo` members in any packaged skill (`generated_members == []`).
- The existing packaging test suite continues to pass.

### Testing (TDD)

Add a test in `tests/test_package_skills.py` that plants both a
`__pycache__/x.cpython-312.pyc` file and a loose `stale.pyo` file under a skill
directory, runs packaging, and asserts no member of **either** the per-skill
`.skill` archive **or** the collection ZIP contains a `__pycache__` path
component or ends in `.pyc`/`.pyo`. Write it failing against current behavior
first.

### Verification

- `env -u PYTHONDONTWRITEBYTECODE python3 -m unittest discover -s tests -v`
- Roadmap RM-002 archive-inspection command: package to a temp dir with
  `env -u PYTHONDONTWRITEBYTECODE` and assert no packaged `.skill` archive
  contains a `__pycache__` component or a `.pyc`/`.pyo` member.
- `python3 -m unittest discover -s tests -v`
- `python3 scripts/validate_skills.py`
- `python3 scripts/package_skills.py --version v0.0.0 --dry-run`

## RM-003 — Disclose unverified identity resolution in dry-run

### Change

`resolve_account_id()` (`jira.py:209-232`) short-circuits under `--dry-run`
(L215-216), returning the placeholder `<accountId-resolved-from:EMAIL>` with no
`/user/search` call and no ambiguity check. `cmd_assign` (L437-451) and
`cmd_watch` (L454-477) then emit a clean-looking preview, so a dry-run
`assign`/`watch` by `--email` always appears to succeed even when the email is
ambiguous or unmatched — contradicting the false confidence `SKILL.md`'s dry-run
guidance is meant to prevent.

Chosen remediation: **disclose, do not resolve.** Dry-run stays fully offline
(no network call), consistent with the existing dry-run contract. When a dry-run
`assign`/`watch` resolves identity from `--email` (the faked-placeholder path),
the emitted dry-run JSON includes an explicit field:

```
"identity_resolution": "not verified in dry-run"
```

The caveat appears **only** when identity was actually faked — i.e. dry-run +
`--email` resolution. This covers all three email-resolving paths: `assign
--email`, `watch --email` (add), and `watch --remove --email` (jira.py:456-457
resolves before the DELETE). The `--account-id` and `--unassign` paths need no
resolution and carry no caveat. Contract: **caveat present ⟺ dry-run AND
email-resolved identity.**

Placement: the field is a **top-level key of the dry-run preview object**
emitted by `request()` (a sibling of `method`/`url`/`headers`/`body`), not
injected into `body`. Two constraints force this: `watch` (add) sends the
accountId as a bare JSON string body and `watch --remove` carries it in a query
param, so there is no object body to annotate; and the preview's `url`/`body`
must stay faithful to what the live request would send. Emitting a second JSON
document is also ruled out — dry-run output is a single JSON value per request,
an invariant locked in by the existing
`test_dry_run_redacts_token_and_emits_one_json_value` /
`test_whoami_dry_run_emits_one_json_value` tests, and agents parse it as such.

Detection is explicit (the command tracks whether it took the email-resolution
branch under dry-run and passes that fact through to the preview emission), not
a fragile string-sniff of the placeholder value. Exact wiring is left to the
implementation plan; the observable contract above is fixed.

### `SKILL.md` update

Update the dry-run guidance (Operating rule 2 around L19-23 and/or the dry-run
note around L69) so it accurately states that dry-run previews of `--email`
`assign`/`watch` do **not** verify identity resolution — the `identity_resolution`
field flags this, and identity is checked only on the live run. Also check the
Jira-specific constraint "Email lookup must resolve exactly or unambiguously"
(around L78-79) — it reads as if resolution is always enforced; qualify it for
dry-run if the chosen wording elsewhere doesn't already cover it.

### Acceptance criteria

- Dry-run `assign`/`watch` with `--email` — including `watch --remove --email`
  — emits `identity_resolution: "not verified in dry-run"` as a top-level key of
  the single dry-run preview object, and makes no `/user/search` call.
- Dry-run `assign`/`watch` with `--account-id` (and `--unassign`) does **not**
  emit the caveat field.
- Dry-run output remains exactly one JSON value per previewed request (existing
  `*_emits_one_json_value` tests stay green), and the preview's `url` and `body`
  are unchanged from current behavior.
- `SKILL.md` accurately describes the `--email` dry-run behavior.
- The live (non-dry-run) resolution path is unchanged and still raises on zero or
  multiple matches (existing
  `test_account_resolution_is_exact_or_unambiguous` stays green).
- The existing `jira.py` test suite continues to pass.

### Testing (TDD)

Add `DryRunIdentityResolutionTests.test_email_assign_and_watch_dry_runs_are_not_mistaken_for_verified_identity_resolution`
in `tests/test_jira_cli.py`. It asserts:

- dry-run `assign --email`, `watch --email`, and `watch --remove --email`
  output carry `identity_resolution: "not verified in dry-run"` as a top-level
  key of the (single) preview object and trigger no `/user/search` call, and
- dry-run `--account-id` output does **not** carry the field.

Write it failing against current behavior first.

### Verification

- `python3 -m unittest tests.test_jira_cli.DryRunIdentityResolutionTests.test_email_assign_and_watch_dry_runs_are_not_mistaken_for_verified_identity_resolution`
- `python3 -m unittest discover -s tests -v`
- `python3 scripts/validate_skills.py`
- `python3 scripts/package_skills.py --version v0.0.0 --dry-run`

## Cross-cutting verification

After all three items are implemented, run the full regression set and show
output (evidence before claims):

- `python3 -m unittest discover -s tests -v`
- `python3 scripts/validate_skills.py`
- `python3 scripts/package_skills.py --version v0.0.0 --dry-run`

## Traceability

| Spec item | Roadmap | Audit finding | Affected files |
|---|---|---|---|
| RM-001 | RM-001 | AUD-REL-001 | `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `.github/dependabot.yml` |
| RM-002 | RM-002 | AUD-CORE-001 | `scripts/package_skills.py`, `tests/test_package_skills.py` |
| RM-003 | RM-003 | AUD-JIRA-001 | `skills/abd-jira-cloud/scripts/jira.py`, `skills/abd-jira-cloud/SKILL.md`, `tests/test_jira_cli.py` |
