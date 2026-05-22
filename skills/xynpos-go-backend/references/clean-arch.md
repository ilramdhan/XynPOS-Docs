# Go Clean Architecture Patterns

## Full Service Structure

```
{service-name}/
├── cmd/
│   └── main.go                  ← DI wiring, server start
├── internal/
│   ├── domain/
│   │   ├── {entity}.go          ← Structs, business methods
│   │   └── errors.go            ← var ErrXxx = errors.New(...)
│   ├── repository/
│   │   ├── {entity}_repository.go  ← Interface only
│   │   ├── postgres/
│   │   │   └── {entity}_postgres.go ← Implementation
│   │   └── mock/                ← mockery-generated mocks
│   ├── usecase/
│   │   ├── {entity}_usecase.go      ← Interface
│   │   ├── {entity}_usecase_impl.go ← Implementation
│   │   └── {entity}_usecase_test.go ← Table-driven tests
│   ├── delivery/
│   │   ├── http/
│   │   │   ├── {entity}_handler.go
│   │   │   ├── {entity}_handler_test.go
│   │   │   ├── request.go       ← Input DTOs with validate tags
│   │   │   ├── response.go      ← Output DTOs
│   │   │   └── middleware/
│   │   │       ├── auth.go      ← JWT validation
│   │   │       ├── tenant.go    ← search_path + tenant context
│   │   │       └── rate_limit.go
│   │   └── grpc/
│   │       └── {service}_handler.go
│   └── event/
│       ├── publisher.go         ← NATS publish helpers
│       └── subscriber.go        ← NATS event handlers
├── migrations/
│   ├── 000001_init.up.sql
│   └── 000001_init.down.sql
├── config/
│   └── config.go                ← Viper env loader
├── Dockerfile
├── .env.example
├── go.mod
└── Makefile
```

## main.go DI Pattern

```go
func main() {
    cfg := config.Load()
    log := logger.New(cfg.LogLevel)
    
    db  := database.NewPostgres(cfg.DatabaseURL)
    rdb := redis.NewClient(cfg.RedisURL)
    nc  := nats.Connect(cfg.NatsURL)
    
    // Wire layers bottom-up
    productRepo    := postgres.NewProductRepository(db)
    inventoryRepo  := postgres.NewInventoryRepository(db)
    productUsecase := usecase.NewProductUsecase(productRepo, inventoryRepo, log)
    productHandler := http.NewProductHandler(productUsecase, validator.New())
    
    app := fiber.New(fiber.Config{ErrorHandler: http.GlobalErrorHandler})
    
    // Middleware stack
    app.Use(middleware.Logger(log))
    app.Use(middleware.Recover())
    
    // Routes with auth + tenant middleware
    v1 := app.Group("/v1", middleware.Auth(cfg.JWTSecret))
    http.RegisterProductRoutes(v1, productHandler)
    
    log.Info("starting", zap.Int("port", cfg.Port))
    app.Listen(fmt.Sprintf(":%d", cfg.Port))
}
```

## Domain Entity Pattern

```go
// domain/product.go — NO imports from infra
package domain

import "time"

type Product struct {
    ID           string
    TenantID     string
    Name         string
    SKU          string
    SellingPrice float64
    CostPrice    float64
    Stock        float64
    IsActive     bool
    CreatedAt    time.Time
    UpdatedAt    time.Time
}

// Business methods belong here
func (p *Product) IsAvailable() bool {
    return p.IsActive && p.Stock > 0
}

func (p *Product) CanSell(qty float64) bool {
    return p.IsAvailable() && p.Stock >= qty
}
```

## Repository Interface Pattern

```go
// repository/product_repository.go
package repository

import (
    "context"
    "xynpos/product-service/internal/domain"
)

type ProductRepository interface {
    FindByID(ctx context.Context, id string) (*domain.Product, error)
    FindAll(ctx context.Context, filter ProductFilter) ([]domain.Product, int64, error)
    Create(ctx context.Context, product *domain.Product) error
    Update(ctx context.Context, product *domain.Product) error
    SoftDelete(ctx context.Context, id string) error
    FindBySKU(ctx context.Context, sku string) (*domain.Product, error)
    FindByBarcode(ctx context.Context, barcode string) (*domain.Product, error)
}

type ProductFilter struct {
    Search     string
    CategoryID string
    IsActive   *bool
    OutletID   string
    Page       int
    PerPage    int
}
```

## Usecase Pattern

```go
// usecase/product_usecase_impl.go
type productUsecase struct {
    repo   repository.ProductRepository  // interface, not concrete
    logger *zap.Logger
}

func (u *productUsecase) CreateProduct(ctx context.Context, tenantID string, req CreateProductRequest) (*domain.Product, error) {
    // Business validation
    if req.SellingPrice <= 0 {
        return nil, domain.ErrInvalidPrice
    }
    
    // Check SKU uniqueness
    existing, _ := u.repo.FindBySKU(ctx, req.SKU)
    if existing != nil {
        return nil, domain.ErrSKUAlreadyExists
    }
    
    product := &domain.Product{
        ID:           uuid.New().String(),
        Name:         req.Name,
        SKU:          req.SKU,
        SellingPrice: req.SellingPrice,
        IsActive:     true,
    }
    
    if err := u.repo.Create(ctx, product); err != nil {
        return nil, fmt.Errorf("create product: %w", err)
    }
    
    return product, nil
}
```

## Request Validation Pattern

```go
// delivery/http/request.go
type CreateProductRequest struct {
    Name         string   `json:"name" validate:"required,min=1,max=255"`
    SKU          string   `json:"sku" validate:"omitempty,alphanum,max=100"`
    SellingPrice float64  `json:"selling_price" validate:"required,min=0.01,max=999999999"`
    CostPrice    float64  `json:"cost_price" validate:"min=0"`
    CategoryID   string   `json:"category_id" validate:"required,uuid4"`
    Description  string   `json:"description" validate:"omitempty,max=2000"`
    IsActive     *bool    `json:"is_active"`
}
```

## NATS Event Publishing

```go
// event/publisher.go
func (p *Publisher) PublishTransactionCompleted(ctx context.Context, tx *domain.Transaction) error {
    event := cloudevents.NewEvent()
    event.SetType("pos.transaction.completed")
    event.SetSource("/services/pos")
    event.SetExtension("tenantid", tx.TenantID)
    event.SetData("application/json", tx)
    
    data, _ := json.Marshal(event)
    return p.nc.Publish("pos.transaction.completed", data)
}
```
