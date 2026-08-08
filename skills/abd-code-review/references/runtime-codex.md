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
- applicable user and repository constraints;
- the portable findings-only output contract.

Worker prompts restate applicable user and repository constraints. Codex agents
use a shared workspace. Every review prompt must say: **You are read-only: you must
not edit files or create artifacts; you must not change Git state or delegate; you
must not spawn subagents.**
The primary agent alone writes the final verdict.

Use stable task names based on concern, such as `review_auth_contracts` or
`scout_order_calls`. Do not paste the diff when the worker can run the target
command itself.

## Collection and repair

Use `wait_agent` with a practical interval while workers run. When a report lacks
one specific piece of cited evidence, send one focused follow-up to the same
worker; do not restart the full review. If the worker fails or conflicts with
another report, the primary agent verifies the slice inline. If a worker changes
the workspace, discard its report, disclose the mutation, preserve user-owned
changes, and cover the high-risk slice inline.
