---
skill_id: SKILL-03
name: XynPOS Next.js Frontend Development
category: frontend
description: Skill untuk web dashboard dan web POS — Next.js, TypeScript, Tailwind, TanStack Query, Zustand
version: 1.0.0
applies_to: [frontend, nextjs, typescript, web]
depends_on: [SKILL-00]
---

# SKILL-03: Next.js Frontend Development

## Stack

```
Framework:      Next.js 14 (App Router)
Language:       TypeScript 5 (strict mode)
Styling:        Tailwind CSS v3 + shadcn/ui
Server State:   TanStack Query v5 (React Query)
Client State:   Zustand v4
Forms:          React Hook Form + Zod
Charts:         Recharts + Tremor
Offline:        Dexie.js (IndexedDB)
Icons:          Lucide React
Table:          TanStack Table v8
Animations:     Framer Motion
Package:        pnpm
```

## App Structure

```
frontend/apps/web-dashboard/src/
├── app/                    ← Next.js routes (minimal logic)
│   ├── (auth)/login/
│   └── (dashboard)/
│       ├── layout.tsx
│       ├── products/page.tsx
│       └── reports/page.tsx
├── features/               ← Business features
│   ├── products/
│   │   ├── components/     ← Feature-specific UI
│   │   ├── hooks/          ← useProducts, useDeleteProduct
│   │   ├── api/            ← productsApi.list(), .create()
│   │   └── types/
│   └── transactions/
├── components/             ← Shared generic components
├── hooks/                  ← Shared hooks
├── lib/api.ts              ← Axios instance (single source)
├── store/                  ← Zustand stores
└── types/                  ← Global types
```

## State Management Decision

```
Server state (API data)    → TanStack Query
Client UI state (cart)     → Zustand
Form state                 → React Hook Form
URL state (filters)        → useSearchParams
Local ephemeral            → useState
```

## API Client Pattern

```typescript
// lib/api.ts — satu-satunya HTTP client
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
})

api.interceptors.request.use(config => {
  const token = getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// features/products/api/index.ts
export const productsApi = {
  list: (params?: ProductListParams) =>
    api.get<ApiResponse<Product[]>>('/v1/products', { params }).then(r => r.data),
  create: (data: CreateProductRequest) =>
    api.post<ApiResponse<Product>>('/v1/products', data).then(r => r.data),
}

// ❌ JANGAN fetch langsung di komponen atau hooks
```

## TanStack Query Patterns

```typescript
// ✅ Fetching
const { data: products, isLoading, error } = useQuery({
  queryKey: ['products', filters],
  queryFn: () => productsApi.list(filters),
  staleTime: 5 * 60 * 1000,
})

// ✅ Mutation dengan optimistic update + rollback
const { mutate: deleteProduct } = useMutation({
  mutationFn: (id: string) => productsApi.delete(id),
  onMutate: async (id) => {
    await queryClient.cancelQueries({ queryKey: ['products'] })
    const prev = queryClient.getQueryData(['products'])
    queryClient.setQueryData(['products'], (old: Product[]) =>
      old.filter(p => p.id !== id))
    return { prev }
  },
  onError: (_, __, context) => {
    queryClient.setQueryData(['products'], context?.prev)
    toast.error('Gagal menghapus produk')
  },
  onSuccess: () => {
    toast.success('Produk dihapus')
    queryClient.invalidateQueries({ queryKey: ['products'] })
  },
})
```

## Zustand Store Pattern

```typescript
// store/cartStore.ts
interface CartStore {
  items: CartItem[]
  addItem: (product: Product, quantity?: number) => void
  removeItem: (productId: string) => void
  updateQuantity: (productId: string, qty: number) => void
  applyDiscount: (discount: Discount) => void
  clearCart: () => void
}

export const useCartStore = create<CartStore>((set) => ({
  items: [],
  addItem: (product, quantity = 1) => set(state => {
    const existing = state.items.find(i => i.productId === product.id)
    if (existing) {
      return { items: state.items.map(i =>
        i.productId === product.id ? { ...i, quantity: i.quantity + quantity } : i
      )}
    }
    return { items: [...state.items, { productId: product.id, product, quantity }] }
  }),
  // ...
}))

// Selector — watch granular, tidak full store
export const useCartTotal = () =>
  useCartStore(s => s.items.reduce((sum, i) => sum + i.product.price * i.quantity, 0))
```

## TypeScript Rules

```typescript
// ✅ Typed props
interface ProductCardProps {
  product: Product
  onSelect: (product: Product) => void
  isSelected?: boolean
}

// ✅ Zod schema untuk forms
const CreateProductSchema = z.object({
  name: z.string().min(1, 'Wajib diisi').max(255),
  sellingPrice: z.number().min(0.01, 'Harga > 0'),
  categoryId: z.string().uuid('Kategori tidak valid'),
})
type CreateProductForm = z.infer<typeof CreateProductSchema>

// ❌ NEVER any
function process(data: any) { }

// ✅ Use unknown with type guard
function process(data: unknown) {
  if (isProduct(data)) { /* TypeScript knows it's Product here */ }
}
```

## Component Rules

```typescript
// ✅ Single responsibility — page hanya orchestrate
function ProductsPage() {
  const { data, isLoading } = useProducts()
  const { mutate: delete_ } = useDeleteProduct()
  
  if (isLoading) return <TableSkeleton />
  return <ProductsTable products={data} onDelete={delete_} />
}

// ✅ Loading + error + empty states semua ada
function ProductsTable({ products, onDelete }) {
  if (products.length === 0) return <EmptyState />
  return (/* table */)
}

// ✅ Error boundary di layout
function DashboardLayout({ children }) {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      {children}
    </ErrorBoundary>
  )
}
```

## Tailwind + Design Tokens

```typescript
// Gunakan design token, bukan arbitrary values
<div className="bg-primary text-primary-foreground p-4 rounded-lg">  // ✅
<div className="bg-[#1E40AF] p-[16px] rounded-[12px]">               // ❌

// Responsive untuk POS screen (landscape tablet)
<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
```

## Checklist Sebelum PR

```
[ ] Server state via TanStack Query (bukan useState+useEffect)
[ ] Tidak ada `any` type
[ ] Semua form pakai React Hook Form + Zod
[ ] API calls via lib/api.ts
[ ] Loading state ada untuk semua async
[ ] Error state ada saat fetch gagal
[ ] Empty state ada saat data kosong
[ ] Responsive mobile + tablet + desktop
[ ] Tidak ada inline static style (pakai Tailwind)
[ ] Error boundary di layout
```
