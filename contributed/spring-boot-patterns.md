# Spring Boot Patterns

## Layered Architecture

- **Controller -> Service -> Repository** is the standard call chain
- **Controllers handle HTTP concerns only** -- status codes, request/response mapping:
  ```java
  @RestController
  @RequestMapping("/api/v1/users")
  public class UserController {
      private final UserService userService;

      public UserController(UserService userService) {
          this.userService = userService;
      }

      @GetMapping("/{id}")
      public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
          return ResponseEntity.ok(userService.findById(id));
      }
  }
  ```
- **Services contain business logic** and are annotated with `@Service`
- **Repositories extend `JpaRepository<T, ID>`** for data access

## Dependency Injection

- **Use constructor injection**, not `@Autowired` on fields:
  ```java
  @Service
  public class UserService {
      private final UserRepository userRepository;
      private final EmailService emailService;

      // Spring auto-injects when there is a single constructor
      public UserService(UserRepository userRepository, EmailService emailService) {
          this.userRepository = userRepository;
          this.emailService = emailService;
      }
  }
  ```
- **Constructor injection makes dependencies explicit** and enables easy unit testing

## Error Handling

- **Use `@RestControllerAdvice` for global exception handling**:
  ```java
  @RestControllerAdvice
  public class GlobalExceptionHandler {
      @ExceptionHandler(ResourceNotFoundException.class)
      public ResponseEntity<ErrorResponse> handleNotFound(ResourceNotFoundException ex) {
          return ResponseEntity.status(HttpStatus.NOT_FOUND)
              .body(new ErrorResponse("NOT_FOUND", ex.getMessage()));
      }
  }
  ```
- **Define custom exceptions extending `RuntimeException`**:
  ```java
  public class ResourceNotFoundException extends RuntimeException {
      public ResourceNotFoundException(String resource, Long id) {
          super(String.format("%s with id %d not found", resource, id));
      }
  }
  ```

## Transactions

- **Place `@Transactional` on service methods**, not on repository or controller:
  ```java
  @Transactional
  public UserDto createUser(CreateUserRequest request) {
      User user = userRepository.save(toEntity(request));
      emailService.sendWelcome(user.getEmail());
      return toDto(user);
  }
  ```
- **Use `@Transactional(readOnly = true)`** for read-only operations to enable query optimizations

## Testing

- **`@SpringBootTest`** loads the full application context for integration tests
- **`@WebMvcTest(UserController.class)`** loads only the web layer for fast controller tests:
  ```java
  @WebMvcTest(UserController.class)
  class UserControllerTest {
      @Autowired
      private MockMvc mockMvc;

      @MockBean
      private UserService userService;

      @Test
      void getUser_returnsUser() throws Exception {
          when(userService.findById(1L)).thenReturn(testUser());
          mockMvc.perform(get("/api/v1/users/1"))
              .andExpect(status().isOk())
              .andExpect(jsonPath("$.name").value("Alice"));
      }
  }
  ```

## Configuration

- **Use `application.yml`** over `application.properties` for readability
- **Bind config groups to typed classes** with `@ConfigurationProperties`:
  ```java
  @ConfigurationProperties(prefix = "app.mail")
  public record MailConfig(String host, int port, String from) {}
  ```
