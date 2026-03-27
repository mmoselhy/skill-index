# Tokio Async Patterns

## Entry Point

- **Use `#[tokio::main]` on `main`** to set up the runtime:
  ```rust
  #[tokio::main]
  async fn main() -> anyhow::Result<()> {
      let listener = TcpListener::bind("0.0.0.0:8080").await?;
      serve(listener).await
  }
  ```
- **Use `#[tokio::test]` for async tests** -- each test gets its own runtime

## Spawning Tasks

- **Use `tokio::spawn` for concurrent work** that runs independently:
  ```rust
  let handle = tokio::spawn(async move {
      process_job(job).await
  });
  let result = handle.await?;
  ```
- **Spawned tasks must be `Send + 'static`** -- no borrowed references across `.await`
- **Use `JoinSet` to manage multiple spawned tasks**:
  ```rust
  let mut set = JoinSet::new();
  for item in items {
      set.spawn(async move { process(item).await });
  }
  while let Some(result) = set.join_next().await {
      result??;
  }
  ```

## Select and Racing

- **Use `tokio::select!` to race multiple futures**:
  ```rust
  tokio::select! {
      msg = rx.recv() => handle_message(msg),
      _ = tokio::signal::ctrl_c() => {
          println!("shutting down");
          return Ok(());
      }
  }
  ```
- **Pin futures that are polled across loop iterations** with `tokio::pin!`

## Channels

- **`mpsc` for fan-in work queues** (multiple producers, single consumer):
  ```rust
  let (tx, mut rx) = tokio::sync::mpsc::channel(100);
  tokio::spawn(async move {
      while let Some(job) = rx.recv().await {
          process(job).await;
      }
  });
  tx.send(job).await?;
  ```
- **`oneshot` for request-response** patterns:
  ```rust
  let (reply_tx, reply_rx) = tokio::sync::oneshot::channel();
  tx.send(Command::Get { key, reply: reply_tx }).await?;
  let value = reply_rx.await?;
  ```
- **`broadcast` for fan-out** when multiple consumers need the same message

## Graceful Shutdown

- **Use `tokio::signal` to catch OS signals**:
  ```rust
  let shutdown = tokio::signal::ctrl_c();
  tokio::select! {
      _ = server.run() => {},
      _ = shutdown => {
          println!("received shutdown signal");
          server.stop().await;
      }
  }
  ```

## Error Handling

- **Use `anyhow::Result` in application code** for ergonomic error propagation
- **Use custom error enums with `thiserror` in library code** for typed errors:
  ```rust
  #[derive(Debug, thiserror::Error)]
  enum DbError {
      #[error("connection failed: {0}")]
      Connection(#[from] tokio_postgres::Error),
      #[error("record not found")]
      NotFound,
  }
  ```
- **Never `.unwrap()` on channel sends in production** -- the receiver may have dropped
