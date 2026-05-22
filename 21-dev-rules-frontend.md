# XynPOS — Blueprint 21: Development Rules — Frontend (Next.js/TypeScript)
> Extended Synaptic | Version 1.0 | Mandatory for all FE developers

---

## 1. Project Structure Rules

### ✅ WAJIB: Feature-Based Organization dalam apps/

```
src/
├── app/                   ← Next.js App Router pages SAJA
│   ├── (auth)/
│   └── (dashboard)/
│       └── products/
│           ├── page.tsx   ← Hanya boleh import dari features/
│           └── [id]/
├── features/              ← Semua business logic
│   ├── products/
│   │   ├── components/    ← Product-specific components
│   │   ├── hooks/         ← useProducts, useProductMutation
│   │   ├── api/           ← API calls untuk products
│   │   └── types/         ← Product-specific types
│   └── transactions/
├── components/            ← Shared generic components (Button, Modal, dll)
├── hooks/                 ← Shared hooks (useDebounce, useLocalStorage)
├── lib/                   ← Config & utils (api client, formatters)
├── store/                 ← Zustand stores (client state only)
└── types/                 ← Global types
```

### ✅ WAJIB: File Naming

```
PascalCase  → React components: ProductCard.tsx, PaymentModal.tsx
camelCase   → hooks, utils, stores: useCart.ts, cartStore.ts, formatCurrency.ts
kebab-case  → tidak dipakai di file naming (hanya URL)
```

---

## 2. Component Rules

### ✅ WAJIB: Component Responsibility

```tsx
// Setiap komponen punya SATU tanggung jawab

// ❌ SALAH: komponen yang tahu terlalu banyak
function ProductPage() {
  const [products, setProducts] = useState([])
  
  useEffect(() => {
    // Fetch langsung di component — JANGAN
    fetch('/api/products').then(r => r.json()).then(setProducts)
  }, [])
  
  const handleDelete = async (id: string) => {
    // Business logic di component — JANGAN
    await fetch(`/api/products/${id}`, { method: 'DELETE' })
    setProducts(prev => prev.filter(p => p.id !== id))
  }
  
  return <div>{/* ... */}</div>
}

// ✅ BENAR: separasi concern
function ProductPage() {
  const { data: products, isLoading } = useProducts()  // React Query hook
  const { mutate: deleteProduct } = useDeleteProduct()  // mutation hook
  
  if (isLoading) return <LoadingSpinner />
  
  return <ProductList products={products} onDelete={deleteProduct} />
}
```

### ✅ WAJIB: Props Typing dengan TypeScript

```tsx
// ✅ BENAR: typed props dengan interface
interface ProductCardProps {
  product: Product
  onSelect: (product: Product) => void
  isSelected?: boolean      // optional dengan ?
  className?: string
}

function ProductCard({ product, onSelect, isSelected = false, className }: ProductCardProps) {
  // ...
}

// ❌ SALAH: any props
function ProductCard(props: any) { /* ... */ }

// ❌ SALAH: tidak ada type
function ProductCard({ product, onSelect }) { /* ... */ }
```

### ✅ WAJIB: Tidak Ada Inline Style (Kecuali Dynamic Values)

```tsx
// ❌ JANGAN: inline style yang static
<div style={{ color: 'red', fontSize: '14px', padding: '8px' }}>

// ✅ BENAR: Tailwind classes
<div className="text-red-500 text-sm p-2">

// ✅ OK: inline style HANYA untuk dynamic values yang tidak bisa di-Tailwind
<div style={{ width: `${progress}%` }}>   // dynamic percentage OK
```

### ✅ WAJIB: Accessibility (a11y) Dasar

```tsx
// ✅ Semua interactive element punya keyboard access dan aria
<button
  onClick={handleClick}
  aria-label="Hapus produk Kopi Susu"
  disabled={isDeleting}
>
  <Trash2Icon className="h-4 w-4" />
</button>

// ✅ Image harus ada alt
<Image src={product.imageUrl} alt={product.name} width={200} height={200} />

// ✅ Form input harus ada label
<label htmlFor="product-name">Nama Produk</label>
<input id="product-name" type="text" />
```

---

## 3. State Management Rules

### ✅ WAJIB: Pilih State Management yang Tepat

```
Server state (data dari API)   → TanStack Query (useQuery, useMutation)
Client UI state (cart, modal)  → Zustand store
Form state                     → React Hook Form
Local ephemeral state          → useState (jika tidak perlu share)
URL state (filter, pagination) → useSearchParams

JANGAN gunakan useState untuk server data!
```

```tsx
// ✅ BENAR: server data via TanStack Query
function ProductList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['products', filters],
    queryFn: () => productsApi.list(filters),
    staleTime: 5 * 60 * 1000,  // 5 menit
  })
}

// ❌ SALAH: server data via useState + useEffect
function ProductList() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    setLoading(true)
    fetch('/api/products').then(r => r.json())
      .then(setProducts).finally(() => setLoading(false))
  }, [])
}
```

### ✅ WAJIB: Zustand Store Structure

```typescript
// ✅ BENAR: store yang focused dan minimal
interface CartStore {
  items: CartItem[]
  addItem: (product: Product) => void
  removeItem: (productId: string) => void
  updateQuantity: (productId: string, qty: number) => void
  clearCart: () => void
  // Computed (bukan state — gunakan selector)
}

// Selector untuk computed values
export const useCartTotal = () =>
  useCartStore(state =>
    state.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

// ❌ JANGAN taruh server data di Zustand
interface BadStore {
  products: Product[]  // Ini harusnya di React Query!
  fetchProducts: () => void
}
```

---

## 4. API Call Rules

### ✅ WAJIB: Semua API Call via Centralized Client

```typescript
// lib/api.ts — satu-satunya tempat konfigurasi HTTP client
import axios from 'axios'

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
})

// Interceptor otomatis inject Bearer token
api.interceptors.request.use(config => {
  const token = getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Interceptor untuk handle 401 → refresh token
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      await refreshTokenAndRetry(error.config)
    }
    return Promise.reject(error)
  }
)
```

```typescript
// ✅ BENAR: API functions di features/products/api/
export const productsApi = {
  list: (params?: ProductListParams) =>
    api.get<ApiResponse<Product[]>>('/v1/products', { params }),
  
  getById: (id: string) =>
    api.get<ApiResponse<Product>>(`/v1/products/${id}`),
  
  create: (data: CreateProductRequest) =>
    api.post<ApiResponse<Product>>('/v1/products', data),
  
  update: (id: string, data: UpdateProductRequest) =>
    api.patch<ApiResponse<Product>>(`/v1/products/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/v1/products/${id}`),
}

// ❌ JANGAN fetch langsung di komponen
const res = await fetch('/api/products')  // JANGAN
```

---

## 5. TypeScript Rules

### ✅ WAJIB: No `any` (Gunakan `unknown` jika terpaksa)

```typescript
// ❌ JANGAN
function processData(data: any) {
  data.whatever()  // Runtime error waiting to happen
}

// ✅ Gunakan proper typing
function processData(data: TransactionData) { /* ... */ }

// ✅ Jika tidak tahu tipe, gunakan unknown + type guard
function processData(data: unknown) {
  if (isTransactionData(data)) {
    data.id  // Sekarang TypeScript tahu ini TransactionData
  }
}
```

### ✅ WAJIB: Strict TypeScript Configuration

```json
// tsconfig.json harus include:
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### ✅ WAJIB: Zod untuk Runtime Validation

```typescript
// Validasi form dan API response dengan Zod
import { z } from 'zod'

const CreateProductSchema = z.object({
  name: z.string().min(1, 'Nama wajib diisi').max(255),
  sellingPrice: z.number().min(0.01, 'Harga harus lebih dari 0'),
  categoryId: z.string().uuid('Kategori tidak valid'),
  description: z.string().max(2000).optional(),
})

type CreateProductFormData = z.infer<typeof CreateProductSchema>

// Gunakan dengan React Hook Form
const { register, handleSubmit, formState: { errors } } =
  useForm<CreateProductFormData>({
    resolver: zodResolver(CreateProductSchema),
  })
```

---

## 6. Performance Rules

### ✅ WAJIB: Memoization yang Tepat (Tidak Berlebihan)

```tsx
// Gunakan useMemo HANYA untuk computation yang mahal
// ❌ Over-memoization (tidak perlu)
const name = useMemo(() => product.name, [product.name])  // string lookup tidak mahal

// ✅ Memoize yang perlu
const sortedProducts = useMemo(
  () => products.sort((a, b) => a.name.localeCompare(b.name)),
  [products]  // Sorting 1000+ item adalah operasi mahal
)

// Gunakan useCallback HANYA untuk function yang di-pass ke child komponen dengan React.memo
const handleDelete = useCallback(
  (id: string) => deleteProduct.mutate(id),
  [deleteProduct]
)
```

### ✅ WAJIB: Image Optimization

```tsx
// Selalu gunakan next/image untuk gambar
import Image from 'next/image'

// ✅ BENAR
<Image
  src={product.imageUrl}
  alt={product.name}
  width={200}
  height={200}
  className="rounded-lg object-cover"
  loading="lazy"    // untuk gambar di bawah fold
  priority          // untuk gambar above fold (LCP image)
/>

// ❌ JANGAN pakai <img> langsung untuk gambar produk
<img src={product.imageUrl} />  // Tidak ada optimization
```

### ✅ WAJIB: Loading States untuk Semua Async Operations

```tsx
// ✅ Selalu ada feedback untuk user saat loading/submitting
function CreateProductForm() {
  const { mutate, isPending } = useMutation({ /* ... */ })
  
  return (
    <form onSubmit={handleSubmit(data => mutate(data))}>
      {/* ... form fields */}
      <Button type="submit" disabled={isPending}>
        {isPending ? (
          <>
            <Spinner className="mr-2 h-4 w-4 animate-spin" />
            Menyimpan...
          </>
        ) : (
          'Simpan Produk'
        )}
      </Button>
    </form>
  )
}
```

---

## 7. Error Handling (UI)

### ✅ WAJIB: Error Boundary di Setiap Route

```tsx
// app/(dashboard)/products/layout.tsx
export default function ProductsLayout({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary fallback={<ProductsErrorFallback />}>
      {children}
    </ErrorBoundary>
  )
}
```

### ✅ WAJIB: Toast Notification untuk User Feedback

```tsx
import { toast } from 'sonner'

const { mutate: deleteProduct } = useMutation({
  mutationFn: (id: string) => productsApi.delete(id),
  onSuccess: () => {
    toast.success('Produk berhasil dihapus')
    queryClient.invalidateQueries({ queryKey: ['products'] })
  },
  onError: (error) => {
    toast.error(getErrorMessage(error))  // helper untuk extract error message
  },
})
```

---

## 8. Tailwind CSS Rules

### ✅ WAJIB: Gunakan Design System Variables

```tsx
// Warna dan spacing mengacu ke design tokens yang sudah didefinisikan
// Lihat tailwind.config.ts untuk custom values

// ✅ BENAR: pakai design token
<div className="bg-primary text-primary-foreground rounded-lg p-4">

// ❌ JANGAN: hardcode warna arbitrary
<div className="bg-[#1E40AF] text-[#FFFFFF] rounded-[12px] p-[16px]">
```

### ✅ WAJIB: Responsive Classes untuk POS Screen

```tsx
// POS screen harus support landscape tablet
// Gunakan responsive prefix
<div className={cn(
  "grid gap-2",
  "grid-cols-2",              // Mobile portrait: 2 kolom
  "sm:grid-cols-3",           // Tablet portrait: 3 kolom
  "md:grid-cols-4",           // Tablet landscape: 4 kolom
  "lg:grid-cols-5",           // Desktop: 5 kolom
)}>
```

---

## 9. Testing Rules

### ✅ WAJIB: Test untuk Custom Hooks

```typescript
// Setiap custom hook yang punya logic WAJIB ada test
describe('useCart', () => {
  it('menghitung total dengan benar termasuk diskon', () => {
    const { result } = renderHook(() => useCart(), {
      wrapper: createTestWrapper(),
    })
    
    act(() => {
      result.current.addItem(mockProduct)
      result.current.applyDiscount({ type: 'fixed', value: 5000 })
    })
    
    expect(result.current.total).toBe(mockProduct.price - 5000)
  })
})
```

### ✅ WAJIB: Test untuk Komponen Kritis

```
Wajib ada test untuk:
- Semua komponen di features/pos/components/
- Semua form component
- Shared components di packages/ui/

Boleh skip test untuk:
- Presentational components yang hanya render static content
- Layout components tanpa logic
```

---

## 10. Code Review Checklist (FE Self-Review)

```
STRUCTURE:
[ ] Komponen hanya punya 1 responsibility
[ ] File naming PascalCase untuk komponen, camelCase untuk hooks/utils
[ ] Tidak ada business logic di page.tsx langsung

STATE:
[ ] Server state via TanStack Query (bukan useState + useEffect)
[ ] Client state via Zustand (bukan prop drilling > 3 level)
[ ] Form state via React Hook Form + Zod

TYPESCRIPT:
[ ] Tidak ada `any` type
[ ] Semua props di-type dengan interface
[ ] Zod validation untuk semua form

API:
[ ] Semua API call via centralized api client
[ ] Error handling ada (onError callback)
[ ] Loading state ada (isPending/isLoading)

UI/UX:
[ ] Responsive untuk mobile + tablet + desktop
[ ] Accessible (aria labels, keyboard navigation)
[ ] Loading state visible untuk semua async operations
[ ] Error state visible saat fetch gagal
[ ] Empty state visible saat data kosong

PERFORMANCE:
[ ] Tidak ada unnecessary re-renders (cek dengan React DevTools Profiler)
[ ] Images pakai next/image
[ ] useMemo/useCallback hanya dipakai saat perlu
```

---

*Last updated: 2025 | Extended Synaptic — XynPOS*
