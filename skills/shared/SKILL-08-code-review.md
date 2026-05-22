---
skill_id: SKILL-08
name: XynPOS Code Review Assistant
category: shared
description: Skill untuk review PR — quality, security, performance, architecture
version: 1.0.0
applies_to: [review, quality, all-stack]
depends_on: [SKILL-00, SKILL-01, SKILL-03, SKILL-04]
---

# SKILL-08: Code Review Assistant

## Review Philosophy

Setiap review harus:
1. Jelaskan **WHY** masalah ada, bukan hanya WHAT yang salah
2. Berikan **contoh perbaikan konkret**
3. Bedakan **BLOCKER** (wajib diperbaiki) vs **SUGGESTION** (nice to have)
4. Apresiasi kode yang bagus — review bukan hanya tentang kritik

## Go Backend Review Checklist

```
ARCHITECTURE (BLOCKER jika dilanggar):
[ ] Clean architecture tidak dilanggar — usecase tidak import gorm/redis
[ ] Error di-wrap dengan konteks: fmt.Errorf("context: %w", err)
[ ] Tidak ada fmt.Println — gunakan zap logger
[ ] tenantID dari JWT (c.Locals), BUKAN dari request body/query

DATABASE (BLOCKER):
[ ] Tidak ada SQL string concatenation → SQL injection!
[ ] Tidak ada SELECT * — specify columns
[ ] Multi-step operations pakai DB transaction
[ ] Semua FK columns punya index (di migration)

SECURITY (BLOCKER):
[ ] Tidak ada hardcoded secret
[ ] Input divalidasi di handler layer
[ ] Sensitive data tidak di-log

TESTING (BLOCKER jika coverage < 70%):
[ ] Test coverage >= 70%
[ ] Happy path DAN error cases di-test
[ ] Table-driven tests untuk multiple scenarios
[ ] Mock via mockery (bukan manual mock)

API (BLOCKER):
[ ] Response pakai standard format dari shared/pkg/response
[ ] Swagger updated jika ada endpoint baru
[ ] Pagination untuk list endpoints

SUGGESTION:
[ ] Context timeout untuk external calls
[ ] Benchmark untuk kode di hot path
[ ] Lebih sedikit nesting dengan early return
```

## Next.js Frontend Review Checklist

```
STATE (BLOCKER):
[ ] Server state via TanStack Query — BUKAN useState+useEffect
[ ] Tidak ada `any` type
[ ] Semua form pakai React Hook Form + Zod validation

API (BLOCKER):
[ ] Semua API calls via lib/api.ts (centralized client)
[ ] Loading state ada untuk semua async operations
[ ] Error state ada dan informatif ke user

COMPONENT (BLOCKER):
[ ] Komponen hanya punya 1 responsibility
[ ] Error boundary di layout
[ ] Empty state ada saat data kosong

PERFORMANCE (SUGGESTION):
[ ] useMemo/useCallback hanya untuk compute yang mahal
[ ] next/image untuk semua gambar (bukan <img>)
[ ] Tidak ada unnecessary re-renders
```

## Flutter Mobile Review Checklist

```
ARCHITECTURE (BLOCKER):
[ ] Layer dependency tidak dilanggar
[ ] Model dan Entity TERPISAH (domain tidak punya fromJson)
[ ] Either<Failure, T> dari repository

STATE (BLOCKER):
[ ] AsyncValue untuk semua async state
[ ] Provider granular (tidak watch full state untuk partial update)

OFFLINE (BLOCKER untuk POS features):
[ ] Transaksi kasir bisa jalan tanpa internet
[ ] Local ID (idempotency) ada

PERFORMANCE (BLOCKER jika list panjang):
[ ] ListView.builder untuk list > 10 items
[ ] CachedNetworkImage untuk network images
[ ] const constructor untuk static widgets
```

## Common Issues & How to Give Feedback

### Issue: No error context
```go
// ❌ Code yang di-review
if err != nil { return nil, err }

// ✅ Feedback yang harus diberikan:
// BLOCKER: Error harus di-wrap dengan konteks untuk memudahkan debugging.
// Tanpa konteks, saat error muncul di production sulit tahu dari mana asalnya.
// 
// Fix:
if err != nil {
    return nil, fmt.Errorf("create transaction: find product %s: %w", productID, err)
}
```

### Issue: Business logic di handler
```go
// ❌ Code yang di-review
func (h *Handler) Create(c *fiber.Ctx) error {
    // ... parse request
    if product.Stock < req.Quantity { // business logic di handler!
        return fiber.NewError(422, "Stok tidak cukup")
    }
}

// ✅ Feedback:
// BLOCKER: Business logic (validasi stok) tidak boleh di handler layer.
// Handler hanya orchestrate: parse → validate input → call usecase → format response.
// Pindahkan ke usecase layer dan return domain.ErrInsufficientStock
```

### Issue: useState + useEffect untuk server data
```typescript
// ❌ Code yang di-review
const [products, setProducts] = useState([])
useEffect(() => { fetch('/api/products').then(r => r.json()).then(setProducts) }, [])

// ✅ Feedback:
// BLOCKER: Server data harus pakai TanStack Query, bukan useState+useEffect.
// Alasan: tidak ada caching, tidak ada deduplication, tidak ada background refetch,
// tidak ada loading/error state management yang proper.
// 
// Fix:
const { data: products, isLoading, error } = useQuery({
  queryKey: ['products'],
  queryFn: () => productsApi.list(),
})
```

## PR Description Template Review

```
Saat review PR, pastikan PR description memiliki:
[ ] Deskripsi singkat apa yang berubah
[ ] Screenshot/video jika ada UI changes
[ ] Cara test feature ini
[ ] Breaking changes (jika ada)
[ ] Related tickets/issues

Jika PR description kurang → minta di-update sebelum review
```

## Review Etiquette

```
✅ Gunakan kata yang konstruktif:
  "Sebaiknya kita...", "Satu hal yang bisa diperbaiki adalah...", "Pertimbangkan..."

✅ Bedakan severity dengan jelas:
  "[BLOCKER] ..." — harus diperbaiki sebelum merge
  "[SUGGESTION] ..." — nice to have, bisa jadi tiket terpisah
  "[QUESTION] ..." — butuh klarifikasi

✅ Apresiasi yang bagus:
  "Suka cara kamu handle offline sync di sini 👍"
  "Error handling di sini sudah sangat rapi"

❌ Hindari:
  "Ini salah" (tanpa penjelasan)
  "Kenapa begini?" (tanpa konteks mengapa ini jadi masalah)
  "Aku gak suka ini" (subjektif tanpa dasar teknis)
```
