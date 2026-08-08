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
duplicating skill prose. Worker prompts restate applicable user and repository
constraints.

Every prompt states that the worker is read-only, must not edit files, create
artifacts, change Git state, or delegate, and returns only the portable findings
contract. The primary agent runs broad tooling once, resolves report conflicts
against source, verifies proposed Blocking evidence, performs whole-change
Layers 12 and 14, and writes the final verdict.

If a worker changes the workspace, discard its report, disclose the mutation,
preserve user-owned changes, and cover the high-risk slice inline.
