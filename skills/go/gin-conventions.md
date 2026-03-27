# Gin Web Framework Conventions

## Router Organization

- **Group routes by API version and domain** using `r.Group()`:
  ```go
  v1 := r.Group("/api/v1")
  {
      users := v1.Group("/users")
      users.GET("", listUsers)
      users.POST("", createUser)
      users.GET("/:id", getUser)
  }
  ```
- **Keep route registration in a dedicated function** like `setupRoutes(r *gin.Engine)` to avoid cluttering `main()`

## Middleware

- **Chain middleware in order**: recovery first, then logging, then auth:
  ```go
  r := gin.New()
  r.Use(gin.Recovery())
  r.Use(gin.Logger())
  r.Use(authMiddleware())
  ```
- **Scope auth middleware to protected groups only** rather than applying globally:
  ```go
  admin := v1.Group("/admin")
  admin.Use(authMiddleware())
  ```

## Request Handling

- **Use `ShouldBindJSON()` over `BindJSON()`** to control error responses yourself:
  ```go
  var req CreateUserRequest
  if err := c.ShouldBindJSON(&req); err != nil {
      c.AbortWithStatusJSON(http.StatusBadRequest, ErrorResponse{
          Code:    "INVALID_REQUEST",
          Message: err.Error(),
      })
      return
  }
  ```
- **Handler signature is always `func(c *gin.Context)`** -- return values go through `c.JSON()`, not `return`

## Response Patterns

- **Use `c.JSON()` for success responses**:
  ```go
  c.JSON(http.StatusOK, gin.H{"user": user})
  ```
- **Use `c.AbortWithStatusJSON()` for errors** to stop middleware chain execution
- **Define a standard error response struct** used across all handlers:
  ```go
  type ErrorResponse struct {
      Code    string `json:"code"`
      Message string `json:"message"`
  }
  ```

## Handler Structure

- **One handler per function** -- avoid anonymous functions in route registration
- **Validate early, return early** -- check binding and auth before business logic
- **Keep handlers thin** -- delegate to service layer, handlers only translate HTTP to domain calls
