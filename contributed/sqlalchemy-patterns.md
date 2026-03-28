# SQLAlchemy Patterns

## Session Lifecycle

- **One session per request or unit of work.** Never share sessions across threads or hold them open indefinitely:
  ```python
  # FastAPI dependency
  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```
- **Commit at the boundary**, not deep inside helper functions. Let the caller decide when to commit.

## Eager Loading to Avoid N+1

- **Use `selectinload()` for collections** and `joinedload()` for single relationships. Choose at query time, not on the model:
  ```python
  stmt = (
      select(Order)
      .options(
          joinedload(Order.customer),
          selectinload(Order.items).joinedload(OrderItem.product),
      )
      .where(Order.status == "pending")
  )
  orders = session.scalars(stmt).unique().all()
  ```
- **`selectinload()`** fires a second `SELECT ... WHERE id IN (...)` query. Better for collections to avoid row multiplication.
- **`joinedload()`** uses a SQL JOIN. Better for many-to-one and one-to-one relationships.

## Relationship Configuration

- **Use `back_populates` on both sides** instead of `backref`. It is explicit and discoverable:
  ```python
  class User(Base):
      __tablename__ = "users"
      id: Mapped[int] = mapped_column(primary_key=True)
      orders: Mapped[list["Order"]] = relationship(back_populates="user")

  class Order(Base):
      __tablename__ = "orders"
      user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
      user: Mapped["User"] = relationship(back_populates="orders")
  ```

## Alembic Migration Conventions

- **Name migrations descriptively:** `alembic revision -m "add_status_column_to_orders"`, not "update" or "fix".
- **Set a naming convention on `MetaData`** so constraints get predictable names:
  ```python
  convention = {
      "ix": "ix_%(column_0_label)s",
      "uq": "uq_%(table_name)s_%(column_0_name)s",
      "ck": "ck_%(table_name)s_%(constraint_name)s",
      "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
      "pk": "pk_%(table_name)s",
  }
  metadata = MetaData(naming_convention=convention)
  ```
- **Review auto-generated migrations before applying.** Alembic sometimes misses renames and generates drop+create instead.

## Mapped Column Types

- **Use `Mapped[]` type annotations** with SQLAlchemy 2.0 declarative style:
  ```python
  class Product(Base):
      __tablename__ = "products"
      id: Mapped[int] = mapped_column(primary_key=True)
      name: Mapped[str] = mapped_column(String(255))
      price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
      created_at: Mapped[datetime] = mapped_column(server_default=func.now())
      description: Mapped[str | None]  # nullable column
  ```

## Repository Pattern

- **Encapsulate queries in a repository class** to keep ORM details out of service code:
  ```python
  class OrderRepository:
      def __init__(self, session: Session):
          self.session = session

      def get_pending(self) -> list[Order]:
          stmt = select(Order).where(Order.status == "pending")
          return list(self.session.scalars(stmt))

      def get_by_id(self, order_id: int) -> Order | None:
          return self.session.get(Order, order_id)
  ```
- **The repository returns domain objects**, not raw rows or dicts. Let the caller decide serialization.
