# Node / TypeScript Backend (NestJS, Express, Fastify, workers) — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches Node/TS backend code. Each section extends the same-named universal layer.

## Correctness

- **Floating promises**: async call without `await`/`.catch()` — the error vanishes and ordering silently breaks. Look for `void fn()` used to intentionally fire-and-forget without a `.catch` attached.
- `Promise.all` fails fast — partial side effects of the resolved siblings remain; `allSettled` where partial completion must be handled.
- `parseInt` without radix on odd inputs; `==` vs `===`; `typeof x === "object"` matching `null`; `NaN` propagating through arithmetic then failing comparisons.
- Date pitfalls: `new Date(string)` parsing is locale/format-sensitive; month is 0-indexed in the constructor.
- TS type assertions (`as X`, `!`) papering over a value that can genuinely be undefined at runtime — the compiler is silenced, production isn't. `any` leaking through API boundaries.
- JSON.parse without try/catch on external input; `Number(userInput)` producing `NaN` checks.

## Security

- **NestJS DTO validation is opt-in twice**: DTOs must carry `class-validator` decorators AND a `ValidationPipe` must be active (global or route-level) — an undecorated DTO validates nothing; without `whitelist: true`, extra properties pass through (mass assignment).
- Guards present on new controllers/handlers/resolvers — don't assume a global guard covers new modules; `@Public()`-style decorators not accidentally applied.
- Express: routes added before auth middleware in the chain; error middleware leaking stack traces.
- Injection: template-literal SQL, unparameterized `query()`, MongoDB operator injection (`{ $gt: "" }` from user JSON — sanitize or validate shape), `child_process.exec` with user input (prefer `execFile`).
- Prototype pollution: deep-merge of user JSON into objects; `Object.assign({}, userInput)` into config/options.
- `eval`, `new Function`, dynamic `require` of user-influenced paths.
- Secrets: `.env` committed, secrets in `NODE_ENV`-agnostic client-shared constants, tokens logged by request loggers (redact headers like `authorization`, `cookie`).
- Cookie session flags (`httpOnly`, `secure`, `sameSite`); JWT: algorithm pinned (no `none`), expiry enforced, secret from env.

## Performance

- **Serial `await` in a loop** where batching is safe — `Promise.all` with a concurrency bound (`p-limit`-style) for large sets; conversely, unbounded `Promise.all` over thousands of items is its own outage.
- **Event-loop blocking**: `JSON.parse`/`stringify` of huge payloads, sync crypto (`pbkdf2Sync`), `fs.*Sync` in request paths, catastrophic regex (ReDoS) on user input.
- Buffering entire uploads/responses in memory vs streaming (`pipeline`).
- ORM N+1 (TypeORM/Prisma/Sequelize): relation access in loops without eager/`include`; Prisma `include` breadth on hot queries.
- Per-request instantiation of heavy clients (DB pools, HTTP agents) instead of module/DI-singleton reuse; missing keep-alive agents for high-volume outbound HTTP.

## Reliability

- Every outbound HTTP call has a timeout — `fetch` and default `axios` have none; `AbortController`/`timeout` option required.
- `unhandledRejection`/`uncaughtException` handlers: process should log and exit (restart via orchestrator), not limp on with corrupted state.
- Worker/queue consumers (BullMQ, SQS, Kafka): explicit ack/fail semantics, retry/backoff config, dead-letter queue, idempotent processing.
- Graceful shutdown: SIGTERM handler closes server, drains in-flight requests and jobs, closes DB pools; NestJS `enableShutdownHooks()`.
- DB transactions: not held across external calls; client released back to the pool on all error paths (a leaked client silently exhausts the pool).

## Concurrency

- **Module-level mutable state** shared across concurrent requests (caches, "current user" variables, accumulating arrays). NestJS: request-specific state stored in singleton-scoped providers (default scope!) — needs request scope or AsyncLocalStorage.
- Check-then-act across `await` points: state read before an `await` may be stale after it — the interleaving window is every `await`.
- In-process locks/queues don't survive multi-instance deployment — races must be settled at the DB/queue layer.

## TypeScript Specifics

- `tsconfig` strictness not weakened (`strict`, `noUncheckedIndexedAccess` where used); new `@ts-ignore`/`@ts-expect-error` justified with a comment.
- Runtime validation at trust boundaries: TS types are compile-time only — external input (HTTP bodies, queue messages, env) needs zod/class-validator/etc., not just an interface.
- Exhaustiveness: `switch` on unions with a `never` default guard so new variants fail compilation, not silently fall through.

## Tests

- Async tests actually await their assertions (a passing test that finishes before its expectation runs).
- E2E through real routing/guards/pipes (NestJS `Test.createTestingModule` + supertest) when the contract includes middleware behavior.
- Timers/dates mocked (`jest.useFakeTimers`) instead of real `setTimeout` sleeps; network mocked at boundary (nock/msw), not deep in internals.
