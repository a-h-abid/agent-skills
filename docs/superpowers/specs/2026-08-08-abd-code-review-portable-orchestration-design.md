# Portable Code-Review Orchestration Design

## Goal

Make `abd-code-review` use subagents cost-efficiently on Codex while retaining first-class Claude Code support and the skill's existing review depth, evidence standards, and final output contract.

## Constraints

- Keep the core workflow portable across agent runtimes.
- Preserve the existing defensive review methodology and stack-specific references.
- Avoid delegating work whose setup and synthesis cost exceeds its context savings.
- Keep target discovery, tooling, whole-change judgment, severity calibration, and the final verdict with the primary agent.
- Treat reviewer workers as read-only even on runtimes where workers share a writable workspace.
- Fall back to a complete inline review when worker tooling or capacity is unavailable.
- Do not hard-code assumptions that every runtime has the same worker types, context inheritance, or concurrency limit.

## Architecture

The main `SKILL.md` will describe portable roles and decisions. Runtime-specific mechanics will live in two references:

- `references/runtime-codex.md`
- `references/runtime-claude-code.md`

The primary agent detects its runtime and reads only the matching adapter. If no adapter matches, it follows the portable fallback in `SKILL.md`.

Portable terminology replaces runtime-specific names:

- **Evidence scout:** a narrowly scoped worker that performs one bounded search or verification task.
- **Reviewer worker:** a read-only worker that reviews an assigned concern and file bundle.
- **Primary agent:** owns scope, risk mapping, tooling, synthesis, evidence rechecks, and the final review.

## Delegation Policy

Delegation depends on review size, risk, separability, and available worker capacity.

### Small changes

For changes below roughly 150 lines, the primary agent performs the review inline. Worker setup and synthesis would normally cost more than they save.

### Medium changes

For changes around 150-800 lines, the primary agent performs the full review. It may use one evidence scout only when there is a bounded, independent search that would materially reduce context or elapsed time, such as tracing call sites, locating authorization coverage, or checking schema support.

### Large changes

For changes above roughly 800 lines, the primary agent builds the target, intent, change map, stack map, tooling leads, and risk ranking. It then creates concern bundles from the actual change rather than dispatching one worker for every fixed checklist category.

Use two reviewer workers by default. Add a third only when the diff contains a genuinely separate high-risk concern that cannot be combined cleanly with either existing bundle. Never exceed the runtime's currently available worker capacity.

Bundle by shared files, data flow, and risk so each worker can reach conclusions without rereading most of another worker's slice. Typical concerns remain correctness/contracts, security/privacy, data/deploy/config, and production behavior, but they may be combined or omitted when the change does not contain them.

Architecture fit and missing-code analysis remain with the primary agent because they require the whole-change view.

## Worker Input and Output Contract

Each worker receives only:

1. The target as a command to run and its assigned risk-ranked files.
2. A short intent and change-map summary.
3. The path to the main skill sections and stack references it must read.
4. Tooling leads relevant to its assignment.
5. A findings-only output contract.

Workers do not receive pasted diffs or duplicated skill prose when they can read the source files directly. They do not edit files, run broad test suites already run by the primary agent, issue the final verdict, or delegate further.

Each finding includes `file:line`, a severity suggestion, confidence, the defect and consequence, evidence actually read, and a suggested fix. A clean assignment returns `no findings` plus anything it could not inspect.

The primary agent deduplicates by root cause, reopens cited evidence for proposed Blocking findings, recalibrates severity with the whole-change view, records inspection gaps, and writes the existing review format.

## Codex Adapter

The Codex adapter will:

- Map evidence scouts and reviewer workers to Codex's collaboration tools.
- Prefer fresh task-local context for bounded workers rather than inheriting the entire conversation.
- Account for the primary agent occupying one concurrency slot.
- Dispatch only independent bundles concurrently and consolidate when capacity is smaller than the bundle count.
- State explicitly that all agents share the workspace and that workers are read-only for review tasks.
- Keep implementable follow-up work on the same worker only when clarification is required; review workers otherwise return one compact report.
- Use the least costly capable model and reasoning level for bounded evidence collection when runtime policy permits selection.
- Reserve stronger model/reasoning choices for high-risk, cross-file reviewer bundles when the expected quality gain justifies the cost.
- Avoid hard-coding a model version so the adapter remains valid as Codex models change.

## Claude Code Adapter

The Claude Code adapter will preserve the effective behavior of the current skill:

- Use read-only exploration workers for bounded evidence searches.
- Use general-purpose reviewer workers for deep, multi-file concern bundles.
- Run independent bundles in parallel within available capacity.
- Keep prompts path-based and outputs concise.
- Keep synthesis and the verdict with the primary agent.

The adapter will avoid making Claude-specific worker names part of the portable core.

## Fallback and Failure Handling

- If worker dispatch is unavailable, review inline in risk-ranked order and list lighter scrutiny in the coverage overview.
- If capacity is lower than expected, consolidate bundles rather than queueing many narrow workers.
- If a worker fails or cannot inspect its assignment, the primary agent covers the high-risk gap inline or records it explicitly.
- If a worker edits the workspace despite the read-only contract, stop using that worker's results, disclose the mutation, and preserve user-owned changes.
- If worker reports conflict, the primary agent reads the cited evidence and resolves the conflict rather than voting by majority.
- Tooling runs once under the primary agent; workers receive only relevant leads.

## Validation Strategy

Apply RED-GREEN-REFACTOR to the orchestration guidance.

### Baseline

Exercise the existing skill in fresh-context scenarios representing:

- a small low-risk diff where delegation is wasteful;
- a medium diff with one independent evidence search;
- a large multi-concern diff under Codex-like limited capacity;
- unavailable worker tooling.

Record unnecessary workers, duplicated context, runtime-specific ambiguity, concurrency mistakes, unsafe write behavior, and synthesis gaps.

### Revised behavior

Run equivalent fresh-context scenarios with the revised skill and verify:

- no delegation for a normal small review;
- at most one justified scout for a medium review;
- two large-review workers by default and no more than three when risk warrants it;
- no dispatch beyond available capacity;
- task-local worker context and path-based instructions;
- read-only worker behavior;
- one tooling run;
- primary-agent evidence verification, deduplication, and verdict ownership;
- complete inline fallback.

Use focused wording micro-tests where baseline behavior shows a repeatable instruction-shape failure. Finish with the repository's skill validator, packaging tests, and relevant workflow tests.

## Non-Goals

- Changing the fourteen review layers or their severity model.
- Adding new language or framework review references.
- Making subagents mandatory for every review.
- Tying the portable skill to a particular Codex or Claude model version.
- Committing, pushing, merging, or publishing the changes as part of this task without explicit user direction.

## Success Criteria

The revised skill is successful when both Codex and Claude Code can select the correct runtime guidance, small and medium reviews avoid unnecessary worker cost, large reviews use bounded risk-based parallelism, worker prompts remain compact, and the primary agent still produces evidence-backed findings with the same or better coverage and severity calibration.
