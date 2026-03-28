# Pytest Patterns

## Fixture Scoping and Composition

- **Use the narrowest scope that works.** `function` (default) gives test isolation. `module` and `session` are for expensive resources like database connections or Docker containers.
- **Compose fixtures by injecting them into each other**, not by building monolithic setup functions:
  ```python
  @pytest.fixture
  def db_connection(db_engine):
      conn = db_engine.connect()
      yield conn
      conn.close()
  ```

## conftest.py Organization

- **One `conftest.py` per directory**, scoped to that directory's needs. Never put all fixtures in a single root `conftest.py`.
- **Root `conftest.py`** holds shared fixtures (database, auth tokens). Subdirectory `conftest.py` files hold domain-specific fixtures.

## Parametrize for Data-Driven Tests

- **Use `@pytest.mark.parametrize` instead of loops** inside test functions:
  ```python
  @pytest.mark.parametrize("input,expected", [
      ("hello", "HELLO"),
      ("world", "WORLD"),
      ("", ""),
  ])
  def test_uppercase(input, expected):
      assert input.upper() == expected
  ```
- **Use `ids=` parameter** to label test cases when inputs are not self-describing.

## Factory Fixtures Over Complex Chains

- **Return a factory callable** when tests need variations of the same object:
  ```python
  @pytest.fixture
  def make_user(db_session):
      def _make_user(name="default", role="viewer"):
          user = User(name=name, role=role)
          db_session.add(user)
          db_session.flush()
          return user
      return _make_user
  ```

## Temporary Files and Paths

- **Use `tmp_path` (pathlib.Path) over `tempfile` manual management.** Pytest handles cleanup automatically:
  ```python
  def test_write_config(tmp_path):
      config_file = tmp_path / "config.json"
      config_file.write_text('{"key": "value"}')
      assert config_file.exists()
  ```

## Exception Testing

- **Use `pytest.raises` as a context manager**, not as a bare call. Check the message when it matters:
  ```python
  with pytest.raises(ValueError, match="must be positive"):
      calculate(-1)
  ```

## Assertion Style

- **Use plain `assert` statements.** Pytest's assertion introspection gives detailed diffs automatically. Never use `self.assertEqual` or `assert_that` wrappers.
- **One logical assertion per test.** Multiple asserts are fine if they verify the same behavior.

## Markers for Test Categories

- **Mark slow and integration tests** so the fast suite runs in seconds:
  ```python
  @pytest.mark.slow
  def test_full_pipeline():
      ...

  @pytest.mark.integration
  def test_database_roundtrip(db):
      ...
  ```
- **Register markers in `pyproject.toml`** to avoid warnings:
  ```toml
  [tool.pytest.ini_options]
  markers = [
      "slow: marks tests as slow",
      "integration: marks tests requiring external services",
  ]
  ```
