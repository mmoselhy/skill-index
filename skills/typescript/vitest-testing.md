# Vitest Testing Patterns

## Test Organization

- **`describe` blocks** group related tests by unit (function, component, feature):
  ```ts
  describe("formatCurrency", () => {
    it("formats USD with two decimal places", () => {
      expect(formatCurrency(1234.5, "USD")).toBe("$1,234.50");
    });

    it("returns empty string for NaN input", () => {
      expect(formatCurrency(NaN, "USD")).toBe("");
    });
  });
  ```
- **`it` descriptions read as sentences** — start with a verb: "returns", "throws", "renders".
- **One assertion per test** when practical. Multiple assertions are fine if they verify a single logical outcome.

## File Co-location

- **Place test files next to source**: `utils/formatCurrency.ts` and `utils/formatCurrency.test.ts`.
- **Use `.test.ts` suffix** (not `.spec.ts`) for consistency. Configure in `vitest.config.ts`:
  ```ts
  export default defineConfig({
    test: { include: ["**/*.test.{ts,tsx}"] },
  });
  ```

## Mocking Modules

- **`vi.mock()` hoists automatically** — call at the top level to replace a module:
  ```ts
  vi.mock("@/lib/db", () => ({
    db: { user: { findMany: vi.fn().mockResolvedValue([{ id: "1", name: "Alice" }]) } },
  }));
  ```
- **`vi.mocked(fn)`** provides type-safe access to mock metadata:
  ```ts
  import { fetchUser } from "@/lib/api";
  vi.mock("@/lib/api");

  it("calls fetchUser with the correct id", async () => {
    vi.mocked(fetchUser).mockResolvedValue({ id: "1", name: "Alice" });
    await loadProfile("1");
    expect(vi.mocked(fetchUser)).toHaveBeenCalledWith("1");
  });
  ```

## Function Spies

- **`vi.fn()`** creates a standalone spy for callbacks and injected dependencies:
  ```ts
  const onSubmit = vi.fn();
  render(<Form onSubmit={onSubmit} />);
  fireEvent.click(screen.getByRole("button"));
  expect(onSubmit).toHaveBeenCalledOnce();
  ```
- **`vi.spyOn(object, "method")`** wraps an existing method without replacing the module.

## Setup and Teardown

- **`beforeEach`** resets shared state so tests stay isolated:
  ```ts
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });
  ```
- **`afterEach`** cleans up side effects (timers, DOM, subscriptions).
- **`beforeAll` / `afterAll`** for expensive one-time setup like starting a test database.

## Assertions

- **`toEqual()`** for deep structural comparison of objects and arrays.
- **`toBe()`** for primitives and reference identity.
- **`toMatchInlineSnapshot()`** captures output inline so diffs appear in code review:
  ```ts
  expect(serialize(user)).toMatchInlineSnapshot(`
    {
      "id": "1",
      "name": "Alice",
    }
  `);
  ```
- **`toThrowError(/message/)`** asserts thrown errors with a pattern match.

## Async Testing

- **Return or `await` promises** in test bodies — Vitest detects the async boundary:
  ```ts
  it("fetches data", async () => {
    const data = await fetchData();
    expect(data).toEqual({ status: "ok" });
  });
  ```
- **`vi.useFakeTimers()`** and **`vi.advanceTimersByTime(ms)`** for testing debounce, polling, and timeouts.
