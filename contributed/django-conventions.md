# Django Conventions

## Fat Models, Thin Views

- **Put business logic on the model**, not in views or serializers. Views should only handle HTTP concerns:
  ```python
  class Order(models.Model):
      def cancel(self):
          if self.status == "shipped":
              raise ValueError("Cannot cancel shipped orders")
          self.status = "cancelled"
          self.cancelled_at = timezone.now()
          self.save(update_fields=["status", "cancelled_at"])
  ```
- **Views call model methods**, they do not contain domain logic:
  ```python
  def cancel_order(request, pk):
      order = get_object_or_404(Order, pk=pk)
      order.cancel()
      return redirect("order-detail", pk=pk)
  ```

## Custom Managers and QuerySets

- **Define custom querysets for reusable filters**, then expose them through a manager:
  ```python
  class ActiveQuerySet(models.QuerySet):
      def active(self):
          return self.filter(is_active=True, deleted_at__isnull=True)

  class UserManager(models.Manager):
      def get_queryset(self):
          return ActiveQuerySet(self.model, using=self._db)

  class User(models.Model):
      objects = UserManager()
  ```
- **Chain custom queryset methods** just like built-in ones: `User.objects.active().filter(role="admin")`.

## Test Class Selection

- **`SimpleTestCase`** for tests that need no database access at all.
- **`TestCase`** (wraps each test in a transaction) for most database tests. Fastest option with DB.
- **`TransactionTestCase`** only when testing code that calls `transaction.atomic()` or needs to verify commit/rollback behavior. It is significantly slower.

## URL References

- **Always use `reverse()` or `{% url %}` for URL references.** Never hardcode paths:
  ```python
  from django.urls import reverse
  url = reverse("user-detail", kwargs={"pk": user.pk})
  ```
- **Name every URL pattern.** Use `app_name` for namespace isolation.

## Signals

- **Use signals sparingly.** Prefer explicit method calls for business logic. Signals make control flow invisible and hard to debug.
- **Acceptable signal uses:** cache invalidation, audit logging, third-party integrations. Not for core business rules.

## Settings Organization

- **Split settings into modules:** `settings/base.py`, `settings/local.py`, `settings/production.py`.
- **`base.py`** holds shared config. Environment-specific files import from base and override:
  ```python
  # settings/production.py
  from .base import *  # noqa: F403
  DEBUG = False
  DATABASES["default"]["CONN_MAX_AGE"] = 600
  ```
- **Use `django-environ` or `os.environ`** for secrets. Never commit secrets to settings files.

## Migration Best Practices

- **One migration per logical change.** Squash old migrations when the chain gets long.
- **Never edit a migration that has been applied in production.** Create a new one.
- **Add `db_index=True`** on fields used in `filter()`, `order_by()`, or `get()` queries.
- **Use `RunPython` with a reverse function** for data migrations so they can be rolled back:
  ```python
  operations = [
      migrations.RunPython(populate_slugs, reverse_code=migrations.RunPython.noop),
  ]
  ```
