# XynPOS — Blueprint 20: Development Rules — Backend (Go)
> Extended Synaptic | Version 1.0 | Mandatory for all BE developers

---

## Preface

Rules ini adalah **law**, bukan guideline. Setiap PR yang melanggar rules ini akan di-reject sampai diperbaiki. Tujuannya bukan birokratis — tapi untuk menjaga codebase tetap maintainable saat tim dan codebase berkembang.

---

## 1. Project Structure Rules

### ✅ WAJIB: Clean Architecture Layer

```
Setiap service WAJIB mengikuti layer ini secara ketat:

domain/      → Entity + business rules
               BOLEH: struct, interface, error definition, business logic pure
               TIDAK BOLEH: import apapun dari infra (gorm, redis, dll)

repository/  → Interface data access (interface definition saja)
               BOLEH: interface definition, error types
               TIDAK BOLEH: implementasi konkret (itu di postgres/ subfolder)

usecase/     → Business orchestration
               BOLEH: import domain, repository interfaces
               TIDAK BOLEH: import gorm, database, http package langsung

delivery/    → Transport (HTTP handler, gRPC)
               BOLEH: import usecase, standard library, fiber
               TIDAK BOLEH: business logic, direct DB access

Dependency direction: delivery → usecase → repository(interface) ← domain
```

```go
// ✅ BENAR: usecase hanya tahu interface
type TransactionUsecase struct {
    txRepo  repository.TransactionRepository  // interface
    invRepo repository.InventoryRepository    // interface
    logger  *zap.Logger
}

// ❌ SALAH: usecase import konkret DB
type TransactionUsecase struct {
    db *gorm.DB  // JANGAN! Ini coupling ke infra
}
```

### ✅ WAJIB: File Naming

```
snake_case untuk semua file Go:
✅ transaction_repository.go
✅ create_transaction_request.go
❌ TransactionRepository.go
❌ createTransactionRequest.go
```

### ✅ WAJIB: Package Naming

```go
// Package name = nama folder, lowercase, no underscore
package usecase     // ✅
package repository  // ✅
package pos_service // ❌ (no underscore)
package posService  // ❌ (no camelCase)
```

---

## 2. Error Handling Rules

### ✅ WAJIB: Wrap Error dengan Konteks

```go
// ✅ BENAR: selalu wrap dengan konteks
if err != nil {
    return nil, fmt.Errorf("create transaction: get product by id %s: %w", productID, err)
}

// ❌ SALAH: return error tanpa konteks
if err != nil {
    return nil, err
}

// ❌ SALAH: log dan return (double logging)
if err != nil {
    log.Error("error", err)
    return nil, err
}
```

### ✅ WAJIB: Custom Error Types untuk Domain Errors

```go
// di domain/errors.go
var (
    ErrProductNotFound     = errors.New("product not found")
    ErrInsufficientStock   = errors.New("insufficient stock")
    ErrTransactionNotFound = errors.New("transaction not found")
    ErrInvalidPaymentAmount = errors.New("invalid payment amount")
    ErrTenantSuspended     = errors.New("tenant is suspended")
)

// Di usecase, return domain error
if product == nil {
    return nil, domain.ErrProductNotFound
}

// Di handler, map ke HTTP status
switch {
case errors.Is(err, domain.ErrProductNotFound):
    return fiber.NewError(404, "Produk tidak ditemukan")
case errors.Is(err, domain.ErrInsufficientStock):
    return fiber.NewError(422, "Stok tidak mencukupi")
}
```

### ✅ WAJIB: Tidak Boleh Panic di Production Code

```go
// ❌ TIDAK BOLEH ada panic di kode produksi (kecuali main.go init)
func processOrder() {
    panic("something went wrong") // NEVER
}

// ✅ Return error, jangan panic
func processOrder() error {
    return fmt.Errorf("something went wrong: %w", err)
}
```

---

## 3. Logging Rules

### ✅ WAJIB: Gunakan Structured Logging (Zap)

```go
// Inject logger via constructor, bukan global
type TransactionUsecase struct {
    logger *zap.Logger
}

// ✅ BENAR: structured fields
logger.Info("transaction created",
    zap.String("tenant_id", tenantID),
    zap.String("transaction_id", tx.ID),
    zap.Float64("total", tx.TotalAmount),
    zap.Duration("duration", time.Since(start)),
)

// ❌ SALAH: string interpolation
logger.Info(fmt.Sprintf("transaction %s created for tenant %s", txID, tenantID))

// ❌ SALAH: fmt.Println
fmt.Println("transaction created:", txID)
```

### ✅ WAJIB: Log Level yang Tepat

```go
logger.Debug(...)   // Detail flow untuk debugging (dimatikan di production)
logger.Info(...)    // Event penting (transaction created, user logged in)
logger.Warn(...)    // Kondisi tidak normal tapi tidak fatal (retry, cache miss)
logger.Error(...)   // Error yang perlu perhatian (DB error, external service fail)
// Fatal/Panic: TIDAK BOLEH di production code selain main.go init
```

### ✅ WAJIB: Tidak Log Data Sensitif

```go
// ❌ JANGAN log password, token, PIN, nomor kartu
logger.Info("user login", zap.String("password", req.Password))  // NEVER!

// ✅ Log hanya identifier yang aman
logger.Info("user login",
    zap.String("email", maskEmail(req.Email)),
    zap.String("ip", c.IP()),
)
```

---

## 4. Database Rules

### ✅ WAJIB: Selalu Gunakan Context

```go
// ✅ BENAR: semua query pakai context (untuk timeout + cancellation)
result := db.WithContext(ctx).Where("id = ?", id).First(&product)

// ❌ SALAH: tanpa context (tidak bisa timeout)
result := db.Where("id = ?", id).First(&product)
```

### ✅ WAJIB: Tidak Ada Raw String SQL Concatenation

```go
// ❌ SANGAT BERBAHAYA: SQL injection
db.Exec("SELECT * FROM products WHERE name = '" + name + "'")

// ✅ BENAR: parameterized
db.Where("name = ?", name).Find(&products)

// ✅ BENAR: raw query jika perlu, tetap parameterized
db.Raw("SELECT * FROM products WHERE name = ? AND is_active = ?", name, true).Scan(&products)
```

### ✅ WAJIB: Tidak Boleh SELECT *

```go
// ❌ SALAH: SELECT * mengambil semua kolom
var products []Product
db.Find(&products)

// ✅ BENAR: specify field yang dibutuhkan
var products []Product
db.Select("id", "name", "selling_price", "is_active").Find(&products)
```

### ✅ WAJIB: Transaction untuk Operasi Multi-Step

```go
// ✅ BENAR: gunakan DB transaction untuk operasi atomik
err := db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
    // Kurangi stok
    if err := tx.Model(&inventory).Update("quantity", gorm.Expr("quantity - ?", qty)).Error; err != nil {
        return err  // auto rollback
    }
    
    // Buat transaksi
    if err := tx.Create(&transaction).Error; err != nil {
        return err  // auto rollback
    }
    
    return nil  // commit
})
```

### ✅ WAJIB: Index di Semua Foreign Key

```sql
-- Setiap foreign key column WAJIB punya index
CREATE INDEX idx_transactions_outlet_id ON transactions(outlet_id);
CREATE INDEX idx_transactions_customer_id ON transactions(customer_id) WHERE customer_id IS NOT NULL;
```

---

## 5. API Handler Rules

### ✅ WAJIB: Validasi Semua Input

```go
type CreateProductRequest struct {
    Name         string  `json:"name" validate:"required,min=1,max=255"`
    SellingPrice float64 `json:"selling_price" validate:"required,min=0.01,max=999999999"`
    CategoryID   string  `json:"category_id" validate:"required,uuid4"`
}

func (h *ProductHandler) Create(c *fiber.Ctx) error {
    var req CreateProductRequest
    if err := c.BodyParser(&req); err != nil {
        return fiber.NewError(400, "Invalid request body")
    }
    
    // WAJIB: validasi sebelum proses
    if err := h.validator.Struct(req); err != nil {
        return mapValidationErrors(err)
    }
    
    // ... proses
}
```

### ✅ WAJIB: Standard Response Format

```go
// Selalu gunakan shared/pkg/response
import "github.com/extendedsynaptic/xynpos/shared/pkg/response"

// ✅ Success
return c.JSON(response.Success(data))

// ✅ Success with pagination
return c.JSON(response.SuccessList(items, pagination))

// ✅ Error
return c.Status(404).JSON(response.Error("PRODUCT_NOT_FOUND", "Produk tidak ditemukan"))

// ❌ JANGAN return custom format
return c.JSON(fiber.Map{"ok": true, "result": data})  // JANGAN
```

### ✅ WAJIB: Tidak Ada Business Logic di Handler

```go
// ❌ SALAH: business logic di handler
func (h *TransactionHandler) Create(c *fiber.Ctx) error {
    // ... parse request
    
    // INI BUSINESS LOGIC — tidak boleh di handler!
    if product.Stock < req.Quantity {
        return fiber.NewError(422, "Stok tidak cukup")
    }
    product.Stock -= req.Quantity
    db.Save(&product)
    // ...
}

// ✅ BENAR: handler hanya orchestrate
func (h *TransactionHandler) Create(c *fiber.Ctx) error {
    var req CreateTransactionRequest
    // parse + validate
    
    result, err := h.usecase.CreateTransaction(c.Context(), tenantID, req)
    if err != nil {
        return mapError(err)  // map domain error ke HTTP
    }
    
    return c.Status(201).JSON(response.Success(result))
}
```

---

## 6. Security Rules

### ✅ WAJIB: Tenant Context di Setiap Handler

```go
// Middleware sudah set tenant context — SELALU gunakan ini
func (h *ProductHandler) List(c *fiber.Ctx) error {
    tenantID := c.Locals("tenantID").(string)  // dari JWT middleware
    outletID := c.Locals("outletID").(string)  // dari JWT middleware
    
    // JANGAN pakai tenantID dari request body/query param
    // ❌ tenantID := c.Query("tenant_id")  // SANGAT BERBAHAYA
}
```

### ✅ WAJIB: Validasi Authorization di Setiap Endpoint

```go
// Setiap route harus ada middleware authorization
app.Get("/v1/reports/sales",
    middleware.RequireAuth(),              // validate JWT
    middleware.RequirePermission("report:read"),  // check permission
    middleware.RequirePlan("starter"),     // check plan minimum
    handler.GetSalesReport,
)
```

### ✅ WAJIB: Tidak Ada Secret di Kode

```go
// ❌ JANGAN hardcode secret
const jwtSecret = "mysupersecret123"

// ✅ Ambil dari environment
jwtSecret := os.Getenv("JWT_ACCESS_SECRET")
if jwtSecret == "" {
    log.Fatal("JWT_ACCESS_SECRET is required")
}
```

---

## 7. Testing Rules

### ✅ WAJIB: Test Coverage Minimum 70%

```bash
# Cek sebelum PR
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out | grep total
# Harus >= 70.0%
```

### ✅ WAJIB: Test File untuk Setiap Usecase

```
transaction_usecase_impl.go  → WAJIB ada transaction_usecase_test.go
product_handler.go           → WAJIB ada product_handler_test.go
```

### ✅ WAJIB: Table-Driven Tests untuk Multiple Cases

```go
// ✅ BENAR: table-driven test
func TestCreateTransaction(t *testing.T) {
    tests := []struct {
        name    string
        req     CreateTransactionRequest
        wantErr error
    }{
        {
            name: "success with cash payment",
            req:  CreateTransactionRequest{/* ... */},
            wantErr: nil,
        },
        {
            name: "fail with insufficient stock",
            req:  CreateTransactionRequest{/* quantity too high */},
            wantErr: domain.ErrInsufficientStock,
        },
        {
            name: "fail with invalid payment amount",
            req:  CreateTransactionRequest{/* payment < total */},
            wantErr: domain.ErrInvalidPaymentAmount,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // setup mocks
            _, err := uc.CreateTransaction(ctx, "tenant-1", tt.req)
            assert.ErrorIs(t, err, tt.wantErr)
        })
    }
}
```

---

## 8. Performance Rules

### ✅ WAJIB: Benchmark untuk Kode Kritis

```go
// Untuk fungsi yang dipanggil dalam hot path (misal: checkout)
func BenchmarkCreateTransaction(b *testing.B) {
    // setup
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        uc.CreateTransaction(ctx, "tenant-1", validReq)
    }
}
```

### ✅ WAJIB: Context Timeout untuk External Calls

```go
// Setiap call ke external service wajib punya timeout
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()

result, err := xenditClient.CreateQRIS(ctx, req)
```

### ✅ WAJIB: Database Query Pagination

```go
// TIDAK BOLEH query tanpa limit untuk list endpoint
// ❌ JANGAN
var products []Product
db.Find(&products)  // Bisa return 1 juta row!

// ✅ BENAR: selalu paginate
var products []Product
db.Limit(req.PerPage).Offset((req.Page-1)*req.PerPage).Find(&products)
```

---

## 9. Code Review Checklist (Self-Review)

Sebelum submit PR, centang semua ini:

```
STRUCTURE:
[ ] Clean architecture tidak dilanggar (tidak ada DB call di usecase langsung)
[ ] File naming snake_case
[ ] Tidak ada business logic di handler

ERROR HANDLING:
[ ] Semua error di-wrap dengan konteks
[ ] Domain error defined untuk error bisnis
[ ] Tidak ada panic di production code

SECURITY:
[ ] Tidak ada hardcoded secret
[ ] Input validation di semua handler
[ ] Tenant context dari JWT, bukan dari request
[ ] Tidak ada SQL string concatenation

DATABASE:
[ ] Semua query pakai context
[ ] Tidak ada SELECT *
[ ] Multi-step operation pakai DB transaction
[ ] Index ada untuk FK columns

TESTING:
[ ] Coverage >= 70%
[ ] Test untuk happy path DAN error cases
[ ] Table-driven test untuk multiple cases

LOGGING:
[ ] Pakai structured logging (zap)
[ ] Tidak ada log data sensitif
[ ] Log level sesuai

API:
[ ] Response pakai standard format
[ ] Swagger doc diupdate: make be-swagger SVC=...
[ ] Pagination untuk list endpoint
```

---

*Rules ini adalah living document. Propose perubahan via PR ke file ini dengan diskusi di PR comment.*
*Last updated: 2025 | Extended Synaptic — XynPOS*
