# Go — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches Go code. Each section extends the same-named universal layer.

## Correctness

- **Unchecked `err`**: ignored error returns, `_` on the error position, error checked but the success value used anyway. Also errors wrapped without context (`return err` deep in a call chain) making 3am debugging impossible — prefer `fmt.Errorf("doing X: %w", err)`.
- `errors.Is`/`errors.As` vs `==` comparison on wrapped errors; sentinel error comparison after wrapping breaks.
- Loop-variable capture in closures/goroutines (pre-1.22 semantics — check `go.mod` Go version before flagging).
- Nil map writes panic; nil slice append is fine — check which one the code assumes. Nil pointer receivers on interface values (`typed nil != nil` interface trap).
- Slice aliasing: sub-slicing then appending can silently mutate the parent array; `copy()` where isolation is needed.
- Integer division truncation, int/int64 overflow on multiplication (esp. money, durations); `time.Duration` arithmetic mixing units.
- JSON: struct tags present and correct; unexported fields silently dropped; `omitempty` on a field where zero is a legitimate value (0, false) silently omits real data.

## Security

- Raw `fmt.Sprintf` into SQL — bindings/placeholders only. GORM: `Where(fmt.Sprintf(...))` or map/struct conditions with user keys.
- `exec.Command` with user input in arguments (and never through `sh -c`).
- `filepath.Join` with user input then no containment check (`strings.HasPrefix` after `filepath.Clean`/`filepath.Abs`).
- SSRF: `http.Get(userURL)` without allowlist; redirects followed by default.
- `math/rand` where `crypto/rand` is required (tokens, secrets, IDs with security meaning).
- Struct-level authorization: handlers decoding user JSON directly into DB models (mass-assignment equivalent) — use request DTOs.

## Performance

- Query/RPC/HTTP call inside a `range` loop — batch or preload.
- Unbounded goroutine fan-out (`go f()` per item with no semaphore/errgroup limit); unbuffered channels causing lockstep where a buffer was intended.
- Appending in a loop with known size — preallocate (`make([]T, 0, n)`).
- String concatenation in loops vs `strings.Builder`; repeated regex compile in hot path vs package-level `regexp.MustCompile`.
- `defer` inside a loop (releases only at function exit — file handles/locks pile up).
- Byte/string conversions copying large buffers in hot paths.

## Reliability

- **`context.Context` propagated with a deadline** through every I/O call; `context.Background()` deep in request handling severs cancellation.
- `http.Client` without `Timeout` (default is infinite); per-request `context` deadlines for finer control.
- **Response bodies closed** (`defer resp.Body.Close()`) and drained; missing close leaks connections.
- Timers/tickers stopped (`defer ticker.Stop()`).
- Graceful shutdown: `signal.NotifyContext`, `server.Shutdown(ctx)`, workers draining before exit.
- Panics in goroutines crash the whole process — recover at goroutine boundaries for worker pools, or ensure a supervisor restarts.

## Concurrency

- **Data races** on shared maps/slices/structs across goroutines — `sync.Mutex`/`RWMutex`, `sync.Map` for the narrow cases, or channel ownership. Suggest `go test -race` in the validation.
- Goroutine leaks: started but never joined/cancelled — blocked forever on a channel nobody reads, or `for range ch` on a channel never closed.
- `sync.WaitGroup`: `Add` before `go`, `Done` deferred; `errgroup.Group` with `SetLimit` for bounded parallel work.
- Check-then-act on shared state; `sync.Once` for one-time init; atomic ops (`sync/atomic`) for counters instead of unguarded increments.
- Channel close discipline: only the sender closes; double-close panics; send on closed channel panics.
- Mutex copied by value (struct containing a mutex passed by value); lock not released on early-return error paths (prefer `defer mu.Unlock()`).

## GORM / Database (with `database.md`)

- `Find` vs `First` error semantics: `First` returns `ErrRecordNotFound`, `Find` returns empty slice with nil error — code often checks the wrong one.
- Transactions: `tx := db.Begin()` with a missed `Rollback` on error paths — prefer the `db.Transaction(func(tx ...))` closure form. **`tx.Commit()` error checked.**
- Zero-value trap: `Updates(struct)` skips zero-valued fields (false, 0, "") — silent partial updates; use a map or `Select` to force fields.
- Preloading (`Preload`) for relations touched in loops; `Save` vs `Updates` full-row clobber under concurrency.

## Tests

- Table-driven tests for the new branches; `t.Parallel()` used where safe (and not used where tests share state).
- Race detector in CI for concurrency-touching changes.
- `time.Sleep`-based synchronization in tests = flake; use channels/sync points.
- HTTP handlers tested through `httptest` with real routing/middleware, not by calling the function directly, when auth/middleware is part of the contract.
