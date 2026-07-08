# Kotlin / Android — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches Kotlin or Android code. Each section extends the same-named universal layer.

## Correctness

- Force-unwrap `!!` and unguarded nullable access — especially on data from intents, bundles, JSON, or platform callbacks that can legitimately be null.
- Platform types (values from Java APIs) treated as non-null without validation.
- `lateinit` accessed before initialization on paths the author didn't trace (process death/restore, early callbacks).
- Data class `copy()` sharing mutable collection references; `equals`/`hashCode` semantics when a data class holds arrays.
- `when` on sealed classes/enums without exhaustive branches (statement form compiles without `else` and silently skips new variants — prefer expression form).
- Serialization: `@Serializable`/Moshi/Gson field defaults and nullability matching the actual JSON; proguard/R8 rules for reflective serializers.

## Security

- Sensitive data in `SharedPreferences`/files unencrypted (use EncryptedSharedPreferences/Keystore); secrets or API keys in `BuildConfig`/resources shipped in the APK.
- Exported components (`android:exported="true"` — explicit since API 31): activities/receivers/services accepting untrusted intents; intent extras validated.
- WebView: `setJavaScriptEnabled` + `addJavascriptInterface` with untrusted content; `file://` access; deep links validated before acting.
- PII in logs (`Log.d` survives in release unless stripped); crash-reporting breadcrumbs carrying tokens.
- Certificate pinning / cleartext traffic config for sensitive endpoints.

## Performance

- Main-thread I/O: DB/network/disk on `Dispatchers.Main`; Room queries without `suspend`/Flow off-thread.
- Jetpack Compose: unstable lambdas/parameters causing recomposition storms; `remember`/`derivedStateOf` missing for computed state; keys on `LazyColumn` items.
- Bitmap/image loading unscaled; memory leaks via Activity/Context captured in singletons, companion objects, or long-lived coroutines.
- N+1 against Room/network in loops; missing `@Transaction` on multi-query DAO reads.

## Reliability

- Network calls with timeouts (OkHttp defaults are finite but verify custom clients); Retrofit error bodies handled, not just `isSuccessful` ignored.
- Offline/poor-network behavior: retries, cached state, user-visible error states.
- Process death: state restored (`SavedStateHandle`, `onSaveInstanceState`); long work moved to `WorkManager` with constraints and idempotent workers, not a fire-and-forget coroutine.
- App-version skew: server contract changes tolerated by older shipped clients (you can't force-update mobile).

## Concurrency & Coroutines

- **Scope discipline**: coroutines launched in `GlobalScope` or a custom scope that outlives the screen (leak) vs `viewModelScope`/`lifecycleScope`; jobs cancelled with their owner.
- Blocking calls (`runBlocking`, `Thread.sleep`, sync I/O) on `Dispatchers.Main` or inside `suspend` functions without `withContext(Dispatchers.IO)`.
- Shared mutable state across coroutines without `Mutex`/`StateFlow`/atomic — especially view-model fields updated from multiple collectors.
- `Flow` collection: `collect` on Main vs `flowOn`; `stateIn`/`shareIn` scope and started-policy deliberate; cold flows re-triggering work per collector unintentionally.
- Cancellation cooperation: long CPU loops without `ensureActive()`/`yield()`; `try/catch (e: Exception)` swallowing `CancellationException` (must be rethrown).
- `SupervisorJob` vs regular `Job`: one child failure cancelling siblings unintentionally (or the reverse — failures silently isolated).

## Deploy & Data

- Room migrations provided for schema changes (`fallbackToDestructiveMigration` wipes user data — never ship silently); migration tests present.
- Feature rollout: server-driven flags for risky features (a bad release can't be rolled back from users' devices quickly).

## Tests

- Coroutine tests use `runTest`/`TestDispatcher` with injected dispatchers — `Dispatchers.Main` hardcoded makes logic untestable and flaky.
- ViewModel logic tested off-device; screenshot/UI tests for changed Compose components where visual behavior is the contract.
