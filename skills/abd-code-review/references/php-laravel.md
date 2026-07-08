# PHP / Laravel / Lumen — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches PHP/Laravel/Lumen code. Each section extends the same-named universal layer.

## Correctness

- Silently caught `\Throwable`/`\Exception` with an empty or log-only catch block that changes the caller's contract.
- Loose comparisons (`==`) where type juggling bites: `"0" == false`, `"abc" == 0` (pre-PHP 8 semantics), `in_array` without strict flag.
- `null` propagation through Eloquent: `->first()` returning `null` then a method call on it; prefer `->firstOrFail()` or explicit guard.
- Validation rules actually attached: a FormRequest exists but the controller type-hints plain `Request`; `$request->validated()` vs pulling unvalidated `$request->input()` after validation.
- Carbon mutability: `$date->addDays(...)` mutates the original instance (Carbon 2 non-immutable); prefer `CarbonImmutable` or `->copy()`.

## Security

- **Mass assignment**: `$fillable`/`$guarded` correct on any touched Eloquent model; `Model::create($request->all())` with a wide-open `$fillable` is an injection point for columns like `role`, `is_admin`, `price`.
- **Raw SQL**: scrutinize `whereRaw`, `orderByRaw`, `selectRaw`, `DB::select`, `DB::statement` for string interpolation; bindings array must carry user input.
- **Authorization**: policies/gates actually invoked (`authorize()`, `can()`, policy middleware) — defining a Policy does nothing unless it's called. Route-model binding does not scope to the current user/tenant by default; check for global scopes or explicit `where('user_id', ...)`.
- `unserialize()` on any user-influenced data; prefer JSON.
- Blade: `{!! !!}` raw echo of user data; `@json` vs manual `json_encode` into script tags.
- File uploads: `getClientOriginalExtension()`/`getClientMimeType()` are user-controlled; validate server-side and store outside webroot or in object storage.
- Debug leaks: `APP_DEBUG=true` implications, `dd()`/`dump()`/`ray()` left in code, Telescope/Debugbar exposed in production routes.

## Performance

- **N+1**: verify `->with()` / `->load()` eager-loads every relationship touched inside a loop or Blade `@foreach`; watch accessors and `$appends` that lazily touch relations during serialization (an innocent `toArray()` can explode into hundreds of queries).
- `->get()` then `->count()`/`->filter()`/`->first()` in PHP where the DB should do it; `->count()` vs `->exists()` for presence checks.
- Chunking: `->get()` on unbounded tables vs `->chunkById()`/`->cursor()`/`->lazy()`. Note `->chunk()` with concurrent writes can skip rows — `chunkById` is the safe default.
- Cache: `Cache::remember` TTL sane; key includes every variable the value depends on (tenant, locale, user); invalidation on write paths.
- Queue vs sync: heavy work (mail, HTTP calls, exports) dispatched to queue, not done in the request; `dispatchAfterResponse` vs proper queue for anything non-trivial.

## Reliability

- **`env()` outside `config/`** — returns `null` in production under `config:cache`. Config values must go through `config()`.
- HTTP client calls (`Http::`/Guzzle) have `->timeout()` and `->retry()` decisions; a default Guzzle client waits forever under some configs.
- `DB::transaction(function () { ... })` wrapping an external HTTP call or queue dispatch — the connection is held and a partial failure splits state. Dispatch after commit (`afterCommit`, `DB::afterCommit`).
- Queued event listeners / notifications: `ShouldQueue` present where the work is heavy; `afterCommit` set when the job reads rows the transaction just wrote (otherwise the worker can run before commit and see nothing).

## Concurrency & Jobs

- **Queued job serialization compatibility**: changing a job class's constructor/properties, or a model it serializes, breaks jobs already in the queue mid-deploy. Same for cached serialized objects and queued listeners/mailables.
- Jobs idempotent under retry; `$tries`, `$backoff`, `retryUntil()`, and `failed()` handler deliberate, not defaults; dead-letter/`failed_jobs` monitoring exists.
- `WithoutOverlapping` / `ShouldBeUnique` where concurrent execution of the same logical job corrupts state; unique lock TTL longer than max runtime.
- Check-then-act on rows: `firstOrCreate` is not atomic under race — needs a unique constraint backing it; `increment()`/`decrement()` or `lockForUpdate()` instead of read-modify-write for counters/balances.
- Scheduled tasks: `withoutOverlapping()` and `onOneServer()` for multi-server cron.

## Deploy & Data

- Migrations use guarded operations for big tables (see `database.md`); `php artisan migrate` ordering relative to code deploy stated.
- Model `$casts` changes are effectively schema changes for serialized/cached data.
- Route/config/view caches: does the deploy pipeline rebuild them (`config:cache`, `route:cache`)? Closures in routes break `route:cache`.

## Tests

- Feature tests hit the actual route (auth + validation + policy in play), not just unit-test the service class.
- `RefreshDatabase` vs production-like data volume for query-shape assertions; `assertDatabaseHas` over "no exception thrown".
- Fakes actually asserted: `Queue::fake()`/`Mail::fake()` followed by `assertPushed`/`assertSent`, not just silencing side effects.
