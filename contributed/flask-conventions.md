# Flask Conventions

## Application Factory Pattern

- **Always use `create_app()` as the entry point.** This enables testing with different configs and avoids import-time side effects:
  ```python
  def create_app(config_name="default"):
      app = Flask(__name__)
      app.config.from_object(config[config_name])

      db.init_app(app)
      migrate.init_app(app, db)
      login_manager.init_app(app)

      from .routes import main_bp, auth_bp
      app.register_blueprint(main_bp)
      app.register_blueprint(auth_bp, url_prefix="/auth")

      return app
  ```
- **Never create the `Flask()` instance at module level** in production code. Tests need fresh app instances.

## Blueprints for Modular Organization

- **One blueprint per feature domain.** Each blueprint lives in its own package:
  ```
  app/
    auth/
      __init__.py   # blueprint definition
      routes.py     # route handlers
      forms.py      # WTForms classes
    orders/
      __init__.py
      routes.py
      models.py
  ```
- **Define the blueprint in `__init__.py`** of its package:
  ```python
  from flask import Blueprint
  auth_bp = Blueprint("auth", __name__, template_folder="templates")
  from . import routes  # noqa: E402 — registers routes on blueprint
  ```

## Error Handlers

- **Register error handlers on the app, not on blueprints.** Blueprint-level handlers only catch errors from that blueprint's own views, which leads to inconsistent behavior:
  ```python
  def create_app():
      app = Flask(__name__)

      @app.errorhandler(404)
      def not_found(e):
          return render_template("404.html"), 404

      @app.errorhandler(500)
      def server_error(e):
          return render_template("500.html"), 500

      return app
  ```

## Request-Scoped State with flask.g

- **Use `flask.g` for per-request state** like database connections or the current user. It is reset between requests:
  ```python
  @app.before_request
  def load_user():
      token = request.headers.get("Authorization")
      g.current_user = decode_token(token) if token else None
  ```
- **Never store persistent state on `flask.g`**. It dies when the request ends.

## Configuration from Environment

- **Load secrets from environment variables**, never from committed files:
  ```python
  class Config:
      SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-key")
      SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
      SQLALCHEMY_TRACK_MODIFICATIONS = False
  ```
- **Use a config class hierarchy:** `Config` (base), `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`.

## Extension Initialization Pattern

- **Create extensions at module level, initialize with `init_app()` inside the factory.** This avoids circular imports:
  ```python
  # extensions.py
  from flask_sqlalchemy import SQLAlchemy
  from flask_migrate import Migrate

  db = SQLAlchemy()
  migrate = Migrate()
  ```
  ```python
  # app.py
  from .extensions import db, migrate

  def create_app():
      app = Flask(__name__)
      db.init_app(app)
      migrate.init_app(app, db)
      return app
  ```
- **Import from `extensions.py`** in models and routes, not from the app module.
