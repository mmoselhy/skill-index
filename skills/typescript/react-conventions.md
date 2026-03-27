# React + TypeScript Conventions

## Component Naming

- **PascalCase file names** matching the default export: `UserProfile.tsx` exports `UserProfile`.
- **Index files only for barrels** — avoid `index.tsx` as a component file name; use the component name so search and tabs stay readable.

## Props Interfaces

- **Define `interface FooProps`** co-located directly above the component:
  ```tsx
  interface UserCardProps {
    user: User;
    onSelect: (id: string) => void;
    variant?: "compact" | "full";
  }

  export function UserCard({ user, onSelect, variant = "full" }: UserCardProps) {
    // ...
  }
  ```
- **Prefer `interface` over `type`** for props — interfaces produce clearer error messages and are extendable.
- **Use `React.ComponentPropsWithoutRef<"button">`** to extend native element props instead of redefining `className`, `disabled`, etc.

## Custom Hooks

- **Always prefix with `use`**: `useAuth`, `useDebounce`, `useMediaQuery`.
- **Extract shared stateful logic** into hooks rather than duplicating `useState`/`useEffect` across components:
  ```tsx
  function useDebounce<T>(value: T, delay: number): T {
    const [debounced, setDebounced] = useState(value);
    useEffect(() => {
      const timer = setTimeout(() => setDebounced(value), delay);
      return () => clearTimeout(timer);
    }, [value, delay]);
    return debounced;
  }
  ```
- **Return tuples or objects** — tuples for simple state (`[value, setValue]`), objects for multiple return values.

## State Management

- **Local state first** — `useState` covers most cases. Start here.
- **Context for shared UI state** — theme, locale, sidebar open/closed. Avoid putting server data in context.
- **External store for complex state** — use Zustand, Jotai, or Redux Toolkit when state is accessed across many unrelated components or needs middleware.
- **Server state belongs in a data layer** — React Query / SWR for client-fetched data, server components for SSR data.

## Event Handler Naming

- **`handle<Event>` inside the component** that owns the logic: `handleSubmit`, `handleClick`.
- **`on<Event>` in the props interface** to signal a callback: `onSubmit`, `onClick`.
  ```tsx
  interface ModalProps { onClose: () => void; }

  function Modal({ onClose }: ModalProps) {
    const handleBackdropClick = () => onClose();
    return <div onClick={handleBackdropClick}>...</div>;
  }
  ```

## Type Safety

- **Avoid `any`** — use `unknown` for truly unknown values, then narrow with type guards.
- **Use generics** for reusable utilities:
  ```tsx
  function List<T extends { id: string }>({ items, renderItem }: {
    items: T[];
    renderItem: (item: T) => React.ReactNode;
  }) {
    return <ul>{items.map(item => <li key={item.id}>{renderItem(item)}</li>)}</ul>;
  }
  ```
- **Discriminated unions** for variant components: `type Status = { kind: "loading" } | { kind: "error"; message: string } | { kind: "success"; data: Data }`.

## Composition Over Prop Drilling

- **Use `children` and render props** instead of passing data through intermediate components:
  ```tsx
  <Card>
    <Card.Header title="Users" />
    <Card.Body>{content}</Card.Body>
  </Card>
  ```
- **Compound components** share implicit state via context, keeping the public API declarative.
- **Lift content up** — pass JSX as props (`header={<Logo />}`) rather than passing raw data through 3+ levels.
