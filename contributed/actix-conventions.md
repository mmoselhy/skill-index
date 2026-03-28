# Actix Web Conventions

## Handler Functions

- **Handlers return `impl Responder`** and use extractors as function parameters:
  ```rust
  async fn get_user(path: web::Path<i32>, db: web::Data<DbPool>) -> impl Responder {
      let user_id = path.into_inner();
      match db.find_user(user_id).await {
          Ok(user) => HttpResponse::Ok().json(user),
          Err(_) => HttpResponse::NotFound().json(ErrorResponse::not_found("user")),
      }
  }
  ```
- **Keep handlers thin** -- extract business logic into service modules

## Extractors

- **`web::Path<T>`** for URL path segments: `/users/{id}`
- **`web::Json<T>`** for JSON request bodies (T must implement `Deserialize`):
  ```rust
  async fn create_user(body: web::Json<CreateUserRequest>) -> impl Responder {
      let req = body.into_inner();
      // ...
  }
  ```
- **`web::Query<T>`** for query string parameters: `?page=1&limit=20`
- **`web::Data<T>`** for shared application state injected at startup
- **Extractor order in function signature does not matter** -- Actix resolves by type

## Error Handling

- **Implement `ResponseError` on custom error types** for automatic conversion:
  ```rust
  #[derive(Debug, thiserror::Error)]
  enum AppError {
      #[error("not found: {0}")]
      NotFound(String),
      #[error("internal error")]
      Internal(#[from] anyhow::Error),
  }

  impl ResponseError for AppError {
      fn error_response(&self) -> HttpResponse {
          match self {
              AppError::NotFound(msg) => HttpResponse::NotFound().json(json!({"error": msg})),
              AppError::Internal(_) => HttpResponse::InternalServerError().finish(),
          }
      }
  }
  ```
- **Handlers can then return `Result<impl Responder, AppError>`** for ergonomic `?` usage

## App Configuration

- **Share state with `web::Data`** wrapped in `Arc` if needed:
  ```rust
  let pool = web::Data::new(create_pool().await);
  HttpServer::new(move || {
      App::new()
          .app_data(pool.clone())
          .service(web::resource("/users").route(web::get().to(list_users)))
  })
  ```
- **Use `.service()` and `.resource()` for route grouping**:
  ```rust
  App::new()
      .service(
          web::scope("/api/v1")
              .service(web::resource("/users").route(web::get().to(list_users)))
              .service(web::resource("/users/{id}").route(web::get().to(get_user)))
      )
  ```

## Middleware

- **Apply middleware with `.wrap()`** for struct-based middleware or **`.wrap_fn()`** for closures:
  ```rust
  App::new()
      .wrap(middleware::Logger::default())
      .wrap(middleware::Compress::default())
      .wrap_fn(|req, srv| {
          let start = Instant::now();
          let fut = srv.call(req);
          async move {
              let res = fut.await?;
              log::info!("request took {:?}", start.elapsed());
              Ok(res)
          }
      })
  ```
