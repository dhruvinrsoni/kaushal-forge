---
name: api-design
description: >
  REST API design conventions for Spring Boot 3+ — naming, HTTP verbs,
  validation, error handling, and response patterns.
metadata:
  version: "1.0.0"
  reasoning_mode: linear
---

# REST API Design — Spring Boot

## URL Naming Conventions

| Pattern | Example | Note |
|---------|---------|------|
| Plural nouns for collections | `GET /api/users` | Not `/getUsers` |
| Singular noun for item | `GET /api/users/{id}` | |
| Nested resources | `GET /api/users/{id}/orders` | Max 2 levels deep |
| Query params for filtering | `GET /api/users?role=admin&page=0` | Not a path segment |
| Lowercase, hyphenated | `/api/order-items` | Not camelCase |

## HTTP Verbs

| Verb | Purpose | Response |
|------|---------|----------|
| `GET` | Retrieve | 200 OK |
| `POST` | Create | 201 Created + Location header |
| `PUT` | Full replace | 200 OK |
| `PATCH` | Partial update | 200 OK |
| `DELETE` | Remove | 204 No Content |

## Controller Pattern

```java
@RestController
@RequestMapping("/api/users")
@Validated
public class UserController {

    private final UserService userService;

    // Constructor injection (not @Autowired field injection)
    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }

    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        UserResponse created = userService.create(request);
        URI location = URI.create("/api/users/" + created.id());
        return ResponseEntity.created(location).body(created);
    }
}
```

## Validation with Jakarta

```java
public record CreateUserRequest(
    @NotBlank @Size(min = 2, max = 100) String name,
    @Email @NotBlank String email,
    @Min(0) @Max(150) Integer age
) {}
```

## Global Error Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(EntityNotFoundException.class)
    public ProblemDetail handleNotFound(EntityNotFoundException ex) {
        ProblemDetail detail = ProblemDetail.forStatus(HttpStatus.NOT_FOUND);
        detail.setTitle("Resource Not Found");
        detail.setDetail(ex.getMessage());
        return detail;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail detail = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
        detail.setTitle("Validation Failed");
        detail.setProperty("errors", ex.getBindingResult().getFieldErrors()
            .stream().map(e -> e.getField() + ": " + e.getDefaultMessage())
            .toList());
        return detail;
    }
}
```

## Response DTOs

Use Java `record` for immutable DTOs:
```java
public record UserResponse(Long id, String name, String email, Instant createdAt) {}
```

Map entities → DTOs in the service layer, never in controllers or repositories.

## Conventions Summary

- **No business logic in controllers** — delegate to service layer
- **No SQL in controllers** — use repository layer
- **Request DTOs for input** — never expose entity directly via `@RequestBody`
- **Response DTOs for output** — never return JPA entities directly (lazy-loading pitfalls)
- **Use `ProblemDetail`** (RFC 9457) for error responses — Spring Boot 3 supports natively
