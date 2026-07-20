---
name: abd-code-review
description: Run a deep, evidence-based, multi-layer code review on a diff, PR, branch, commit range, or file set — any language, framework, or stack.
disable-model-invocation: true
---

# Deep Code Review

Review the target the user named — a diff, PR, branch, commit range, or set of files (including anything passed as an argument to this skill). If they didn't name one, use the default in Step 0.

You are reviewing as a **senior staff engineer** and production owner. Bias your effort toward **correctness, security, data integrity, reliability, performance, and failure modes** over stylistic cleanliness — flag style briefly, then move on. Your goal is not to produce a long checklist; it is to produce **useful, verified, high-signal findings** that help the author safely ship or correctly rework the change.

This review is **language- and stack-agnostic**: detect what you're actually looking at, then layer the matching stack-specific scrutiny (from `references/`) on top of the universal principles below.

## Review Principles

1. **Evidence first.** Never claim an issue is real unless you read the relevant code, config, schema, tests, or call sites.
2. **Risk over taste.** Prioritize production impact. Don't block on personal preference.
3. **Review the change, not only the diff.** Follow call sites, data flow, config, tests, migrations, consumers, and deploy effects.
4. **Think like production.** Real traffic, partial failure, retries, bad input, old clients, rolling deploys, stale caches, concurrent workers, dependency outages.
5. **Be fair.** Distinguish confirmed problems from likely risks and unverified suspicions.
6. **Don't pad.** No fake findings to fill a layer; no "no issues found" boilerplate per layer.
7. **Don't silently narrow scope.** Anything you couldn't inspect goes in the coverage overview.

## Step 0 — Gather context before judging

Don't review blind. First, actually load the thing you're reviewing:

- If given a PR number or branch, get the diff (`gh pr diff <n>`, `git diff <base>...<head>`). If given files, read them. **If no target is given**, default to uncommitted changes plus the current branch diffed against the default branch (`git diff origin/main...HEAD` + `git status`/`git diff`); state the target you chose. Only ask if that yields nothing sensible.
- **Load the intent, not just the code**: PR description (`gh pr view <n>`), commit messages (`git log --oneline <base>..<head>`), linked ticket if referenced. Layer 1's "is this the right problem?" is unanswerable without this.
- **Build a change map** before judging: entry points touched (routes, handlers, jobs, consumers, cron, webhooks, CLI, middleware), data touched (tables, cache keys, queues/topics, files, external APIs), runtime touched (env vars, flags, secrets, containers, CI/CD), and the compatibility surface (public APIs, event schemas, DB schema, old clients).
- Read enough surrounding code to understand behavior — a diff line is rarely judgeable in isolation. When a finding depends on how a function is called, **open the call sites** rather than assuming. Read model/entity definitions when validation or authorization depends on them; read migrations together with the code that uses them.
- **If this is a re-review** (a prior review of this PR exists in the conversation): verify each prior finding against the new diff, report resolved/unresolved status briefly, and give full treatment only to new or changed code.

### Size the review

Pick a strategy before diving in:

- **Small diff (< ~150 lines)**: full-depth pass on everything. Don't pad — a clean 20-line fix deserves a short review.
- **Medium (~150–800 lines)**: full pass, but lead with the highest-risk files.
- **Large (> ~800 lines)**: rank files by risk first — migrations, auth/authz, payments/money, concurrency-touching code, external integrations get deep review; mechanical/generated/rename-only files get a skim. **List the files that got lighter scrutiny in the coverage overview.** Never silently skim.

### Leverage the project's own tooling first

Before manual review, check for and run whatever the repo already has — it's cheaper and more reliable than re-deriving the same findings by eye:

- Static analysis / linters / type checkers if configured (`phpstan`, `golangci-lint`, `eslint`/`tsc --noEmit`, `mypy`, `cargo clippy`, etc.).
- The test suite scoped to touched files/packages, if runnable quickly.
- Security tooling if present: dependency audit, secret scan, SAST.
- Treat tool output as **leads to verify and contextualize**, not findings to copy-paste. Don't spend manual effort on classes of issues the tooling already covers and passes.
- If tooling exists but can't run (missing deps, no DB), note that in the coverage overview.

### Evidence-gathering moves

"Verify before you flag" means doing the work. Concretely:

- Claiming a missing index → **read the actual schema/migration files** for that table.
- Claiming N+1 / missing eager-load → find the loop **and** the repeated I/O inside it.
- Claiming a race → identify the two concurrent actors that actually interleave.
- Claiming missing authorization → check middleware, guards, route groups, and base classes before declaring it absent.
- Suspicious-looking code → `git log -p` / `git blame` it; it may be a deliberate fix with history.
- Claiming dead/unused code → grep for call sites first.

Tag every finding with confidence: `[confirmed]` (you read the evidence and it's real), `[likely]` (strong evidence, one piece of context missing), or `[unverified]` (plausible suspicion worth checking). Unverified suspicions go in "Worth considering" with what you'd need to check — never in Blocking.

### Detect the stack

Identify, from the files in the diff, the **language(s)**, **framework(s)**, and **runtime/infra** in play. Then **read the matching reference file(s)** — they contain the stack-specific checks that this file deliberately omits. Read only the ones for stacks actually present in the diff.

| Signal in the diff | Stack | Read |
|---|---|---|
| `*.php`, `composer.json`, `artisan`, Eloquent, `routes/` | PHP / Laravel / Lumen | `references/php-laravel.md` |
| `*.go`, `go.mod`, GoFiber, GORM | Go | `references/go.md` |
| `*.ts`/`*.js`, `package.json`, NestJS/Express/Fastify, Node workers | Node / TypeScript backend | `references/node-ts.md` |
| `*.kt`, Gradle, Jetpack Compose, Android manifests | Kotlin / Android | `references/kotlin-android.md` |
| `*.vue`, Nuxt, Vite, Pinia | Vue / Nuxt frontend | `references/vue-nuxt.md` |
| JSX/TSX, React, Next.js | React / Next.js frontend | `references/react-next.md` |
| `*.py`, `pyproject.toml`, Django/FastAPI/Flask, Celery | Python | `references/python.md` |
| `*.java`, `pom.xml`/Gradle, Spring | Java / Spring | `references/java-spring.md` |
| `*.rs`, `Cargo.toml` | Rust | `references/rust.md` |
| `*.cs`, `*.csproj`, ASP.NET | C# / .NET | `references/dotnet.md` |
| `*.sql`, migration files, schema/ORM model changes | Database | `references/database.md` |
| `Dockerfile`, Compose, K8s/Helm, Terraform, CI pipeline files | Infra / Containers / CI-CD | `references/infra-cicd.md` |
| Dependency manifests or lockfiles changed (`composer.json`/`.lock`, `package.json`/lockfiles, `go.mod`/`.sum`, `requirements*.txt`, `Cargo.toml`/`.lock`, etc.) | Dependencies / supply chain | `references/dependencies.md` |
| `*.sh`/`*.bash`, shell in CI steps or containers; standalone config files (`.env*`, `*.yaml`/`*.toml`/`*.ini`, `nginx.conf`, etc.) | Shell scripts / configuration | `references/shell-config.md` |

For a stack with no reference file (Ruby, Elixir, Swift, C++…), apply the universal layers plus your own knowledge of that ecosystem's idioms and failure modes — the layers below are stack-independent by design.

Work through every layer at the depth your sizing strategy allows. Don't skip a layer because nothing obvious jumps out — actively look. But only **report what's actually present**; don't pad the output.

## Layer 1 — Intent & Correctness

- What problem is this solving — is it the right problem, and does the implementation actually solve it? Does it match the stated PR/ticket intent and acceptance criteria?
- Logic correctness: boundary conditions, off-by-one, null/zero/empty/negative/duplicate/expired/unexpected-type inputs. Read every input as adversarial or confused, not cooperative.
- State transitions valid and enforced — invalid transitions rejected, not silently accepted.
- Symmetric operations complete: a rule added to create but forgotten in update/delete/import; partial-update (PATCH) semantics where omitted-field must differ from explicit-null.
- Money represented as float instead of integer-minor-units/decimal; rounding rules explicit; timezone-naive datetime handling or implicit server-timezone assumptions; locale/encoding assumptions.
- Error returns honored, not ignored; failures surfaced, not swallowed.

## Layer 2 — Security & Abuse Resistance

- User-controlled input: validated for type, format, length, range, enum, and object shape before use — on the server, regardless of client-side validation.
- **Authorization** checked on every new endpoint/route/handler/queue consumer/webhook/resolver — not just authentication. Confirm the actor is allowed to act on *this* resource (no IDOR); tenant/ownership scoping enforced at the query level; bulk actions authorize every item.
- Injection: queries parameterized everywhere; no command injection via shell/process execution; no path traversal on file/object-storage paths; no SSRF on outbound calls built from user input (including redirects and cloud metadata IPs); no unsafe deserialization or dynamic code execution.
- Web surface: CSRF protection on cookie-authenticated state changes, CORS not overly broad, open redirects prevented, uploads validated (type, size, storage location, no executable serving).
- Abuse: rate limits on login/OTP/password-reset/expensive/write-heavy endpoints; oversized payloads rejected.
- Secrets: none hardcoded or committed; they belong in env/secrets manager. Error responses don't leak stack traces, SQL, or internal hostnames.
- Sensitive data (tokens, passwords, PII, full card/MSISDN) never logged in plaintext, never leaked to client bundles or analytics.

## Layer 3 — Data Integrity & Persistence

- Database constraints enforce the invariants the code assumes: unique, foreign key, not-null, check constraints — don't rely on "the app validates it" when the DB can enforce it.
- Read-modify-write operations atomic where correctness requires it; deletion semantics deliberate (soft vs hard, cascades, orphan cleanup).
- Numeric precision correct for money, balances, quotas, counters. Time stored consistently (UTC boundaries explicit).
- Backfills idempotent and resumable; generated IDs/slugs/codes collision-safe.
- Serialization round-trips preserve meaning; schema evolution of stored blobs considered.

## Layer 4 — Deploy & Migration Safety

Review schema and runtime changes as a **rollout**, not a static diff — old and new code run simultaneously during deploy.

- Migration backward-compatible with the currently-deployed app during a rolling deploy (non-nullable column with no default; renaming/dropping a column old code still reads).
- Large-table changes: does the `ALTER` lock the table at production size? Online schema-change tool needed?
- Rollback/down migration present and honest (doesn't pretend data loss is reversible); destructive operations explicitly called out.
- Deploy ordering explicit where it matters: migration before/after code, worker restarts, cache clears, flag flips.
- Serialized artifacts in flight survive the deploy: queued jobs, cached objects, events/messages produced by old code and consumed by new (and vice versa).

## Layer 5 — Performance & Scalability

- **Repeated I/O inside a loop** — the universal N+1 (DB, cache, HTTP, RPC, filesystem, queue).
- Missing indexes on columns hit by `WHERE`, `JOIN ON`, `ORDER BY` — confirmed against the actual schema.
- Over-fetching: `SELECT *` on wide tables; unbounded queries with no pagination/limit; unbounded fan-out or recursion.
- Nested loops / repeated linear scans over collections that could be large in prod — use a map/set/index instead of O(n²).
- Large result sets loaded fully into memory instead of streamed/chunked.
- Synchronous external calls in the request path that could be async, batched, or moved to a job.
- Caching: present where useful — and is **invalidation** correct? Stampede/dogpile on hot keys? Tenant/user scoping so cached data can't bleed across users?
- What's the bottleneck at **10× traffic, 10× data, 10× concurrency**? Single-row write contention, lock hot spots, connection-pool exhaustion, hot partitions.

## Layer 6 — Reliability & Resilience

Assume dependencies fail, latency spikes, messages duplicate, and processes restart mid-operation.

- Exceptions/errors handled at the right level, logged with context (correlation ID, actor, offending input) — not swallowed silently.
- **Every external call (HTTP, DB, queue publish, RPC) has a timeout/deadline.** Missing timeout = resource leak under degradation.
- Retries: bounded attempts, backoff with jitter, and **only** where the operation is idempotent.
- Critical dependency down — fallback/degraded mode, or does the whole feature die with it?
- Transaction boundaries: no DB transaction held open across an external network call; queue publish reliable relative to DB commit where required (outbox or equivalent).
- Multi-step workflow: if step 3 fails, is step 1's effect left inconsistent? Compensation/rollback/recovery path?
- Idempotency on anything retryable: queue consumers, webhook handlers, scheduled jobs (safe if overlapping, delayed, or run twice), mutating endpoints.
- Graceful shutdown: in-flight requests/jobs drained, not killed mid-write.

## Layer 7 — Concurrency & Race Conditions

- Shared mutable state touched by multiple requests/workers/threads/processes simultaneously.
- Classic read-then-write (check-then-act) races at the DB level — atomic operation, `SELECT ... FOR UPDATE`, optimistic version column, unique constraint, or queue serialization needed?
- Duplicate triggers (double-click, retry, refresh, webhook redelivery) must not create duplicate side effects — idempotency keys on payment/order/notification-like mutations.
- Queue consumers safe to scale to N workers without double-processing; ordering assumptions explicit and enforced if required.
- Counters, quotas, balances, inventory, coupon redemptions, and status transitions race-safe.
- Locks have timeout, scope, and failure handling; lock ordering can't deadlock.

## Layer 8 — API & Contract Compatibility

- Backward compatible for existing consumers — no silently removed/renamed/retyped fields without versioning; new fields have safe defaults and documented optionality.
- Correct semantics: right HTTP verb and status code (201 vs 200, 422 vs 400, 409 for conflicts); error shape consistent and machine-readable.
- Event/message schema changes: old and new consumers/producers coexist with both shapes in flight; schema registry/spec (OpenAPI, protobuf, GraphQL) updated; generated clients regenerated if required.
- New endpoints protected against oversized payloads and abusive request rates.

## Layer 9 — Observability & Operability

Could an on-call engineer diagnose and mitigate this at 3am?

- Structured logging with correlated context on new error paths and important state transitions.
- Metrics emitted for new significant operations (latency, failure rate, queue depth/lag) that an alert could actually be built on — if this breaks, does anything page someone, or does it fail silently?
- A single unit of work traceable end-to-end across any new async flow.
- Audit logging for sensitive/admin/security-relevant operations.
- Health/readiness checks reflect new hard dependencies.

## Layer 10 — Config, Flags & Operational Readiness

- Zero-downtime deployable, or does it require specific ordering? Say so explicitly.
- New env vars/config documented, with safe defaults, and **fail-fast at startup** if required and missing (not a `null` surprise at first request). Config validated and typed where possible.
- Risky behavior gated behind a feature flag / kill switch? If a flag is added: owner, default, rollout plan, and a removal path — or it's permanent config in disguise.
- Rollback plan: clean code revert, or does schema/state make rollback destructive?
- Multi-tenant/region config can't bleed across tenants/regions; dev/staging/prod behavior differences intentional.

## Layer 11 — Test & CI Quality (not coverage %)

- Do tests cover the **risky** paths — failure modes, business-logic branches, authz failures, external-call failures, concurrency — not just happy paths and getters?
- Bug fix without a regression test that would have caught it?
- Assertions meaningful, or `assertTrue`-style theater? Behavior-tested or implementation-detail-tested (brittle)?
- Integration tests for new queries, queue flows, and external integrations; flakiness controlled (time, randomness, network).
- Will failures actually block CI merge? Snapshot/golden updates reviewed, not blindly accepted.

## Layer 12 — Architecture & Maintainability

- Fits the existing architecture and conventions, or introduces an inconsistent pattern without justification?
- Abstraction level matched to the problem's actual complexity — neither over-engineered nor a god-function.
- New coupling between modules that should stay independent; dependencies pointing the wrong way (domain depending on infrastructure/UI).
- Single clear responsibility; naming reveals intent; comments explain *why*, not *what*.
- Dead code, debug leftovers, commented-out blocks, ownerless TODOs removed.

## Layer 13 — Privacy & Compliance

Apply when the change touches user data, payments, identity, auth, logs, analytics, exports, or admin actions.

- Data collected is necessary and minimized; retention/delete/export flows not broken by the change.
- Sensitive data masked in logs, traces, analytics, and support tooling.
- Access to personal/admin data audited; consent and user preferences respected.
- Test fixtures contain no real customer data.

## Layer 14 — What's missing

The most dangerous problems are often **absent** code, not present code. Actively ask:

- A new route but no authorization policy? A new input path but no validation?
- A new failure mode with no handling, no test, no metric, no log?
- A new external call with no timeout/retry decision?
- A new mutation with no idempotency/race protection?
- A config/flag/migration/index/manifest/doc the change implies but the diff doesn't include?
- A symmetric operation half-done (added to create, forgotten in update/delete/list/export)?
- A frontend change with no loading/empty/error/permission state?

## Output Format

**Open with a coverage overview** — this is the reader's TL;DR; keep it tight:

```md
## Review Overview
**Target:** <PR/branch/files/commit range reviewed>
**Stack:** <languages/frameworks detected> · **Size:** <~N lines across M files>
**Summary:** <2–3 sentences: what this change does as you understand it, and its overall risk profile>
**Verdict:** ✅ ship it · ⚠️ ship with required fixes · 🛑 needs rework — <single most important thing to address first>
**Inspected:** <diff, call sites, tests, migrations, schema, tooling run…>
**Not inspected:** <what you couldn't check and why — tests not runnable, no DB access, files skimmed in a large diff — so the author knows the review's blind spots>
```

If your understanding in **Summary** is wrong, the author catches a misdirected review immediately instead of after 15 findings.

Then structure findings by **severity**, not by layer. Rules:

- **Confidence tag** on every finding — `[confirmed]`, `[likely]`, or `[unverified]`. **A finding cannot be Blocking unless it is `[confirmed]` or `[likely]` with the evidence stated** — otherwise it demotes to "Worth considering".
- **Scope tag** where it's not obvious — `[introduced]` (this change created it) vs `[pre-existing]` (already there, this change touches or worsens it). Pre-existing issues in untouched nearby code are at most 🟡, mentioned once, briefly.
- **Deduplicate by root cause**: the same problem in 8 places is ONE finding with a list of instances, not 8 findings.

1. **🔴 Blocking** — security holes, data corruption/loss risk, unsafe migration/deploy, broken authz, will break in production.
2. **🟠 Should fix** — real correctness/reliability/performance risk, but not an emergency.
3. **🟡 Worth considering** — design/architecture concerns, debatable tradeoffs, unverified-but-plausible suspicions with what you'd need to check.
4. **🟢 Nit** — style, naming, minor cleanup. **Max ~5**; if there are more, name the pattern once.

For each finding give: **`file:line`** reference, **what's wrong**, **why it matters concretely** ("this N+1s ~200 queries per request at current cart sizes", not "this could be better"), and a **suggested fix** (ideally a code snippet).

After the findings, optionally add **Done well** (1–2 lines max): a genuinely good decision worth reinforcing. Skip if forced.

### Severity calibration

- 🔴 requires plausible: unauthorized data access, data loss/corruption, duplicate money movement, production outage, unsafe migration on real data, secret/PII leak, broken public contract.
- 🟠 for: real but bounded correctness bugs, meaningful performance regressions, missing timeout/retry on important paths, missing tests around risky behavior.
- 🟡 for: better designs that aren't required, future-scaling concerns, readability improvements, tradeoffs worth acknowledging, unverified suspicions.
- 🟢 only for: naming, formatting, tiny duplication, comment wording.

### Before returning the review, self-check

Did I verify every Blocking/Should-fix claim, or tag it honestly? Did I open call sites where a finding depended on them? Did I check the layers that don't announce themselves (deploy safety, concurrency, what's missing)? Did I deduplicate and avoid checklist-dumping? Does the author know exactly what to change next? If any answer is no, fix the review before returning it.
