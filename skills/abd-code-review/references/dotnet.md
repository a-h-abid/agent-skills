# C# / .NET (ASP.NET Core, EF Core) — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches C#/.NET code.

## Correctness

- Nullable reference types: `!` (null-forgiving) suppressing a genuinely-possible null; `#nullable disable` in new code; NRT annotations don't validate runtime input — external data still needs checks.
- `async void` outside event handlers (exceptions crash the process, caller can't await); missing `await` on a returned `Task` (fire-and-forget by accident); `Task.Result`/`.Wait()`/`.GetAwaiter().GetResult()` — sync-over-async deadlock and thread starvation.
- `decimal` for money (not `double`/`float`); `DateTime.Now` vs `UtcNow`; `DateTimeKind` honesty; prefer `DateTimeOffset` for absolute instants.
- LINQ deferred execution: query re-enumerated multiple times (re-hits the DB); `First()` vs `FirstOrDefault()` + null-handling mismatch.
- `struct` mutability surprises; `==` on strings vs culture-sensitive `Compare` misuse.

## Security

- SQL: interpolated strings into `FromSqlRaw`/`ExecuteSqlRaw` — use `FromSqlInterpolated` or parameters.
- AuthZ: `[Authorize]` (with the right policy/roles) on new controllers/endpoints — minimal-API endpoints need `.RequireAuthorization()`; `[AllowAnonymous]` not inherited accidentally; resource-based authz (`IAuthorizationService`) for per-object checks (no IDOR).
- Over-posting/mass assignment: binding request bodies straight to EF entities — use DTOs/`[Bind]`.
- Deserialization: `BinaryFormatter`/`SoapFormatter` (banned), `TypeNameHandling.All` in Newtonsoft on untrusted input.
- Secrets in `appsettings.json` committed; use user-secrets/KeyVault/env. Detailed errors (`UseDeveloperExceptionPage`) off in production.
- Path traversal on file endpoints; CSRF: antiforgery on cookie-authenticated form posts.

## Performance & EF Core

- **N+1**: lazy-loading proxies or per-item queries in loops — `Include`/projection (`Select` to DTO); `AsNoTracking()` for read-only queries.
- Client-side evaluation: LINQ that can't translate silently pulls tables into memory (newer EF throws — but check raw `AsEnumerable()` insertions).
- Unbounded queries without paging; `Count()` vs `Any()`; cartesian explosion from multiple `Include`s — split queries where warranted.
- `IQueryable` composed across layers vs materializing early; `SaveChanges` per row in loops vs batching.
- Large objects/streams buffered in memory vs streaming responses (`IAsyncEnumerable`, `Stream` results).

## Reliability

- `HttpClient` lifetime: `new HttpClient()` per request exhausts sockets — `IHttpClientFactory`; explicit `Timeout` (default 100s may be wrong) and Polly-style retry/circuit policies where configured.
- **`CancellationToken` accepted and propagated** through controllers → services → EF/HTTP calls; long operations honor it.
- `DbContext` is not thread-safe and is scoped — captured in singletons or parallel tasks = intermittent corruption; `IDbContextFactory` for background work.
- Background work: `IHostedService`/`BackgroundService` with scoped-service resolution done correctly (create scopes), exceptions handled (an unhandled exception silently stops the service — or crashes the host in .NET 6+), graceful shutdown honoring the stopping token.
- Transactions not spanning external calls; `TransactionScope` with async needs `TransactionScopeAsyncFlowOption.Enabled`.

## Concurrency

- Singleton services (or static fields) holding mutable per-request state; `IMemoryCache` `GetOrCreate` stampedes on hot keys.
- Check-then-act on shared collections vs `ConcurrentDictionary.GetOrAdd`; `lock` on `this`/public objects.
- EF optimistic concurrency: `rowversion`/concurrency tokens on entities where lost updates matter; `DbUpdateConcurrencyException` handled.

## Tests

- `WebApplicationFactory` integration tests exercise routing/auth/filters for auth-sensitive endpoints, not just direct service calls.
- EF InMemory provider hides relational behavior (no FK enforcement, different LINQ translation) — SQLite/Testcontainers for query-shape claims.
- Async tests properly awaited; time abstracted (`TimeProvider`/injected clock) instead of `Task.Delay` sleeps.
