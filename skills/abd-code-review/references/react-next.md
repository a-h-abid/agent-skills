# React / Next.js — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches React/Next.js code.

## Correctness

- **UI state matches backend reality**: loading, empty, error, retry, unauthorized states for every new fetch/mutation; optimistic updates rolled back on failure; cache invalidation after mutations (React Query/SWR `invalidateQueries`, Next.js `revalidatePath`/`revalidateTag`).
- Hook rules: conditional hooks; `useEffect` dependency arrays missing values (stale closures) or over-including (loops); effects that should be event handlers or derived state.
- Effect cleanup: subscriptions/listeners/intervals removed; async effect results discarded after unmount or when a newer request superseded them (race → stale overwrite).
- `useState` from props without sync intent (stale copies); state updates depending on previous state not using the updater form.
- Keys on lists: stable identity, not array index when the list reorders/filters.

## Security

- XSS: `dangerouslySetInnerHTML` with user-influenced content; `javascript:` URLs in `href`; markdown renderers with raw HTML enabled.
- **Server/client boundary (App Router)**: secrets imported into client components ship to the browser (`NEXT_PUBLIC_` is public by definition); server-only modules marked (`server-only` package); Server Actions validate input and check authz — they're public endpoints, not internal functions.
- Middleware-only auth checks: Next.js middleware is advisory routing — the data access itself (route handlers, server components, actions) must enforce authz.
- Tokens in `localStorage` vs httpOnly cookies; PII in client-side analytics/logs.

## Performance

- Re-render pressure: new object/array/function literals passed to memoized children; context values recreated per render; state placed high in the tree when only a leaf needs it.
- `useMemo`/`useCallback` where measurement justifies it — and missing where an expensive computation runs per keystroke.
- Bundle: heavy client components that could be server components; dynamic `import()` for modal/rare paths; full-library imports.
- Waterfalls: sequential awaits in server components that could be parallel (`Promise.all`); fetch-in-child patterns causing request cascades; N+1 fetches per list item.
- Images via `next/image` (sizing, lazy loading); fonts via `next/font`.

## Next.js Specifics

- Rendering mode intentional: static vs dynamic (accidental `cookies()`/`headers()` call opting a page out of static); ISR revalidate values sane; `cache: "no-store"` vs default fetch caching — data freshness matches the product need.
- Route handlers are backend endpoints — full backend layers apply (validation, authz, rate limits, timeouts).
- Server/client component boundaries: `"use client"` pushed as low as possible; serializable props across the boundary.
- Hydration mismatches: browser-only values (time, random, locale, `window`) rendered on the server; guard with effects or `suppressHydrationWarning` only when justified.

## State & Data

- Server state in a server-cache library (React Query/SWR) vs hand-rolled `useEffect` fetching with its race/retry/cache gaps.
- Global stores reset on logout/tenant switch; nothing sensitive persisted to storage.
- Double-submit protection on forms; `AbortController` or request-identity checks for rapid navigation/typeahead.

## Accessibility

- Interactive elements are real `button`/`a`/`label`, keyboard operable; focus managed on modals/route changes (trap, restore); `Escape` closes overlays.
- Form inputs labeled; validation errors associated (`aria-describedby`) and announced (`aria-live`); color not the only signal; contrast on new UI.

## Tests

- Testing Library queries by role/label (user-visible behavior), not test-ids/implementation internals, where practical.
- New conditional states (loading/error/empty/unauthorized) each rendered in a test; async assertions properly awaited (`findBy`, `waitFor`) — no bare `getBy` after an async update.
