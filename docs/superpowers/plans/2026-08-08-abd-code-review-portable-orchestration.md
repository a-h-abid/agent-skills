# Portable Code-Review Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Checkbox discipline:** Change a step to `- [x]` only after its stated verification succeeds. Do not batch-mark later steps.

**Goal:** Make `abd-code-review` use bounded, cost-efficient subagent orchestration on Codex while preserving first-class Claude Code support and the existing evidence-backed review quality.

**Architecture:** Keep review policy and portable worker roles in `SKILL.md`, then load exactly one small runtime adapter for Codex or Claude Code. The primary agent retains target discovery, tooling, whole-change judgment, evidence rechecks, deduplication, severity, and the final verdict; workers only perform read-only evidence collection or bounded concern reviews.

**Tech Stack:** Markdown Agent Skills, Python 3.12 standard-library `unittest`, repository skill validator and deterministic packaging dry run, Codex collaboration tools, Claude Code Agent tool.

## Global Constraints

- Preserve the fourteen review layers, severity model, confidence tags, coverage overview, and final output format.
- Use portable terms in `SKILL.md`: **primary agent**, **evidence scout**, and **reviewer worker**.
- Read exactly one runtime adapter when worker tooling is available; use the inline fallback otherwise.
- Small reviews use no workers; medium reviews use at most one justified scout; large reviews use two reviewer workers by default and a third only for a genuinely separate high-risk concern.
- Never exceed runtime-reported available worker capacity; the primary agent counts against Codex concurrency.
- Workers are read-only, do not delegate, do not rerun broad tooling, and do not issue the final verdict.
- Use fresh task-local Codex context where supported; do not hard-code model versions.
- Keep all changes dependency-free and compatible with the existing package builder.
- Do not modify stack-specific review guidance except where a portable orchestration cross-reference requires it.
- Do not commit, push, pull, fetch, merge, squash, or rebase during execution unless the user gives separate explicit authorization.
- Before claiming completion, invoke and follow `superpowers:verification-before-completion`.

## File Map

- Modify `skills/abd-code-review/SKILL.md`: portable sizing, runtime selection, bounded delegation, worker contract, fallback, and synthesis ownership.
- Create `skills/abd-code-review/references/runtime-codex.md`: exact Codex capacity, fresh-context, shared-workspace, dispatch, waiting, and follow-up rules.
- Create `skills/abd-code-review/references/runtime-claude-code.md`: exact Claude Code evidence-scout and reviewer-worker mappings.
- Create `tests/test_abd_code_review_skill.py`: deterministic contract tests for the portable core and both adapters.
- Modify `tests/test_repository_layout.py`: make repository layout validation branch-neutral while preserving nested Git-root detection.
- Modify `skills/abd-code-review/README.md`: document adaptive delegation and runtime compatibility without exposing internal prompt detail.
- Modify this plan during execution only to mark verified checkboxes.

---

### Task 0: Make Repository Layout Validation Branch-Neutral

**Files:**
- Modify: `tests/test_repository_layout.py:61-74`

**Interfaces:**
- Preserves: detection of nested `.git` roots.
- Removes: the unrelated requirement that the test process must run on the `main` branch.

- [x] **Step 1: Rename the test to describe the retained invariant**

Rename `test_repository_has_one_git_root_on_main` to `test_repository_has_one_git_root`.

- [x] **Step 2: Remove only the current-branch assertion**

Delete the `git branch --show-current` subprocess and `self.assertEqual(branch, "main")`. Keep the nested `.git` scan and `self.assertEqual(nested, [])` unchanged.

- [x] **Step 3: Verify the focused test passes on the feature branch**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_repository_layout.RepositoryLayoutTests.test_repository_has_one_git_root -v
```

Expected: PASS while checked out on `feat/abd-code-review-portable-orchestration`.

- [x] **Step 4: Verify the complete clean baseline**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

Expected: all 57 baseline tests pass; validator reports `Validated 2 skill(s).`; packaging reports `Packaging dry run passed.`

---

### Task 1: Portable Orchestration Contract and Runtime Adapters

**Files:**
- Create: `tests/test_abd_code_review_skill.py`
- Modify: `skills/abd-code-review/SKILL.md:41-82`
- Modify: `skills/abd-code-review/SKILL.md:120-122`
- Create: `skills/abd-code-review/references/runtime-codex.md`
- Create: `skills/abd-code-review/references/runtime-claude-code.md`

**Interfaces:**
- Produces: portable roles `primary agent`, `evidence scout`, and `reviewer worker`.
- Produces: runtime routing from `SKILL.md` to exactly one adapter.
- Produces: Codex adapter contract using `spawn_agent`, `wait_agent`, task-local context, and shared-workspace safeguards.
- Produces: Claude Code adapter contract using `Explore` for bounded scouting and `general-purpose` for deep review bundles.
- Consumes: existing Review Principles, Evidence-gathering moves, stack references, Layers 1-14, and Output Format unchanged.

- [x] **Step 1: Run fresh-context baseline scenarios against the current skill**

Use fresh reviewer agents with no design or expected-answer leakage. Each receives the current skill path and one scenario below. Ask for an execution allocation only; do not ask it to critique the skill.

Prompt prefix:

```text
Use the abd-code-review skill at
/home/abid/dev-projects/abd/agent-skills/skills/abd-code-review/SKILL.md.
You are preparing to review the change described below. Do not edit files and do
not perform the review yet. Return the exact worker allocation and dispatch
strategy you would use, what the primary agent retains, and what context each
worker receives.
```

Run these scenarios:

```text
SMALL: An 85-line Python bug fix in two files with one regression test. No auth,
schema, infrastructure, concurrency, or external integration changes. Worker
capacity is available.

MEDIUM: A 460-line Node/TypeScript endpoint change across eight files. The main
review needs one independent authorization-middleware and call-site sweep.
Everything else fits in the primary context. Worker capacity is available.

LARGE: A 2,200-line PHP/Lumen change touching authorization, a migration, a
queue consumer, Redis idempotency, CI, and tests. The runtime is Codex with room
for at most three workers in addition to the primary agent.

FALLBACK: A 1,100-line Go service diff must be reviewed in a runtime with no
subagent-dispatch capability.
```

Record in the execution notes for each response: worker count, runtime-specific terms used, duplicated skill/diff content, capacity handling, read-only instruction, primary-agent responsibilities, and fallback behavior. Do not edit the skill before all four baselines are observed.

Expected baseline: at least one concrete failure matching the current text, such as Claude-specific `Explore` terminology in a portable path, four fixed large-review bundles despite Codex capacity, missing task-local context guidance, or missing shared-workspace safeguards. If every scenario already satisfies the proposed contract, stop and report that the planned change lacks a demonstrated behavioral need.

- [x] **Step 2: Write deterministic failing contract tests**

Create `tests/test_abd_code_review_skill.py` with:

```python
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "abd-code-review" / "SKILL.md"
CODEX = ROOT / "skills" / "abd-code-review" / "references" / "runtime-codex.md"
CLAUDE = ROOT / "skills" / "abd-code-review" / "references" / "runtime-claude-code.md"


class CodeReviewOrchestrationTests(unittest.TestCase):
    def test_core_routes_to_runtime_adapters_and_uses_portable_roles(self) -> None:
        text = SKILL.read_text(encoding="utf-8")

        for role in ("primary agent", "evidence scout", "reviewer worker"):
            self.assertIn(role, text.lower())
        self.assertIn("`references/runtime-codex.md`", text)
        self.assertIn("`references/runtime-claude-code.md`", text)
        self.assertIn("read exactly one", text.lower())
        self.assertNotIn("Explore subagents", text)
        self.assertNotIn("general-purpose reviewer subagents", text)

    def test_core_has_bounded_cost_aware_sizing(self) -> None:
        text = SKILL.read_text(encoding="utf-8").lower()

        self.assertRegex(text, r"small[^\n]*no (?:subagents|workers)")
        self.assertRegex(text, r"medium[^\n]*at most one[^\n]*evidence scout")
        self.assertIn("two reviewer workers by default", text)
        self.assertIn("third", text)
        self.assertIn("available worker capacity", text)

    def test_codex_adapter_uses_fresh_context_and_shared_workspace_safety(self) -> None:
        text = CODEX.read_text(encoding="utf-8")

        for tool in ("spawn_agent", "wait_agent"):
            self.assertIn(tool, text)
        self.assertIn('fork_turns="none"', text)
        self.assertIn("primary agent occupies", text.lower())
        self.assertIn("shared workspace", text.lower())
        self.assertIn("must not edit", text.lower())
        self.assertIn("must not spawn", text.lower())
        self.assertIsNone(
            re.search(r"\b(?:gpt|claude)-\d|\b(?:haiku|sonnet|opus)\b", text, re.IGNORECASE)
        )

    def test_claude_adapter_preserves_native_worker_types(self) -> None:
        text = CLAUDE.read_text(encoding="utf-8")

        self.assertIn("Explore", text)
        self.assertIn("general-purpose", text)
        self.assertIn("read-only", text.lower())
        self.assertIn("parallel", text.lower())
        self.assertIn("primary agent", text.lower())

    def test_every_orchestration_document_keeps_verdict_with_primary(self) -> None:
        for path in (SKILL, CODEX, CLAUDE):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("final verdict", text)
                self.assertIn("primary agent", text)


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 3: Run the contract tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_abd_code_review_skill -v
```

Expected: FAIL because both runtime adapter files are absent and the core still contains Claude-specific worker terms. Confirm failures express the intended missing contract, not a syntax or import error.

- [x] **Step 4: Replace the sizing and delegation section with the portable core**

In `skills/abd-code-review/SKILL.md`, replace the current `### Size the review` and `### Executing with subagents (large diffs)` sections, through the re-review paragraph immediately before `### Leverage the project's own tooling first`, with this structure and wording:

```markdown
### Size the review and choose execution mode

Size, risk, separability, and available worker capacity determine who does the
reading. A **primary agent** always owns the target, intent, change map, tooling,
whole-change judgment, synthesis, severity, and final verdict. An **evidence
scout** performs one bounded search. A **reviewer worker** performs an assigned
read-only concern-and-file review.

If worker tooling is available, read exactly one matching runtime adapter before
dispatching:

- Codex collaboration tools: `references/runtime-codex.md`
- Claude Code Agent tool: `references/runtime-claude-code.md`

If neither adapter matches or dispatch is unavailable, review inline in
risk-ranked order. List anything that received lighter scrutiny in the coverage
overview.

- **Small diff (< ~150 lines): no workers.** Review everything inline. A clean
  20-line fix deserves a short review, not orchestration overhead.
- **Medium diff (~150-800 lines): at most one evidence scout.** The primary agent
  performs the full review. Dispatch only one bounded, independent search when
  it materially saves context or elapsed time, such as a call-site sweep, schema
  check, authorization-middleware hunt, or dead-code search.
- **Large diff (> ~800 lines): two reviewer workers by default.** First rank files
  by risk. Add a third reviewer worker only when a genuinely separate high-risk
  concern cannot be combined cleanly with either existing bundle. Never exceed
  available worker capacity. Migrations, auth/authz, money, concurrency, and
  external integrations get deep review; mechanical/generated/rename-only files
  may get a skim, disclosed in the coverage overview.

Line count is a guide, not an override: keep a large mechanical diff inline or
escalate a smaller security- or migration-heavy change when its independent risk
surfaces justify it.

### Build concern bundles

Delegation outsources reading, not judgment. After Step 0 and one tooling run,
bundle the concerns actually present in the change by shared files, data flow,
and risk. Combine or omit these common groupings rather than dispatching an
empty worker:

- **Correctness & contracts** — Layers 1, 8, 11
- **Security & privacy** — Layers 2, 13
- **Data, deploy & config** — Layers 3, 4, 10
- **Production behavior** — Layers 5, 6, 7, 9

Keep Layers 12 and 14 with the primary agent because architecture fit and
what-is-missing require the whole-change view. On a large re-review, prior-finding
status may become one bundle only when capacity remains after new high-risk code
is covered.

### Worker input and output contract

Give each worker only:

1. The target as commands to run plus its risk-ranked assigned files.
2. A 3-5 line intent and change-map summary.
3. Paths to this skill's Review Principles, Evidence-gathering moves, assigned
   layers, and matching stack references.
4. Tooling leads relevant to its assignment.
5. This findings-only contract: `file:line` · severity suggestion · confidence ·
   defect and consequence · evidence actually read · suggested fix, followed by
   a short couldn't-inspect list. A clean slice returns `no findings`.

Use paths instead of pasted diffs or duplicated skill prose whenever workers can
read the repository. Every worker is read-only: it must not edit files, delegate
again, rerun the broad tooling, write the overview, or issue the final verdict.

The primary agent deduplicates reports by root cause, re-reads cited evidence for
every proposed Blocking finding, resolves conflicting reports from source,
recalibrates severity with the whole-change view, records inspection gaps, and
writes the Output Format. If a worker fails, cover its high-risk gap inline or
disclose it; never silently drop the slice.
```

Keep `### Leverage the project's own tooling first` and all subsequent review layers intact. Retain its existing rule that tooling runs once and worker bundles receive only relevant leads.

- [x] **Step 5: Create the Codex runtime adapter**

Create `skills/abd-code-review/references/runtime-codex.md`:

```markdown
# Codex Review Orchestration

Read this adapter only when Codex collaboration tools are available. The portable
policy and output contract remain in `../SKILL.md`.

## Capacity and cost

Read the runtime-reported concurrency limit and current live-agent state when
available. The primary agent occupies one slot; existing live workers occupy
others. Never dispatch beyond the remaining capacity. If capacity is unknown,
use at most two concurrent workers.

Prefer fewer cohesive bundles over many narrow workers. Omit model and reasoning
overrides by default so workers inherit the runtime's supported configuration.
If the user or runtime supplies an explicit model policy, use its least costly
capable option for a bounded evidence scout and reserve stronger reasoning for a
high-risk cross-file reviewer. Never invent or hard-code a model identifier.

## Dispatch

Spawn independent workers without waiting between dispatches. Use
`spawn_agent` with `fork_turns="none"` so each worker receives fresh task-local
context rather than the entire conversation. Give every worker:

- the absolute working directory and skill path;
- its role, target commands, assigned files, and relevant stack references;
- the short intent/change summary and relevant tooling leads;
- the portable findings-only output contract.

Codex agents share a workspace. Every review prompt must say: **You are read-only:
you must not edit files, create artifacts, change Git state, or spawn subagents.**
The primary agent alone writes the final verdict.

Use stable task names based on concern, such as `review_auth_contracts` or
`scout_order_calls`. Do not paste the diff when the worker can run the target
command itself.

## Collection and repair

Use `wait_agent` with a practical interval while workers run. When a report lacks
one specific piece of cited evidence, send one focused follow-up to the same
worker; do not restart the full review. If the worker fails, conflicts with
another report, or touches the workspace, the primary agent verifies the slice
inline and reports any resulting coverage gap or mutation.
```

- [x] **Step 6: Create the Claude Code runtime adapter**

Create `skills/abd-code-review/references/runtime-claude-code.md`:

```markdown
# Claude Code Review Orchestration

Read this adapter only when Claude Code's Agent tool is available. The portable
policy and output contract remain in `../SKILL.md`.

## Worker mapping

- Map a bounded evidence scout to a read-only `Explore` worker.
- Map a multi-file reviewer worker to a `general-purpose` worker with an explicit
  read-only instruction.

Dispatch independent assignments in parallel in one tool-call response, within
the available worker limit. Prefer two cohesive large-review bundles; add a third
only under the portable high-risk rule.

## Prompt and ownership

Give each worker the repository path, target commands, assigned files, short
intent/change summary, relevant tooling leads, and paths to the exact skill
sections and stack references it must read. Use paths instead of pasting diffs or
duplicating skill prose.

Every prompt states that the worker is read-only, must not edit files or delegate,
and returns only the portable findings contract. The primary agent runs broad
tooling once, resolves report conflicts against source, verifies proposed
Blocking evidence, performs whole-change Layers 12 and 14, and writes the final
verdict.
```

- [x] **Step 7: Remove the remaining runtime-specific core wording**

In `skills/abd-code-review/SKILL.md`:

- Keep the existing tooling-once rule, but refer to `workers` rather than `reviewer bundles` if needed for grammatical consistency.
- Change the stack-detection delegation sentence to: `When delegating, the primary agent detects the stack to scope bundles and assign reference paths; each worker reads only its own references.`
- Search the portable core for `Explore`, `general-purpose`, `spawn_agent`, `Agent tool`, and model names. Runtime mechanics must appear only in the matching adapter.

Run:

```bash
rg -n "Explore|general-purpose|spawn_agent|Agent tool|haiku|sonnet|opus|gpt-[0-9]|claude-[0-9]" skills/abd-code-review/SKILL.md
```

Expected: no matches.

- [x] **Step 8: Run focused tests and skill validation**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_abd_code_review_skill -v
python3 scripts/validate_skills.py
```

Expected: five orchestration tests pass; validator reports `Validated 2 skill(s).`

---

### Task 2: Fresh-Context Behavior Verification and Wording Refinement

**Files:**
- Modify if required: `skills/abd-code-review/SKILL.md`
- Modify if required: `skills/abd-code-review/references/runtime-codex.md`
- Modify if required: `skills/abd-code-review/references/runtime-claude-code.md`
- Test: `tests/test_abd_code_review_skill.py`

**Interfaces:**
- Consumes: the portable roles, adapters, size bands, worker contract, and synthesis contract from Task 1.
- Produces: observed compliance with bounded delegation, task-local prompts, read-only behavior, and primary-agent verdict ownership.

- [x] **Step 1: Micro-test the highest-risk Codex wording with five fresh contexts**

Use five fresh agents. Give each the revised skill path and the `LARGE` scenario from Task 1, followed by:

```text
Prepare the exact Codex worker allocation and compact dispatch messages. Do not
perform the review, edit files, or spawn workers. State how concurrency capacity,
context inheritance, shared workspace safety, tooling, and final verdict
ownership are handled.
```

Score each response against this exact contract:

- two workers by default, with a third only if separately justified;
- never more than the three stated available worker slots;
- `fork_turns="none"` or an unambiguous fresh task-local context instruction;
- paths and target commands, not pasted diff/skill prose;
- explicit no-edit and no-subagent instruction;
- primary owns tooling, Layers 12/14, evidence recheck, synthesis, and final verdict.

Expected: all five satisfy every item. Read every response manually; do not treat keyword counts as proof.

- [x] **Step 2: Run full small, medium, and fallback scenarios**

Use one fresh agent per scenario from Task 1 against the revised skill.

Expected:

- `SMALL`: zero workers.
- `MEDIUM`: zero or one evidence scout; if one, it is limited to the authorization/call-site sweep.
- `FALLBACK`: inline risk-ranked review with coverage disclosure and no invented worker tool.

Each response must retain the final verdict with the primary agent and prohibit worker edits when a worker is used.

- [x] **Step 3: Refine only demonstrated failures**

If any scenario fails, classify the failure before editing:

- skipped rule under pressure: add a direct requirement at the decision point;
- wrong output shape: strengthen the positive allocation or prompt recipe;
- missing field: add it to the numbered worker contract;
- conditional mistake: key the rule to observable size, risk, or capacity.

Use `apply_patch` for the smallest wording correction. Add or tighten one deterministic assertion in `tests/test_abd_code_review_skill.py` that represents the demonstrated failure, run it RED against the pre-fix text if still observable, apply the fix, and rerun GREEN. Do not add hypothetical rules unsupported by an observed failure.

If wording changes affect the large Codex allocation contract, repeat Step 1 with five new fresh contexts. Otherwise rerun only the failed full scenario with a fresh context.

- [x] **Step 4: Re-run focused deterministic validation**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_abd_code_review_skill -v
python3 scripts/validate_skills.py
git diff --check
```

Expected: all orchestration tests pass, validator reports `Validated 2 skill(s).`, and `git diff --check` emits no output.

---

### Task 3: Human-Facing Compatibility and Full Regression Gate

**Files:**
- Modify: `skills/abd-code-review/README.md:31-37`
- Modify: `tests/test_abd_code_review_skill.py`
- Verify: all files changed by Tasks 1-3

**Interfaces:**
- Consumes: the final portable orchestration behavior from Tasks 1-2.
- Produces: accurate installation/runtime documentation and a release-ready uncommitted change set.

- [x] **Step 1: Add a failing README compatibility assertion**

Add this path near the constants in `tests/test_abd_code_review_skill.py`:

```python
README = ROOT / "skills" / "abd-code-review" / "README.md"
```

Add this method to `CodeReviewOrchestrationTests`:

```python
    def test_readme_documents_adaptive_portable_delegation(self) -> None:
        text = README.read_text(encoding="utf-8").lower()

        self.assertIn("codex", text)
        self.assertIn("claude code", text)
        self.assertIn("adaptive", text)
        self.assertIn("without subagents", text)
```

- [x] **Step 2: Run the README test and verify RED**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_abd_code_review_skill.CodeReviewOrchestrationTests.test_readme_documents_adaptive_portable_delegation -v
```

Expected: FAIL because the current Compatibility section does not name Codex, Claude Code, adaptive delegation, or the no-subagent fallback.

- [x] **Step 3: Update the README Compatibility section**

Replace the current Compatibility paragraph in `skills/abd-code-review/README.md` with:

```markdown
## Compatibility

The core review workflow is portable across agent runtimes. It uses adaptive,
risk-based delegation on Codex and Claude Code, loading only the matching runtime
adapter. Small reviews stay inline, large reviews use bounded read-only workers,
and the complete review still works without subagents when dispatch is
unavailable.
```

- [x] **Step 4: Run the focused README test and verify GREEN**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_abd_code_review_skill.CodeReviewOrchestrationTests.test_readme_documents_adaptive_portable_delegation -v
```

Expected: PASS.

- [x] **Step 5: Run the complete regression gate**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v0.0.0 --dry-run
git diff --check
```

Expected: all unit tests pass; validator reports `Validated 2 skill(s).`; packaging reports `Packaging dry run passed.`; `git diff --check` emits no output.

- [x] **Step 6: Inspect package inclusion without publishing artifacts**

The dry run validates package construction but does not expose member names. Verify the source set used by packaging:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -c "from pathlib import Path; import sys; sys.path.insert(0, 'scripts'); from package_skills import source_files; skill = Path('skills/abd-code-review'); names = {p.relative_to(skill).as_posix() for p in source_files(skill)}; required = {'references/runtime-codex.md', 'references/runtime-claude-code.md'}; assert required <= names, (required - names); print('runtime adapters included')"
```

Expected: `runtime adapters included`.

- [x] **Step 7: Review the final diff and report the uncommitted result**

Run:

```bash
git status --short
git diff --stat
git diff -- skills/abd-code-review/SKILL.md skills/abd-code-review/README.md skills/abd-code-review/references/runtime-codex.md skills/abd-code-review/references/runtime-claude-code.md tests/test_abd_code_review_skill.py
```

Confirm:

- no review layer or output-format requirement changed accidentally;
- runtime-specific mechanics exist only in their adapter;
- no model version is hard-coded;
- no worker is allowed to edit or delegate;
- only approved design, plan, skill, adapter, README, and test files are changed;
- no commit was created.

Report the behavior-level scenario results, deterministic test count, validator result, packaging result, and all uncommitted paths to the user.
