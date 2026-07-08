# Database, Schema & Migrations — Cross-Cutting Checks

Apply when the diff touches SQL, migration files, schema definitions, or ORM models. These checks are engine-agnostic unless tagged; combine with the language reference for the ORM in play.

## Migration Safety (rolling deploys)

Old app code and new schema (or vice versa) run together during every deploy. For each migration ask:

- **Is it backward-compatible with the currently-deployed code?** Classic breakers: adding a non-nullable column without a default (old code's INSERTs fail); renaming or dropping a column/table old code still reads; tightening a constraint existing rows violate.
- Multi-phase where needed: expand → migrate data → switch code → contract. A rename is *always* two deploys (add new, backfill, dual-write/read, drop old).
- **Locking**: does the `ALTER` take a long exclusive lock at production row counts? Postgres: adding a column with a volatile default, `ALTER TYPE`, adding NOT NULL (pre-11 patterns) rewrite/scan the table; index creation needs `CREATE INDEX CONCURRENTLY` (and can't run in a transaction). MySQL: verify the operation is INPLACE/INSTANT or plan gh-ost/pt-osc.
- Down migration honest: does it actually restore, or pretend data loss is reversible? Destructive operations (drop/truncate/backfill) called out explicitly with a run-once/irreversibility note.
- Backfills: idempotent, resumable, batched (not one UPDATE over 50M rows holding locks and bloating the WAL/undo), throttled against production load, and separated from schema-DDL migrations.
- Deploy ordering stated: migration before or after code rollout, and what happens in the window between.

## Schema Design

- **Constraints enforce the invariants the code assumes**: NOT NULL, UNIQUE, FK, CHECK. "The app validates it" is not enforcement — concurrent writers, admin consoles, and future code paths bypass app validation.
- FKs: ON DELETE behavior deliberate (CASCADE vs RESTRICT vs SET NULL) — an accidental cascade is data loss; a missing one is orphans.
- Column types: money as integer minor units or DECIMAL (never FLOAT); timestamps with time zone semantics explicit (`timestamptz` in Postgres); string lengths meaningful, not all `VARCHAR(255)`; enums vs lookup tables vs CHECK — migration cost of each considered.
- JSON columns intentional: queried fields probably belong in real columns; if queried, are they indexed (expression/GIN)?
- Soft delete: partial/filtered unique indexes so "deleted" rows don't block reuse; every query path filters deleted rows (a global scope or view, not per-query discipline).

## Indexes & Query Shape

- **Every new query's `WHERE`/`JOIN ON`/`ORDER BY` columns confirmed against actual indexes in the schema** — read the migrations/schema, don't assume. Composite index column order matches the query (leftmost-prefix rule); an index on `(a, b)` doesn't serve `WHERE b = ?`.
- Functions/casts on indexed columns in predicates (`WHERE DATE(created_at) = ?`, implicit collation/type casts) defeat the index — check join columns have matching types/collations.
- Leading-wildcard `LIKE '%x%'`; `OR` conditions that prevent index use; `NOT IN` with nullable subqueries (returns nothing when a NULL appears).
- New index on a hot write table: write amplification acknowledged; near-duplicate of an existing index?
- Unbounded result sets: missing LIMIT/pagination. **Offset pagination degrades linearly** — keyset/cursor pagination for large or hot tables.
- For a genuinely new heavy query, ask for/run `EXPLAIN` on realistic data volume — dev-sized tables make every query fast.

## Transactions & Isolation

- Read-modify-write races: `SELECT` then `UPDATE` on the same row needs `FOR UPDATE`, an atomic `UPDATE ... SET x = x + ?`, optimistic version column, or a unique constraint absorbing the race.
- Isolation assumptions explicit: default READ COMMITTED allows non-repeatable reads between two statements in one transaction — code assuming otherwise is wrong.
- Upserts: `INSERT ... ON CONFLICT` / `ON DUPLICATE KEY` instead of check-then-insert; unique constraint exists to back it.
- Deadlock exposure: transactions locking multiple rows/tables in inconsistent order; long transactions holding locks across slow work.
- Advisory/row locks have timeouts (`lock_timeout`, `innodb_lock_wait_timeout` awareness) so a stuck holder doesn't queue the world.

## Data Operations in Application Code

- N+1 confirmed by finding the loop and the per-iteration query; batch with `IN (...)` (bounded batch size — a 100k-element IN list is its own problem).
- `SELECT *` on wide/hot tables when three columns are used; large text/blob columns fetched by default.
- Row-by-row inserts/updates in loops vs bulk operations; huge result sets loaded into memory vs streaming/chunking.
- Retries around DB calls: only where idempotent; serialization-failure retries where isolation level demands them.
