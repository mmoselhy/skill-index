# Next.js App Router Patterns

## File-Based Routing

- **Route segments** map to directories under `app/`. Each folder becomes a URL segment.
- **`page.tsx`** is the only file that makes a route publicly accessible:
  ```tsx
  // app/dashboard/settings/page.tsx -> /dashboard/settings
  export default function SettingsPage() {
    return <h1>Settings</h1>;
  }
  ```
- **`layout.tsx`** wraps child routes and preserves state across navigations:
  ```tsx
  export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    return <div className="flex"><Sidebar /><main>{children}</main></div>;
  }
  ```
- **`loading.tsx`** provides instant loading UI via React Suspense while the page streams in.
- **`error.tsx`** catches runtime errors in the subtree. Must be a client component (`"use client"`).
- **`not-found.tsx`** handles `notFound()` calls within a route segment.

## Server Components by Default

- **All components are Server Components** unless marked with `"use client"` at the top of the file.
- **Add `"use client"` only when you need**: `useState`, `useEffect`, event handlers (`onClick`, `onChange`), browser APIs, or third-party client libraries.
- **Push client boundaries down** — wrap only the interactive leaf, not the whole page.

## Data Fetching

- **Fetch directly in server components** — no `useEffect` or `getServerSideProps`:
  ```tsx
  async function ProductPage({ params }: { params: { id: string } }) {
    const product = await db.product.findUnique({ where: { id: params.id } });
    return <ProductDetail product={product} />;
  }
  ```
- **`fetch()` requests are deduplicated** automatically when the same URL is called in multiple components within one render.
- **Revalidation**: use `revalidatePath('/products')` or `revalidateTag('products')` to invalidate cached data.

## Route Handlers

- **API endpoints** live in `app/api/` as `route.ts` files exporting HTTP method functions:
  ```ts
  // app/api/users/route.ts
  export async function GET(request: Request) {
    const users = await db.user.findMany();
    return Response.json(users);
  }
  ```
- **Dynamic segments** work the same as pages: `app/api/users/[id]/route.ts`.

## Metadata and SEO

- **Export a `metadata` object** or `generateMetadata` function from `page.tsx` or `layout.tsx`:
  ```tsx
  export const metadata: Metadata = { title: 'Dashboard', description: 'User dashboard' };
  ```
- **Dynamic metadata** uses `generateMetadata` with access to route params and parent metadata.

## Server Actions

- **Mark functions with `"use server"`** to call server logic directly from client components:
  ```tsx
  async function createPost(formData: FormData) {
    "use server";
    await db.post.create({ data: { title: formData.get("title") as string } });
    revalidatePath("/posts");
  }
  ```
- **Bind to `<form action>`** for progressive enhancement — forms work without JavaScript.

## Parallel and Intercepting Routes

- **Parallel routes** use `@slot` folder convention to render multiple pages in the same layout simultaneously: `app/@modal/page.tsx` alongside `app/@main/page.tsx`.
- **Intercepting routes** use `(.)`, `(..)`, `(...)` prefixes to show a route in a different context (e.g., a modal overlay for `/photo/[id]` when navigating client-side, full page on direct load).
