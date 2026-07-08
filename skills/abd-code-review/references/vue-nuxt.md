# Vue / Nuxt Frontend — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches Vue/Nuxt code. Each section extends the same-named universal layer.

## Correctness

- **UI state matches backend reality**: loading, empty, error, retry, unauthorized/permission-denied, and disabled states for every new fetch/mutation; optimistic updates rolled back on server failure.
- Reactivity loss: destructuring a `reactive()` object (use `toRefs`/`storeToRefs` for Pinia); mutating props; `ref` vs `reactive` `.value` mistakes; watching a getter vs the whole object (`deep` semantics).
- `v-if` vs `v-show` on components with expensive setup or side-effectful lifecycle; `key` on `v-for` (and not the array index when the list reorders/filters — state bleeds between rows).
- Async `setup()`/`await` in components without `<Suspense>` or proper loading handling.
- Computed properties with side effects, or that depend on non-reactive sources (won't update).
- Form state after mutation: stale data left in fields, client cache/store not invalidated after a write.

## Security

- **XSS**: `v-html` with any user-influenced content; sanitize or don't render raw. URL bindings (`:href`, `:src`) with `javascript:` schemes from user data.
- Secrets/internal URLs leaking into the client bundle — in Nuxt, anything in `runtimeConfig.public` or imported into client code ships to the browser. Server-only keys belong in `runtimeConfig` (private) and server routes.
- Auth checks in client middleware/components are UX, not security — verify the server enforces the same rule (route middleware runs client-side after hydration for SPA navigation).
- Tokens in `localStorage` vs httpOnly cookies — flag new persistence of session material; PII sent to analytics.

## Performance

- Bundle size: heavy libraries imported eagerly into the entry chunk vs dynamic `import()`/lazy components; full-library imports (lodash, icon packs) where per-function imports exist.
- Request waterfalls: sequential `await useFetch` chains that could be parallel; over-fetching on navigation for data already in the store.
- Re-render pressure: large lists without virtualization; expensive computed re-evaluating on unrelated state; watchers doing heavy work on every keystroke without debounce.
- Images unoptimized/unsized (layout shift); missing `loading="lazy"` on below-fold media.

## Nuxt SSR Specifics

- **Server/client state bleed**: module-level or plugin singleton state on the server is shared across all requests — per-request state must live in `useState`/Pinia/`nuxtApp` context. This is the SSR equivalent of a data race, and it leaks one user's data to another.
- Hydration mismatches: markup depending on browser-only values (`window`, locale, time, random) rendered on server; guard with `ClientOnly`/`onMounted`.
- `useFetch`/`useAsyncData` keys unique and stable (duplicate keys share cached data across unrelated components); `server: false` vs SSR intent; payload size shipped to client.
- Browser APIs (`window`, `document`, `localStorage`) touched during SSR without guards — crashes the server render.
- Nuxt server routes (`server/api/`) are backend endpoints — apply the full backend security layers (validation, authz, rate limits), not frontend standards.

## Reliability

- Fetch error handling: `useFetch` `error` actually consumed and rendered, not ignored; retries/backoff for flaky-but-important calls; global error boundary (`NuxtErrorBoundary`/`onErrorCaptured`) for new risky trees.
- Race conditions between rapid navigations/clicks: stale responses overwriting newer state (abort or compare request identity); double-submit protection on forms.
- Third-party script failures don't block core flows.

## Accessibility & UX

- Keyboard reachable and operable: focus management on modals/drawers (trap, restore on close), `Escape` handling; visible focus states preserved.
- Semantic elements over div+click (`button`, `a`, `label`); ARIA only where semantics can't do it; form inputs labeled; errors announced (`aria-live`) not just colored.
- Color contrast on new UI; text alternatives for icons/images that carry meaning.
- i18n: user-facing strings through the translation layer, not hardcoded; dates/numbers/currency formatted per locale; pluralization handled.

## State Management (Pinia)

- Store state normalized enough that a mutation in one view can't leave another view stale; actions the single write path, not components mutating store state ad hoc.
- Store reset on logout/tenant switch — cached data from the previous user is a data leak.
- Persisted store state (plugins) versioned/migratable; nothing sensitive persisted.

## Tests

- Component tests assert user-visible behavior (rendered text, emitted events, a11y roles) not internal implementation (data properties, method calls).
- New conditional states (loading/error/empty/permission) each have a test; store logic unit-tested where it carries business rules.
