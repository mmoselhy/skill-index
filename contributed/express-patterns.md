# Express.js Patterns

## Router-Level Middleware Organization

- **Group routes by resource** using `express.Router()`:
  ```js
  // routes/users.js
  const router = express.Router();
  router.use(authenticate);
  router.get("/", usersController.list);
  router.post("/", validate(createUserSchema), usersController.create);
  router.get("/:id", usersController.getById);
  module.exports = router;
  ```
- **Mount routers with a prefix** in the main app:
  ```js
  app.use("/api/users", require("./routes/users"));
  app.use("/api/orders", require("./routes/orders"));
  ```

## Error-Handling Middleware

- **Four parameters `(err, req, res, next)`** signal Express to treat the function as an error handler:
  ```js
  function errorHandler(err, req, res, next) {
    const status = err.statusCode || 500;
    const message = err.expose ? err.message : "Internal server error";
    console.error(err.stack);
    res.status(status).json({ error: message });
  }
  app.use(errorHandler); // must be registered AFTER all routes
  ```
- **Operational errors** should set `err.statusCode` and `err.expose = true` so the handler knows which messages are safe for the client.

## Request Validation Middleware

- **Validate before the controller** using a schema library (Zod, Joi, ajv):
  ```js
  function validate(schema) {
    return (req, res, next) => {
      const result = schema.safeParse(req.body);
      if (!result.success) {
        return res.status(400).json({ errors: result.error.flatten().fieldErrors });
      }
      req.validated = result.data;
      next();
    };
  }
  ```
- **Apply per-route**, not globally: `router.post("/", validate(createUserSchema), controller.create)`.

## Controller Separation

- **Routes define the HTTP interface** (method, path, middleware chain).
- **Controllers handle request/response** — extract params, call services, send responses:
  ```js
  // controllers/users.js
  exports.getById = async (req, res, next) => {
    try {
      const user = await userService.findById(req.params.id);
      if (!user) return res.status(404).json({ error: "User not found" });
      res.json(user);
    } catch (err) { next(err); }
  };
  ```
- **Services contain business logic** and are framework-agnostic (no `req`/`res`).

## Async Handler Wrapper

- **Catch unhandled promise rejections** so they reach the error handler instead of crashing:
  ```js
  const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };

  router.get("/", asyncHandler(async (req, res) => {
    const items = await itemService.findAll();
    res.json(items);
  }));
  ```
- **Wrap every async route handler** — a single missed `catch` can bring down the process.

## Environment-Based Configuration

- **Centralize config** in a single module that reads from `process.env`:
  ```js
  // config.js
  module.exports = {
    port: parseInt(process.env.PORT, 10) || 3000,
    dbUrl: process.env.DATABASE_URL,
    isProduction: process.env.NODE_ENV === "production",
  };
  ```
- **Validate required variables at startup** — fail fast with a clear message rather than at first request.
- **Never import `dotenv` in production** — use your platform's env injection. Guard with `if (process.env.NODE_ENV !== "production") require("dotenv").config()`.

## Health Check Endpoint

- **Expose a lightweight `GET /healthz`** for load balancers and orchestrators:
  ```js
  app.get("/healthz", async (req, res) => {
    try {
      await db.raw("SELECT 1");
      res.status(200).json({ status: "ok" });
    } catch {
      res.status(503).json({ status: "degraded", error: "database unreachable" });
    }
  });
  ```
- **Keep it fast** — check critical dependencies only (database, cache), not every downstream service.
