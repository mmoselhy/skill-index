# FastAPI Conventions

## Router Organization

- **One router per domain**, mounted in the main app. Keep route handlers thin:
  ```python
  # app/routers/users.py
  router = APIRouter(prefix="/users", tags=["users"])

  @router.get("/{user_id}", response_model=UserOut)
  async def get_user(user_id: int, db: Session = Depends(get_db)):
      user = user_service.get_by_id(db, user_id)
      if not user:
          raise HTTPException(status_code=404, detail="User not found")
      return user
  ```
- **Mount routers in `main.py`**, not nested inside each other:
  ```python
  app = FastAPI()
  app.include_router(users.router)
  app.include_router(orders.router)
  ```

## Dependency Injection

- **Use `Depends()` for shared resources** like database sessions, current user, and config. Never use module-level global state:
  ```python
  async def get_current_user(token: str = Depends(oauth2_scheme)):
      user = decode_token(token)
      if not user:
          raise HTTPException(status_code=401, detail="Invalid token")
      return user

  @router.get("/me")
  async def read_profile(user: User = Depends(get_current_user)):
      return user
  ```
- **Chain dependencies** for layered auth: `get_current_user -> require_admin`.

## Request and Response Models

- **Separate Pydantic models for input vs output.** Never reuse the ORM model directly:
  ```python
  class UserCreate(BaseModel):
      email: str
      password: str

  class UserOut(BaseModel):
      id: int
      email: str
      model_config = ConfigDict(from_attributes=True)
  ```

## Error Handling

- **Use `HTTPException` with consistent status codes.** 400 for bad input, 404 for missing resources, 409 for conflicts, 422 is auto-handled by Pydantic.
- **Add a custom exception handler** for domain exceptions that should not leak internals:
  ```python
  @app.exception_handler(DomainError)
  async def domain_error_handler(request, exc):
      return JSONResponse(status_code=400, content={"detail": str(exc)})
  ```

## Background Tasks

- **Use `BackgroundTasks` for fire-and-forget work** like sending emails or logging analytics:
  ```python
  @router.post("/signup")
  async def signup(user: UserCreate, bg: BackgroundTasks):
      created = user_service.create(user)
      bg.add_task(send_welcome_email, created.email)
      return created
  ```

## Middleware Ordering

- **Middleware executes in reverse registration order.** Register CORS first (outermost), then auth, then request-id. The last registered middleware wraps the innermost layer.

## Path Operation Best Practices

- **Use `status_code=201` on creation endpoints.** Return the created resource.
- **Use `response_model` to control serialization**, not manual dict conversion.
- **Use `Path()` and `Query()` for validation** on path and query parameters with descriptions for auto-docs.
