# Structlog Logging Patterns

## Configuration with Processor Chains

- **Configure structlog once at application startup**, not per-module. Set the processor chain to build structured events:
  ```python
  import structlog

  structlog.configure(
      processors=[
          structlog.contextvars.merge_contextvars,
          structlog.processors.add_log_level,
          structlog.processors.TimeStamper(fmt="iso"),
          structlog.processors.StackInfoRenderer(),
          structlog.processors.format_exc_info,
          structlog.processors.JSONRenderer(),
      ],
      wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
      context_class=dict,
      logger_factory=structlog.PrintLoggerFactory(),
      cache_logger_on_first_use=True,
  )
  ```

## Logger Per Module

- **Call `structlog.get_logger()` at the top of each module.** Bind the module name for traceability:
  ```python
  import structlog

  logger = structlog.get_logger(__name__)

  def process_order(order_id: int):
      logger.info("processing_order", order_id=order_id)
  ```

## Bound Loggers for Request Context

- **Bind request-scoped values once**, then use the bound logger throughout the request lifecycle:
  ```python
  @app.middleware("http")
  async def logging_middleware(request, call_next):
      request_id = request.headers.get("X-Request-ID", str(uuid4()))
      structlog.contextvars.clear_contextvars()
      structlog.contextvars.bind_contextvars(request_id=request_id)
      response = await call_next(request)
      return response
  ```
- **Use `contextvars` integration** (structlog 21.1+) instead of thread-local bound loggers. It works correctly with async code.

## Key-Value Structured Events

- **Use snake_case event names** as the first argument. Pass context as keyword arguments, not formatted strings:
  ```python
  # Good: structured, searchable, parseable
  logger.info("payment_processed", amount=99.99, currency="USD", user_id=42)

  # Bad: unstructured string interpolation
  logger.info(f"Processed payment of $99.99 USD for user 42")
  ```
- **Keep event names stable.** They are the primary key for searching logs. Change them intentionally.

## Integration with stdlib logging

- **Route stdlib logging through structlog** so third-party libraries produce structured output too:
  ```python
  structlog.configure(
      logger_factory=structlog.stdlib.LoggerFactory(),
      wrapper_class=structlog.stdlib.BoundLogger,
      processors=[
          structlog.stdlib.filter_by_level,
          structlog.stdlib.add_logger_name,
          structlog.stdlib.add_log_level,
          structlog.processors.TimeStamper(fmt="iso"),
          structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
      ],
  )
  ```
- **Use `ProcessorFormatter`** as a handler formatter to render stdlib log records through the structlog processor chain.

## Processor Ordering

- **Processor chain order matters.** Follow this sequence:
  1. **Merge context** (`merge_contextvars`) - pull in bound variables
  2. **Add metadata** (`add_log_level`, `TimeStamper`, `add_logger_name`)
  3. **Process exceptions** (`format_exc_info`, `StackInfoRenderer`)
  4. **Render output** (`JSONRenderer` for production, `ConsoleRenderer` for development)
- **Use `ConsoleRenderer()` during development** for colored, human-readable output. Switch to `JSONRenderer()` in production for machine parsing.
