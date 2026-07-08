# Java / Spring — Stack-Specific Checks

Apply these on top of the universal layers when the diff touches Java/Spring code.

## Correctness

- `Optional` misuse: `.get()` without presence check; `Optional` fields/parameters as a null-substitute; `orElse(expensiveCall())` evaluating eagerly vs `orElseGet`.
- `equals`/`hashCode` contract on entities used in collections; comparing with `==` where `.equals` is needed (boxed types, strings).
- BigDecimal: `equals` vs `compareTo` (scale!); float/double for money; `new BigDecimal(0.1)` vs `BigDecimal.valueOf`.
- Checked exceptions wrapped and rethrown without cause; `catch (Exception e) {}` swallowing; exceptions in streams/lambdas silently smothered.
- Time: `java.util.Date`/`Calendar` in new code vs `java.time`; zone handling explicit.

## Security

- SQL: string-concatenated JPQL/native queries; use named/positional parameters. MyBatis `${}` vs `#{}`.
- Spring Security: new endpoints matched by the security config (an unmatched path may default open or closed — verify which); method security (`@PreAuthorize`) actually enabled; CSRF disabled deliberately or by copy-paste?
- Deserialization: Jackson polymorphic typing (`@JsonTypeInfo`, default typing) on untrusted input; native Java deserialization; XML parsers without XXE protection.
- SpEL injection (user input into expression parsing); path traversal on file endpoints; mass assignment via direct entity binding from request bodies (use DTOs).
- Actuator endpoints exposed without auth in new config.

## Performance & JPA Pitfalls

- **N+1**: lazy relations accessed in loops/serialization — `JOIN FETCH`/`@EntityGraph`; `spring.jpa.open-in-view` masking it (queries from the view layer).
- `findAll()` unbounded; pagination with `Pageable`; `@Transactional(readOnly = true)` for read paths (dirty-checking cost).
- LazyInitializationException risk: entities escaping the transaction then touched.
- Streams over huge results vs scrollable/keyset pagination; entity-to-DTO mapping pulling whole graphs.

## Reliability & Transactions

- **`@Transactional` self-invocation does nothing** (proxy-based) — a public method calling its own `@Transactional` method skips the transaction. Same trap for `@Async`, `@Cacheable`, `@Retryable`.
- `@Transactional` on private methods (ignored); checked exceptions don't roll back by default (`rollbackFor`).
- Transactions spanning external HTTP/queue calls; `TransactionalEventListener(AFTER_COMMIT)` for post-commit side effects.
- HTTP clients (RestTemplate/WebClient/Feign) with explicit connect/read timeouts — defaults vary and some are infinite.
- Thread pools bounded with rejection policy; `@Async` executor configured (default is unbounded in older setups).

## Concurrency

- Singleton beans (the default scope) holding mutable per-request state — instance fields on controllers/services are shared across all requests.
- `SimpleDateFormat` and other non-thread-safe classes as shared fields.
- Check-then-act on shared maps vs `ConcurrentHashMap.compute*`; double-checked locking without `volatile`.

## Tests

- `@SpringBootTest` where a slice (`@WebMvcTest`, `@DataJpaTest`) suffices (speed); security filters included when testing auth-sensitive endpoints (`@AutoConfigureMockMvc` + security).
- Testcontainers or embedded DB matching production engine for query-shape claims; H2 dialect differences can hide real bugs.
