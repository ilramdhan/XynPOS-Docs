---
name: xynpos-frontend
description: XynPOS Next.js frontend development — use when building or reviewing React components, pages, hooks, or state management for the web dashboard or web POS application. Triggers when working on Next.js App Router, TypeScript components, TanStack Query data fetching, Zustand stores, React Hook Form, Tailwind CSS, shadcn/ui, or the offline POS interface. Also triggers for questions about frontend architecture, state management decisions, performance optimization, or API integration patterns in the XynPOS web apps.
license: See LICENSE.txt
---

# XynPOS Next.js Frontend Development

Two web applications live in `frontend/apps/`:
- **web-pos** — Full-screen kasir interface (touch-optimized, offline-capable)
- **web-dashboard** — Owner/manager reporting and management dashboard

## Reference Files
- Full component patterns → `references/component-patterns.md`
- State management guide → `references/state-management.md`
- POS-specific patterns → `references/pos-patterns.md`

## Stack

```
Next.js 14 App Router    TypeScript 5 (strict)
Tailwind CSS v3          shadcn/ui
TanStack Query v5        Zustand v4
React Hook Form + Zod    Lucide React icons
pnpm                     Vitest + Playwright
```

## Project Structure

```
frontend/apps/web-dashboard/src/
├── app/                  Next.js routes (minimal logic only)
├── features/             Business features (self-contained)
│   ├── products/
│   │   ├── components/  Feature-specific UI
│   │   ├── hooks/       useProducts(), useDeleteProduct()
│   │   ├── api/         productsApi.list(), .create()
│   │   └── types/
│   └── transactions/
├── components/           Generic shared components
├── hooks/                Shared hooks (useDebounce, etc.)
├── lib/api.ts            Single HTTP client (axios)
├── store/                Zustand stores
└── types/                Global TypeScript types
```

## State Decision Matrix

```
Data from API           → TanStack Query (NEVER useState+useEffect)
Cart, modal open/close  → Zustand store
Form values             → React Hook Form
Filter/sort in URL      → useSearchParams
Local ephemeral UI      → useState
```

## Core Rules

```tsx
// ✅ Server state: TanStack Query
const { data: products, isLoading } = useQuery({
  queryKey: ['products', filters],
  queryFn: () => productsApi.list(filters),
  staleTime: 5 * 60 * 1000,
})

// ❌ NEVER useState+useEffect for server data
const [products, setProducts] = useState([])
useEffect(() => { fetch('/api/products').then(...) }, [])

// ✅ All API calls via centralized client
// lib/api.ts — single axios instance with auth interceptor
import { productsApi } from '@/features/products/api'

// ❌ NEVER direct fetch in components
const res = await fetch('/api/products')

// ✅ TypeScript: no any
interface ProductCardProps { product: Product; onSelect: (p: Product) => void }
// ❌ No any
function Card(props: any) {}

// ✅ Zod for form validation
const Schema = z.object({ name: z.string().min(1), price: z.number().min(0.01) })
type FormData = z.infer<typeof Schema>
```

## Scripts

Run `scripts/check_fe_rules.py <path>` to scan for frontend violations.
