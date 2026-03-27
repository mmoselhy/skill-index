# Go Standard Library Patterns

## Error Handling

- **Wrap errors with context** using `%w` to preserve the chain:
  ```go
  if err != nil {
      return fmt.Errorf("fetching user %d: %w", id, err)
  }
  ```
- **Check wrapped errors with `errors.Is()` and `errors.As()`**, not `==`:
  ```go
  if errors.Is(err, sql.ErrNoRows) {
      return nil, ErrNotFound
  }

  var pgErr *pgconn.PgError
  if errors.As(err, &pgErr) {
      log.Println("pg code:", pgErr.Code)
  }
  ```
- **Define sentinel errors** as package-level variables:
  ```go
  var ErrNotFound = errors.New("not found")
  ```

## Context

- **`context.Context` is always the first parameter**:
  ```go
  func GetUser(ctx context.Context, id int) (*User, error) {
      // ...
  }
  ```
- **Propagate context through the call chain** -- never store it in a struct
- **Use `context.WithTimeout` for deadlines** on external calls:
  ```go
  ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
  defer cancel()
  ```

## Testing

- **Use table-driven tests with `t.Run()` subtests**:
  ```go
  tests := []struct {
      name    string
      input   string
      want    int
      wantErr bool
  }{
      {"valid input", "42", 42, false},
      {"empty string", "", 0, true},
  }
  for _, tt := range tests {
      t.Run(tt.name, func(t *testing.T) {
          got, err := Parse(tt.input)
          if (err != nil) != tt.wantErr {
              t.Fatalf("unexpected error: %v", err)
          }
          if got != tt.want {
              t.Errorf("Parse(%q) = %d, want %d", tt.input, got, tt.want)
          }
      })
  }
  ```
- **Use `t.Helper()`** in test helper functions to get correct line numbers on failure

## Interfaces

- **Keep interfaces small** -- one to three methods maximum
- **Accept interfaces, return structs** -- define interfaces at the call site, not the implementation:
  ```go
  type UserStore interface {
      GetUser(ctx context.Context, id int) (*User, error)
  }

  func NewService(store UserStore) *Service {
      return &Service{store: store}
  }
  ```

## Resource Cleanup

- **Use `defer` immediately after acquiring a resource**:
  ```go
  f, err := os.Open(path)
  if err != nil {
      return err
  }
  defer f.Close()
  ```
- **`defer` runs in LIFO order** -- later defers execute first
