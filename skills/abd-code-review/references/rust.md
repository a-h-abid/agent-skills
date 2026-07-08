# Rust — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches Rust code.

## Correctness

- **`unwrap()`/`expect()`/`panic!` on paths reachable with real input** — fine in tests/main-init, a crash in request handlers and libraries. Indexing (`v[i]`, slicing) panics too — `get()` where out-of-range is possible.
- Error handling: `?` conversions losing context (add context via `anyhow::Context`/custom error variants); errors mapped to `()` or stringly-typed errors at library boundaries; `Result` ignored via `let _ =` on operations whose failure matters.
- Integer overflow: wraps in release mode by default — `checked_*`/`saturating_*`/`wrapping_*` chosen deliberately for arithmetic on external input, money, sizes; `as` casts silently truncating (`u64 as u32`).
- Float comparison; `f64` for money vs integer minor units / decimal crates.
- `clone()` hiding logic bugs: mutating a clone while believing you mutate the original.

## Security

- `unsafe` blocks: justified, minimal, documented invariants; no soundness holes (aliasing `&mut`, uninitialized memory, transmutes).
- SQL via string formatting vs parameterized (sqlx/diesel bind); command injection via `Command::new("sh").arg("-c")` with user input.
- Path traversal: user paths joined then not canonicalized/contained.
- `Deserialize` on untrusted input: size limits (serde with bounded readers), `deny_unknown_fields` where extra fields matter; panics inside `Deserialize` impls.

## Performance

- Unnecessary `clone()`/`to_owned()`/`collect()` in hot paths — borrow or iterate lazily; `String` concatenation in loops vs `push_str`/`format!` once.
- Blocking calls in async contexts (`std::fs`, `std::thread::sleep`, sync locks held across `.await`) — starves the executor; use `tokio::fs`, `tokio::time::sleep`, or `spawn_blocking`.
- Allocations in loops with knowable capacity (`Vec::with_capacity`); `Box<dyn Trait>` vs generics in hot paths — deliberate.
- Regex/parsers compiled once (`LazyLock`/`OnceLock`), not per call.

## Reliability & Async (tokio)

- HTTP clients (`reqwest`) with explicit timeouts — the default client has no request timeout; `tokio::time::timeout` around external calls.
- **Cancellation safety**: tasks dropped at `.await` points (select!, timeouts, client disconnect on server frameworks) — partial writes/state updates must be cancel-safe or shielded.
- Spawned task `JoinHandle`s: errors observed, not dropped silently; panics in tasks surfaced.
- Graceful shutdown: signal handling, draining in-flight work, `CancellationToken`-style propagation.

## Concurrency

- Lock poisoning handling (`Mutex::lock().unwrap()` cascades panics); **std `Mutex` held across `.await`** (won't compile with Send bounds — but `tokio::sync::Mutex` held across long awaits is a throughput bug); prefer narrowing critical sections.
- Deadlock-prone lock ordering; `RwLock` writer starvation on read-heavy paths.
- Channels: bounded vs unbounded (`unbounded_channel` = hidden memory leak under backpressure); send errors (receiver dropped) handled.
- Atomics: correct `Ordering` (over-weak orderings on flags/counters shared across threads).

## Dependencies & Build

- New crates: maintained, audited (`cargo audit`/`cargo deny` if configured), feature flags minimal (default-features trimmed where size matters).
- `Cargo.lock` updated with `Cargo.toml`; MSRV implications of new syntax/crates.

## Tests

- `#[should_panic]` tests pinned with `expected =`; async tests on the right runtime (`#[tokio::test]`); property tests (proptest/quickcheck) for parsing/arithmetic invariants where inputs are adversarial.
- `cargo clippy` clean on touched code; new `#[allow(...)]` justified.
