---
name: xynpos-go-backend
description: XynPOS Go backend development — use when writing, reviewing, or debugging Go code for any XynPOS microservice. Covers clean architecture patterns, error handling, GORM database access, JWT/tenant security, Zap logging, Fiber handlers, gRPC, NATS events, and testing. Triggers when a developer asks to create a Go service, write a handler or usecase, fix a Go bug, review Go code, add an API endpoint, write a migration, or work with the XynPOS backend codebase. Also use when questions like "how do I structure this service" or "what's the right way to handle errors" come up.
license: See LICENSE.txt
---

# XynPOS Go Backend Development

This skill covers writing production-quality Go code for XynPOS microservices following the project's established patterns and rules.

## Quick Reference Files

- Full clean architecture patterns → `references/clean-arch.md`
- Database & GORM patterns → `references/database-patterns.md`
- Testing patterns → `references/testing-patterns.md`
- Security rules → `references/security-rules.md`

## Core Rules (non-negotiable)

### 1. Clean Architecture Layers

```
domain/     → pure entities + error vars (NO infra imports — ever)
repository/ → interface definitions + postgres/ implementations
usecase/    → business logic (imports domain + repo interfaces only)
delivery/   → HTTP/gRPC handlers (imports usecase only)
event/      → NATS pub/sub
```

**Dependency direction:** `delivery → usecase → repository(interface) ← domain`

### 2. Error Handling

Always wrap with context:
```go
// ✅
return nil, fmt.Errorf("create transaction: find product %s: %w", productID, err)

// ❌ loses context
return nil, err
```

Define domain errors in `domain/errors.go`:
```go
var (
    ErrProductNotFound   = errors.New("product not found")
    ErrInsufficientStock = errors.New("insufficient stock")
    ErrTenantSuspended   = errors.New("tenant is suspended")
)
```

Map in handler:
```go
switch {
case errors.Is(err, domain.ErrProductNotFound):
    return c.Status(404).JSON(response.Error("PRODUCT_NOT_FOUND", "Produk tidak ditemukan"))
case errors.Is(err, domain.ErrInsufficientStock):
    return c.Status(422).JSON(response.Error("INSUFFICIENT_STOCK", "Stok tidak mencukupi"))
default:
    logger.Error("unexpected", zap.Error(err))
    return c.Status(500).JSON(response.Error("INTERNAL_ERROR", "Internal server error"))
}
```

### 3. Security — Tenant Isolation

```go
// ✅ ALWAYS from JWT via middleware
tenantID := c.Locals("tenantID").(string)
userID   := c.Locals("userID").(string)

// ❌ NEVER from request — injection risk!
tenantID := c.Query("tenant_id")
tenantID := req.TenantID
```

### 4. Logging (Zap only)

```go
// ✅ Structured fields
logger.Info("transaction created",
    zap.String("tenant_id", tenantID),
    zap.String("tx_id", tx.ID),
    zap.Float64("total", tx.TotalAmount),
)

// ❌ NEVER these
fmt.Println("created:", tx.ID)
log.Printf("tx %s", tx.ID)
logger.Info("login", zap.String("password", req.Password)) // sensitive!
```

### 5. Standard Response

```go
// Always use shared/pkg/response
return c.Status(201).JSON(response.Success(data))
return c.Status(200).JSON(response.SuccessList(items, pagination))
return c.Status(422).JSON(response.Error("VALIDATION_ERROR", "..."))
```

## Handler Pattern (complete example)

```go
func (h *ProductHandler) Create(c *fiber.Ctx) error {
    // 1. Extract tenant from JWT (NEVER from request)
    tenantID := c.Locals("tenantID").(string)

    // 2. Parse + validate input
    var req CreateProductRequest
    if err := c.BodyParser(&req); err != nil {
        return c.Status(400).JSON(response.Error("INVALID_BODY", "Invalid request body"))
    }
    if err := h.validator.Struct(req); err != nil {
        return c.Status(422).JSON(response.ValidationError(err))
    }

    // 3. Call usecase (no business logic here)
    product, err := h.usecase.CreateProduct(c.Context(), tenantID, req)
    if err != nil {
        return mapDomainError(c, err)
    }

    // 4. Return standard response
    return c.Status(201).JSON(response.Success(product))
}
```

## Database Patterns

```go
// ✅ Always with context + specify columns + paginate
var products []Product
db.WithContext(ctx).
    Select("id", "name", "selling_price", "stock").
    Where("is_active = ?", true).
    Limit(req.PerPage).
    Offset((req.Page-1)*req.PerPage).
    Find(&products)

// ✅ Transaction for multi-step
db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
    if err := tx.Model(&inv).Update("quantity", gorm.Expr("quantity - ?", qty)).Error; err != nil {
        return err // auto rollback
    }
    return tx.Create(&transaction).Error // commit if nil
})

// ❌ NEVER raw string concat
db.Exec("SELECT * FROM products WHERE name = '" + name + "'")
```

## Quick Test Pattern

```go
func TestCreateProduct_Success(t *testing.T) {
    mockRepo := mocks.NewProductRepository(t)
    mockRepo.On("Create", mock.Anything, mock.Anything).Return(nil)
    
    uc := usecase.NewProductUsecase(mockRepo, logger.Nop())
    _, err := uc.CreateProduct(context.Background(), "tenant-1", validReq)
    
    assert.NoError(t, err)
    mockRepo.AssertExpectations(t)
}
```

For full patterns, read the references/ files.
