---
name: database
description: >
  Spring Data JPA patterns for Spring Boot 3+ — repositories, transactions,
  entity design, migration with Flyway, and common pitfalls.
metadata:
  version: "1.0.0"
  reasoning_mode: linear
---

# Database Patterns — Spring Boot / JPA

## Repository Pattern

```java
// Extend JpaRepository — gives you save, findById, findAll, delete, etc.
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // Spring Data derives SQL from method names
    Optional<User> findByEmail(String email);
    List<User> findByRoleOrderByCreatedAtDesc(Role role);

    // Custom JPQL for complex queries
    @Query("SELECT u FROM User u WHERE u.createdAt > :since AND u.active = true")
    List<User> findActiveUsersSince(@Param("since") Instant since);
}
```

**Never** write raw JDBC or `EntityManager` queries in controllers. Always go through a `@Repository`.

## Transaction Boundaries

```java
@Service
@Transactional(readOnly = true)  // Default for whole service: read-only
public class UserService {

    @Transactional  // Overrides to read-write for mutations
    public UserResponse create(CreateUserRequest request) {
        // All DB operations here run in one transaction
        User user = new User(request.name(), request.email());
        return toResponse(userRepository.save(user));
    }

    public UserResponse findById(Long id) {
        // Inherits readOnly = true — no transaction overhead for reads
        return userRepository.findById(id)
            .map(this::toResponse)
            .orElseThrow(() -> new EntityNotFoundException("User not found: " + id));
    }
}
```

**Key rules:**
- `@Transactional` belongs on **service layer**, not controllers or repositories
- Use `readOnly = true` for queries — better performance, prevents accidental writes
- Never catch and swallow exceptions inside `@Transactional` — it prevents rollback

## Entity Design

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    @CreatedDate
    @Column(updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;

    // JPA requires no-arg constructor (can be protected)
    protected User() {}

    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }
}
```

## Flyway Migration Strategy

Add dependency: `org.flywaydb:flyway-core`

Migration files in `src/main/resources/db/migration/`:
```
V1__create_users_table.sql
V2__add_role_to_users.sql
V3__create_orders_table.sql
```

**Naming convention:** `V{version}__{description}.sql` (double underscore)

Rules:
- **Never modify an existing migration file** — it will break Flyway checksum validation
- Always create a new migration for schema changes
- Test migrations on a clean DB before PR

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| `LazyInitializationException` in REST response | Return DTO, not entity. Map in service layer. |
| N+1 query problem | Use `@EntityGraph` or JOIN FETCH in repository |
| Transaction on `private` method | Spring AOP can't proxy private — use `public` |
| Missing `@Transactional` on multi-step operation | Wrap entire operation in one service method |
| H2 in-memory for production | Use PostgreSQL/MySQL; H2 only for unit tests |
