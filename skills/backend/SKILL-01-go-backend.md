---
skill_id: SKILL-01
name: XynPOS Go Backend Development
category: backend
description: Skill untuk semua coding session backend Go — service development, API, database, testing
version: 1.0.0
applies_to: [backend, go, api, database]
depends_on: [SKILL-00]
---

# SKILL-01: Go Backend Development

## Stack & Libraries

```go
// Framework
github.com/gofiber/fiber/v2          // HTTP framework
google.golang.org/grpc               // gRPC inter-service
google.golang.org/protobuf           // Protobuf

// Database
gorm.io/gorm                         // ORM
gorm.io/driver/postgres              // PG driver
github.com/golang-migrate/migrate/v4 // Migrations

// Cache & Queue
github.com/redis/go-redis/v9         // Redis client
github.com/nats-io/nats.go           // NATS client

// Utilities
go.uber.org/zap                      // Structured logging
github.com/go-playground/validator/v10 // Validation
github.com/golang-jwt/jwt/v5         // JWT
github.com/google/uuid               // UUID v4
github.com/spf13/viper               // Config management

// Testing
github.com/stretchr/testify          // Assertions
github.com/vektra/mockery/v2         // Mock generation
github.com/testcontainers/testcontainers-go // DB containers for test
```

## Service Structure (Clean Architecture)

```
{service-name}/
├── cmd/main.go              ← Entry point, DI wiring
├── internal/
│   ├── domain/              ← Entities + business rules (NO infra imports)
│   ├── repository/          ← Interfaces + postgres/ implementation
│   ├── usecase/             ← Business logic (depends on repo interfaces only)
│   ├── delivery/
│   │   ├── http/            ← Fiber handlers, DTOs, middleware
│   │   └── grpc/            ← gRPC handlers
│   └── event/               ← NATS publisher/subscriber
├── migrations/              ← golang-migrate SQL files
└── config/config.go         ← Viper config loader
```

## Layer Dependency Rules

```
delivery → usecase → repository(interface) ← domain
✅ usecase import domain + repository interface
✅ delivery import usecase
❌ usecase import gorm/redis directly
❌ domain import anything from infra
```

## Error Handling Patterns

```go
// ✅ Domain errors
var (
    ErrProductNotFound      = errors.New("product not found")
    ErrInsufficientStock    = errors.New("insufficient stock")
    ErrInvalidPaymentAmount = errors.New("invalid payment amount")
    ErrTenantSuspended      = errors.New("tenant is suspended")
    ErrTransactionNotFound  = errors.New("transaction not found")
)

// ✅ Wrap with context
if err != nil {
    return nil, fmt.Errorf("create transaction: get product %s: %w", id, err)
}

// ✅ Map domain error to HTTP in handler
switch {
case errors.Is(err, domain.ErrProductNotFound):
    return fiber.NewError(404, "Produk tidak ditemukan")
case errors.Is(err, domain.ErrInsufficientStock):
    return fiber.NewError(422, "Stok tidak mencukupi")
default:
    logger.Error("unexpected error", zap.Error(err))
    return fiber.NewError(500, "Internal server error")
}
```

## Standard Response

```go
// Import: github.com/extendedsynaptic/xynpos/shared/pkg/response

// Success single
return c.Status(200).JSON(response.Success(data))

// Success created
return c.Status(201).JSON(response.Success(data))

// Success list with pagination
return c.Status(200).JSON(response.SuccessList(items, response.Pagination{
    Page: req.Page, PerPage: req.PerPage, Total: total,
}))

// Error
return c.Status(404).JSON(response.Error("PRODUCT_NOT_FOUND", "Produk tidak ditemukan"))

// Validation error
return c.Status(422).JSON(response.ValidationError(validationErrors))
```

## Tenant Context (SECURITY CRITICAL)

```go
// ✅ SELALU ambil tenantID dari JWT (sudah di-set middleware)
func (h *Handler) Create(c *fiber.Ctx) error {
    tenantID := c.Locals("tenantID").(string)   // dari JWT
    userID   := c.Locals("userID").(string)     // dari JWT
    role     := c.Locals("role").(string)       // dari JWT
    
    // ❌ JANGAN PERNAH:
    // tenantID := c.Query("tenant_id")         // injection risk!
    // tenantID := req.TenantID                 // injection risk!
}
```

## Database Patterns

```go
// ✅ Always use context
db.WithContext(ctx).Where("id = ?", id).First(&product)

// ✅ Specify columns (no SELECT *)
db.Select("id", "name", "selling_price", "stock").Find(&products)

// ✅ DB transaction for multi-step
db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
    if err := tx.Model(&inv).Update("quantity", gorm.Expr("quantity - ?", qty)).Error; err != nil {
        return err // auto rollback
    }
    if err := tx.Create(&transaction).Error; err != nil {
        return err // auto rollback  
    }
    return nil // commit
})

// ✅ Pagination always
db.Limit(req.PerPage).Offset((req.Page-1)*req.PerPage).Find(&items)
```

## Logging (Zap)

```go
// ✅ Structured fields
logger.Info("transaction created",
    zap.String("tenant_id", tenantID),
    zap.String("tx_id", tx.ID),
    zap.Float64("total", tx.TotalAmount),
    zap.Duration("duration", time.Since(start)),
)

// ✅ Error logging
logger.Error("failed to create transaction",
    zap.String("tenant_id", tenantID),
    zap.Error(err),
)

// ❌ NEVER
fmt.Println("error:", err)
log.Printf("transaction %s created", txID)
logger.Info("login", zap.String("password", req.Password)) // sensitive!
```

## Request Validation

```go
type CreateProductRequest struct {
    Name         string  `json:"name" validate:"required,min=1,max=255"`
    SellingPrice float64 `json:"selling_price" validate:"required,min=0.01"`
    CategoryID   string  `json:"category_id" validate:"required,uuid4"`
    SKU          string  `json:"sku" validate:"omitempty,alphanum,max=100"`
}

// Handler
var req CreateProductRequest
if err := c.BodyParser(&req); err != nil {
    return fiber.NewError(400, "Invalid request body")
}
if err := h.validator.Struct(req); err != nil {
    return mapValidationErrors(err) // → 422 response
}
```

## Testing Pattern

```go
// Table-driven test (WAJIB untuk multiple cases)
func TestCreateTransaction(t *testing.T) {
    tests := []struct{
        name    string
        req     CreateTransactionRequest
        setup   func(*mocks.TransactionRepository)
        wantErr error
    }{
        {
            name: "success",
            req:  validRequest,
            setup: func(m *mocks.TransactionRepository) {
                m.On("Create", mock.Anything, mock.Anything).Return(nil)
            },
            wantErr: nil,
        },
        {
            name: "insufficient stock",
            req:  reqWithHighQty,
            setup: func(m *mocks.TransactionRepository) {},
            wantErr: domain.ErrInsufficientStock,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            mockRepo := mocks.NewTransactionRepository(t)
            tt.setup(mockRepo)
            uc := usecase.New(mockRepo)
            
            _, err := uc.Create(context.Background(), "tenant-1", tt.req)
            assert.ErrorIs(t, err, tt.wantErr)
            mockRepo.AssertExpectations(t)
        })
    }
}
```

## Checklist Sebelum PR

```
[ ] Clean architecture tidak dilanggar
[ ] Error di-wrap dengan konteks
[ ] Tidak ada fmt.Println (pakai zap)
[ ] Tidak ada SELECT *
[ ] Multi-step operations pakai DB transaction
[ ] Semua input divalidasi di handler
[ ] tenantID dari JWT, bukan request
[ ] Test coverage >= 70%
[ ] Table-driven tests untuk multiple cases
[ ] Swagger di-update: make be-swagger SVC={nama-service}
[ ] Tidak ada hardcoded secret
```
