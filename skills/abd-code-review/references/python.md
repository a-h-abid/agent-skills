# Python (Django, FastAPI, Flask, Celery) — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches Python code.

## Correctness

- **Mutable default arguments** (`def f(items=[])`) shared across calls; class attributes used as per-instance state.
- Bare `except:` / `except Exception:` swallowing errors (including `KeyboardInterrupt`/`SystemExit` in the bare form); exceptions logged without `exc_info`/traceback.
- Truthiness traps: `if not x` treating `0`, `""`, `[]` like `None` — use `is None` when absence differs from empty.
- Float for money; naive vs aware `datetime` mixing (`datetime.now()` vs `datetime.now(tz=...)`); `date`/`datetime` comparison surprises.
- Late-binding closures in loops; modifying a list/dict while iterating it.
- Type hints are not runtime checks — external input needs pydantic/validators, not just annotations.

## Security

- `subprocess` with `shell=True` and user input; `os.system`.
- `pickle.load`/`yaml.load` (without `SafeLoader`) on untrusted data; `eval`/`exec`.
- Raw SQL: f-strings/`%`-format into queries; Django `.extra()`/`.raw()` with interpolation; parameterize instead.
- Django: `@login_required`/permission checks on new views (and DRF `permission_classes` — a new ViewSet with defaults may be open); `mark_safe`/`|safe` on user content; `DEBUG=True` leaking settings.
- FastAPI: `Depends` auth actually applied to new routers; response models filtering sensitive fields (returning ORM objects can over-expose).
- Path traversal on `open(user_path)`; `tempfile.mktemp` (race) vs `mkstemp`.

## Performance

- **ORM N+1**: Django `select_related`/`prefetch_related`, SQLAlchemy eager options for relations touched in loops; `QuerySet` re-evaluated repeatedly (each `if qs:` + `for x in qs:` can re-query — check caching semantics).
- `len(qs)` vs `.count()`, `if qs` vs `.exists()`; loading whole tables into memory vs `.iterator()`/chunking; bulk operations (`bulk_create`/`bulk_update`) vs per-row saves in loops.
- Sync blocking calls (requests, DB, file I/O) inside `async def` — blocks the event loop; use async clients or thread offload (`run_in_executor`, `asyncio.to_thread`).
- CPU-bound work in async paths or web workers without offloading; GIL means threads don't parallelize CPU.

## Reliability

- `requests` has **no default timeout** — every call needs `timeout=`; same for many async clients.
- Django transactions: `transaction.atomic` blocks containing external calls; `on_commit` for enqueueing tasks that read just-written rows.
- Celery: tasks idempotent under retry; `acks_late` vs default semantics deliberate; `bind=True` + retry backoff; results/errors monitored, not fire-and-forget; task signature changes break in-flight messages mid-deploy.
- asyncio: fire-and-forget `create_task` without holding a reference (GC cancels it) or handling its exception.

## Tests

- pytest fixtures with unintended scope sharing state; frozen time (`freezegun`/`time_machine`) instead of real sleeps; `responses`/`respx` for HTTP boundaries.
- Django: tests hit the real URL routing + middleware for auth-sensitive views, not just call the view function.
