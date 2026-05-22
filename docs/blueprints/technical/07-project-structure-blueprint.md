# XynPOS — Blueprint 07: Project Structure Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Repository Strategy

### Pilihan: Monorepo dengan Nx atau Turborepo

**Keputusan: Monorepo** untuk XynPOS karena:
- Tim kecil (2–5 orang) → semua di satu tempat
- Shared types, utils, dan contracts bisa di-share
- Single CI/CD pipeline lebih mudah di-maintain
- Easier refactor cross-service
- Deploy independen tetap bisa per service

**Tool:** Tidak pakai Nx/Turborepo untuk BE Go (overkill). Pakai **simple workspace** dengan top-level Makefile dan GitHub Actions per service.

---

## 2. Root Repository Structure

```
xynpos/                                   ← Root monorepo
├── .github/                              ← GitHub config
│   ├── workflows/                        ← CI/CD pipelines
│   │   ├── auth-service.yml
│   │   ├── pos-service.yml
│   │   ├── web-frontend.yml
│   │   ├── mobile-app.yml
│   │   └── deploy-staging.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   └── CODEOWNERS
│
├── backend/                              ← All Go microservices
│   ├── services/
│   │   ├── auth-service/
│   │   ├── tenant-service/
│   │   ├── pos-service/
│   │   ├── product-service/
│   │   ├── inventory-service/
│   │   ├── payment-service/
│   │   ├── customer-service/
│   │   ├── report-service/
│   │   ├── notification-service/
│   │   ├── file-service/
│   │   ├── subscription-service/
│   │   └── audit-service/
│   ├── shared/                           ← Shared Go packages
│   │   ├── pkg/
│   │   │   ├── jwt/
│   │   │   ├── database/
│   │   │   ├── redis/
│   │   │   ├── logger/
│   │   │   ├── validator/
│   │   │   ├── response/
│   │   │   └── errors/
│   │   └── proto/                        ← Protobuf definitions
│   │       ├── auth.proto
│   │       ├── inventory.proto
│   │       └── product.proto
│   └── gateway/                          ← Kong config
│       ├── kong.yml
│       └── plugins/
│
├── frontend/                             ← Next.js web app
│   ├── apps/
│   │   ├── web-pos/                      ← POS cashier interface
│   │   └── web-dashboard/                ← Owner/Manager dashboard
│   └── packages/
│       ├── ui/                           ← Shared UI components
│       ├── types/                        ← Shared TypeScript types
│       └── utils/                        ← Shared utilities
│
├── mobile/                               ← Flutter app
│   └── xynpos_mobile/
│
├── infra/                                ← Infrastructure as Code
│   ├── terraform/
│   ├── kubernetes/
│   ├── docker/
│   └── scripts/
│
├── docs/                                 ← Documentation
│   ├── blueprints/                       ← Blueprint documents (ini)
│   ├── api/                              ← API documentation
│   ├── runbooks/                         ← Operational runbooks
│   └── adr/                              ← Architecture Decision Records
│
├── .env.example                          ← Environment template
├── docker-compose.yml                    ← Local dev environment
├── docker-compose.override.yml           ← Local overrides (gitignored)
├── Makefile                              ← Common commands
└── README.md
```

---

## 3. Backend Service Structure (Go)

### 3.1 Standard Structure per Microservice

Semua service mengikuti pattern yang sama untuk konsistensi:

```
backend/services/pos-service/
│
├── cmd/
│   └── main.go                          ← Entry point, dependency injection
│
├── internal/                            ← Business logic (tidak di-export)
│   ├── domain/                          ← Entities & business rules
│   │   ├── transaction.go               ← Domain model
│   │   ├── transaction_test.go
│   │   └── errors.go                    ← Domain-specific errors
│   │
│   ├── repository/                      ← Data access layer (interfaces + impl)
│   │   ├── transaction_repository.go    ← Interface
│   │   ├── postgres/
│   │   │   └── transaction_postgres.go  ← PostgreSQL implementation
│   │   └── mock/
│   │       └── transaction_mock.go      ← Mock untuk testing (mockery)
│   │
│   ├── usecase/                         ← Business logic / use cases
│   │   ├── transaction_usecase.go       ← Interface
│   │   ├── transaction_usecase_impl.go  ← Implementation
│   │   └── transaction_usecase_test.go
│   │
│   ├── delivery/                        ← Transport layer
│   │   ├── http/
│   │   │   ├── transaction_handler.go   ← HTTP handlers
│   │   │   ├── transaction_handler_test.go
│   │   │   ├── request.go               ← Request DTOs
│   │   │   ├── response.go              ← Response DTOs
│   │   │   └── middleware/
│   │   │       ├── auth.go
│   │   │       ├── tenant.go
│   │   │       └── rate_limit.go
│   │   └── grpc/                        ← gRPC handlers (if applicable)
│   │       └── pos_grpc_handler.go
│   │
│   └── event/                           ← Event handling (NATS)
│       ├── publisher.go
│       └── subscriber.go
│
├── migrations/                          ← Database migrations (per tenant schema)
│   ├── 000001_create_transactions.up.sql
│   ├── 000001_create_transactions.down.sql
│   └── ...
│
├── config/
│   └── config.go                        ← Viper config loader
│
├── docs/                                ← Swagger generated docs
│   └── swagger.json
│
├── Dockerfile
├── .env.example
├── go.mod
├── go.sum
└── Makefile                             ← Service-specific commands
```

### 3.2 main.go Pattern (Dependency Injection)

```go
// cmd/main.go
package main

import (
    "github.com/gofiber/fiber/v2"
    "xynpos/pos-service/config"
    "xynpos/pos-service/internal/delivery/http"
    "xynpos/pos-service/internal/repository/postgres"
    "xynpos/pos-service/internal/usecase"
    "xynpos/shared/pkg/database"
    "xynpos/shared/pkg/logger"
)

func main() {
    cfg := config.Load()
    log := logger.New(cfg.LogLevel)
    db := database.NewPostgres(cfg.DatabaseURL)
    redis := redis.NewClient(cfg.RedisURL)
    
    // Wire dependencies
    txRepo := postgres.NewTransactionRepository(db)
    txUsecase := usecase.NewTransactionUsecase(txRepo, redis, log)
    txHandler := http.NewTransactionHandler(txUsecase)
    
    // Setup Fiber
    app := fiber.New(fiber.Config{
        ErrorHandler: http.ErrorHandler,
    })
    
    // Routes
    http.SetupRoutes(app, txHandler)
    
    log.Info("POS Service starting on port", cfg.Port)
    app.Listen(":" + cfg.Port)
}
```

### 3.3 Shared Packages Structure

```
backend/shared/
│
├── pkg/
│   ├── database/
│   │   ├── postgres.go         ← GORM connection + PgBouncer
│   │   └── redis.go            ← Redis connection
│   │
│   ├── jwt/
│   │   ├── jwt.go              ← Generate & validate JWT
│   │   └── claims.go           ← JWT claims struct
│   │
│   ├── logger/
│   │   └── zap.go              ← Zap logger setup
│   │
│   ├── response/
│   │   └── response.go         ← Standard API response format
│   │
│   ├── validator/
│   │   └── validator.go        ← go-playground/validator setup
│   │
│   ├── errors/
│   │   └── errors.go           ← Standard error types & codes
│   │
│   ├── pagination/
│   │   └── pagination.go       ← Cursor & offset pagination
│   │
│   └── middleware/
│       ├── auth.go             ← JWT validation middleware
│       ├── tenant.go           ← Tenant context middleware
│       ├── logger.go           ← Request logging
│       └── rate_limit.go       ← Redis-based rate limiting
│
└── proto/
    ├── auth/
    │   ├── auth.proto
    │   └── auth.pb.go          ← Generated (do not edit)
    ├── inventory/
    │   ├── inventory.proto
    │   └── inventory.pb.go
    └── product/
        ├── product.proto
        └── product.pb.go
```

---

## 4. Frontend Web Structure (Next.js)

```
frontend/
│
├── apps/
│   ├── web-pos/                          ← Kasir interface (full screen, touch-optimized)
│   │   ├── src/
│   │   │   ├── app/                      ← Next.js App Router
│   │   │   │   ├── (auth)/
│   │   │   │   │   ├── login/page.tsx
│   │   │   │   │   └── register/page.tsx
│   │   │   │   ├── (pos)/
│   │   │   │   │   ├── layout.tsx
│   │   │   │   │   ├── page.tsx          ← Main POS screen
│   │   │   │   │   ├── hold/page.tsx
│   │   │   │   │   └── tables/page.tsx
│   │   │   │   └── api/                  ← API routes (if needed)
│   │   │   │
│   │   │   ├── components/
│   │   │   │   ├── pos/
│   │   │   │   │   ├── ProductGrid.tsx
│   │   │   │   │   ├── Cart.tsx
│   │   │   │   │   ├── CartItem.tsx
│   │   │   │   │   ├── PaymentModal.tsx
│   │   │   │   │   ├── ReceiptModal.tsx
│   │   │   │   │   └── SearchBar.tsx
│   │   │   │   └── layout/
│   │   │   │       ├── Sidebar.tsx
│   │   │   │       └── Header.tsx
│   │   │   │
│   │   │   ├── hooks/
│   │   │   │   ├── useCart.ts
│   │   │   │   ├── useProducts.ts
│   │   │   │   ├── usePayment.ts
│   │   │   │   └── useBarcodeScanner.ts
│   │   │   │
│   │   │   ├── store/                    ← Zustand stores
│   │   │   │   ├── cartStore.ts
│   │   │   │   ├── outletStore.ts
│   │   │   │   └── offlineStore.ts       ← IndexedDB via Dexie
│   │   │   │
│   │   │   ├── lib/
│   │   │   │   ├── api.ts                ← Axios/fetch client
│   │   │   │   ├── offline.ts            ← Dexie offline DB
│   │   │   │   └── printer.ts            ← QZ-Tray integration
│   │   │   │
│   │   │   └── types/
│   │   │
│   │   ├── public/
│   │   ├── next.config.ts
│   │   ├── tailwind.config.ts
│   │   └── package.json
│   │
│   └── web-dashboard/                    ← Owner/Manager dashboard
│       ├── src/
│       │   ├── app/
│       │   │   ├── (auth)/
│       │   │   ├── (dashboard)/
│       │   │   │   ├── layout.tsx
│       │   │   │   ├── page.tsx          ← Dashboard home
│       │   │   │   ├── products/
│       │   │   │   ├── inventory/
│       │   │   │   ├── customers/
│       │   │   │   ├── reports/
│       │   │   │   ├── settings/
│       │   │   │   └── subscription/
│       │   │   └── api/
│       │   │
│       │   ├── components/
│       │   │   ├── dashboard/
│       │   │   ├── products/
│       │   │   ├── reports/
│       │   │   └── shared/
│       │   │
│       │   ├── hooks/
│       │   ├── store/
│       │   ├── lib/
│       │   └── types/
│       │
│       └── package.json
│
└── packages/
    ├── ui/                               ← Shared component library
    │   ├── src/
    │   │   ├── components/
    │   │   │   ├── Button.tsx
    │   │   │   ├── Input.tsx
    │   │   │   ├── Modal.tsx
    │   │   │   ├── Table.tsx
    │   │   │   └── ...
    │   │   └── index.ts
    │   └── package.json
    │
    ├── types/                            ← Shared TypeScript types
    │   ├── src/
    │   │   ├── api.types.ts              ← API request/response types
    │   │   ├── models.types.ts           ← Domain models
    │   │   └── index.ts
    │   └── package.json
    │
    └── utils/
        ├── src/
        │   ├── currency.ts               ← Format Rupiah
        │   ├── date.ts                   ← Date formatting
        │   └── validation.ts
        └── package.json
```

---

## 5. Mobile App Structure (Flutter)

```
mobile/xynpos_mobile/
│
├── lib/
│   ├── main.dart                         ← App entry point
│   ├── app.dart                          ← MaterialApp + routing setup
│   │
│   ├── core/                             ← Core infrastructure
│   │   ├── constants/
│   │   │   ├── api_constants.dart
│   │   │   ├── storage_keys.dart
│   │   │   └── app_colors.dart
│   │   ├── di/
│   │   │   └── injection.dart            ← Dependency injection (Riverpod)
│   │   ├── network/
│   │   │   ├── dio_client.dart
│   │   │   ├── interceptors/
│   │   │   │   ├── auth_interceptor.dart
│   │   │   │   └── retry_interceptor.dart
│   │   │   └── api_result.dart           ← Result<T, Error> type
│   │   ├── storage/
│   │   │   ├── hive_service.dart         ← Key-value offline
│   │   │   └── secure_storage.dart       ← Token storage
│   │   ├── offline/
│   │   │   ├── offline_database.dart     ← SQLite schema
│   │   │   ├── sync_manager.dart         ← Offline sync logic
│   │   │   └── conflict_resolver.dart
│   │   └── utils/
│   │       ├── currency_formatter.dart
│   │       ├── date_formatter.dart
│   │       └── logger.dart
│   │
│   ├── features/                         ← Feature-first organization
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   │   ├── datasources/
│   │   │   │   │   └── auth_remote_datasource.dart
│   │   │   │   ├── models/
│   │   │   │   │   └── user_model.dart
│   │   │   │   └── repositories/
│   │   │   │       └── auth_repository_impl.dart
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   └── user_entity.dart
│   │   │   │   ├── repositories/
│   │   │   │   │   └── auth_repository.dart
│   │   │   │   └── usecases/
│   │   │   │       ├── login_usecase.dart
│   │   │   │       └── logout_usecase.dart
│   │   │   └── presentation/
│   │   │       ├── providers/            ← Riverpod providers
│   │   │       │   └── auth_provider.dart
│   │   │       ├── screens/
│   │   │       │   └── login_screen.dart
│   │   │       └── widgets/
│   │   │           └── login_form.dart
│   │   │
│   │   ├── pos/                          ← Main kasir feature
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   │       ├── providers/
│   │   │       │   ├── cart_provider.dart
│   │   │       │   ├── products_provider.dart
│   │   │       │   └── transaction_provider.dart
│   │   │       ├── screens/
│   │   │       │   ├── pos_screen.dart
│   │   │       │   ├── payment_screen.dart
│   │   │       │   └── receipt_screen.dart
│   │   │       └── widgets/
│   │   │           ├── product_grid.dart
│   │   │           ├── cart_panel.dart
│   │   │           └── payment_keypad.dart
│   │   │
│   │   ├── products/
│   │   ├── inventory/
│   │   ├── customers/
│   │   ├── reports/
│   │   │   └── presentation/
│   │   │       ├── screens/
│   │   │       │   └── dashboard_screen.dart  ← Mobile dashboard
│   │   │       └── widgets/
│   │   │           └── sales_chart.dart
│   │   └── settings/
│   │
│   └── shared/                           ← Shared widgets & utilities
│       ├── widgets/
│       │   ├── xyn_button.dart
│       │   ├── xyn_text_field.dart
│       │   ├── xyn_loading.dart
│       │   └── xyn_error_widget.dart
│       └── router/
│           └── app_router.dart           ← go_router setup
│
├── assets/
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── test/
│   ├── unit/
│   ├── widget/
│   └── integration/
│
├── android/
├── ios/
├── pubspec.yaml
└── pubspec.lock
```

---

## 6. Infrastructure Structure

```
infra/
│
├── terraform/
│   ├── environments/
│   │   ├── staging/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── terraform.tfvars
│   │   └── production/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── terraform.tfvars
│   └── modules/
│       ├── digitalocean-droplet/
│       ├── digitalocean-database/
│       ├── digitalocean-redis/
│       └── cloudflare-r2/
│
├── kubernetes/                           ← K8s manifests (Phase 2)
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   └── secrets.yaml
│   ├── services/
│   │   ├── auth-service/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── hpa.yaml               ← Horizontal Pod Autoscaler
│   │   └── pos-service/
│   └── overlays/
│       ├── staging/
│       └── production/
│
├── docker/
│   ├── Dockerfile.go.template           ← Multi-stage Go Dockerfile template
│   ├── Dockerfile.nextjs                ← Next.js Dockerfile
│   └── nginx/
│       └── nginx.conf
│
└── scripts/
    ├── db-migrate.sh                    ← Run migrations
    ├── setup-local.sh                   ← Local dev setup
    └── deploy.sh                        ← Deployment helper
```

---

## 7. Docker Compose (Local Development)

```yaml
# docker-compose.yml (ringkasan)
version: '3.9'

services:
  # Databases
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: xynpos_dev
      POSTGRES_USER: xynpos
      POSTGRES_PASSWORD: dev_password
    ports: ["5432:5432"]
    volumes: ["postgres_data:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  # Message Queue
  nats:
    image: nats:2-alpine
    ports: ["4222:4222", "8222:8222"]

  # Search
  meilisearch:
    image: getmeili/meilisearch:latest
    ports: ["7700:7700"]

  # Services
  auth-service:
    build: ./backend/services/auth-service
    env_file: ./backend/services/auth-service/.env
    ports: ["8001:8001"]
    depends_on: [postgres, redis]

  pos-service:
    build: ./backend/services/pos-service
    ports: ["8005:8005"]
    depends_on: [postgres, redis, nats]

  # ... other services

  # API Gateway
  kong:
    image: kong:3.6-alpine
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: /kong/kong.yml
    volumes: ["./backend/gateway/kong.yml:/kong/kong.yml"]
    ports: ["8000:8000", "8443:8443"]

  # Frontend
  web-dashboard:
    build: ./frontend/apps/web-dashboard
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://kong:8000

volumes:
  postgres_data:
```

---

## 8. Makefile (Root Level Commands)

```makefile
# Common developer commands

# Setup
setup:
	@./infra/scripts/setup-local.sh

# Backend
be-auth:
	@cd backend/services/auth-service && go run cmd/main.go

be-pos:
	@cd backend/services/pos-service && go run cmd/main.go

be-test:
	@cd backend && go test ./...

be-lint:
	@cd backend && golangci-lint run ./...

be-swagger:
	@cd backend/services/$(SVC) && swag init -g cmd/main.go

# Migration
migrate-up:
	@./infra/scripts/db-migrate.sh up $(TENANT)

migrate-down:
	@./infra/scripts/db-migrate.sh down $(TENANT)

# Frontend
fe-dev:
	@cd frontend/apps/web-dashboard && pnpm dev

fe-pos-dev:
	@cd frontend/apps/web-pos && pnpm dev

fe-build:
	@cd frontend && pnpm build

# Mobile
mobile-dev:
	@cd mobile/xynpos_mobile && flutter run

mobile-build-android:
	@cd mobile/xynpos_mobile && flutter build appbundle

mobile-build-ios:
	@cd mobile/xynpos_mobile && flutter build ipa

# Docker
docker-up:
	@docker-compose up -d

docker-down:
	@docker-compose down

docker-logs:
	@docker-compose logs -f $(SVC)

# Generate
proto-gen:
	@./infra/scripts/gen-proto.sh

mock-gen:
	@cd backend && mockery --all

# Deploy
deploy-staging:
	@./infra/scripts/deploy.sh staging

deploy-prod:
	@./infra/scripts/deploy.sh production
```

---

## 9. Naming Conventions

### 9.1 Backend (Go)

| Item | Convention | Contoh |
|------|-----------|--------|
| Package | lowercase snake | `pos_service` |
| File | snake_case | `transaction_repository.go` |
| Struct | PascalCase | `TransactionUsecase` |
| Interface | PascalCase + "er" atau explicit | `TransactionRepository` |
| Variable | camelCase | `tenantID` |
| Constant | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| Error variable | Err prefix | `ErrTransactionNotFound` |

### 9.2 Frontend (TypeScript)

| Item | Convention | Contoh |
|------|-----------|--------|
| Component | PascalCase | `ProductGrid.tsx` |
| Hook | use prefix camelCase | `useCartStore.ts` |
| Store | camelCase + Store | `cartStore.ts` |
| Util | camelCase | `formatCurrency.ts` |
| Type/Interface | PascalCase | `TransactionItem` |
| Constant | UPPER_SNAKE | `API_BASE_URL` |

### 9.3 Flutter (Dart)

| Item | Convention | Contoh |
|------|-----------|--------|
| File | snake_case | `cart_provider.dart` |
| Class | PascalCase | `CartNotifier` |
| Provider | camelCase + Provider | `cartProvider` |
| Screen | PascalCase + Screen | `PosScreen` |
| Widget | PascalCase | `ProductCard` |

---

## 10. API Response Standard

Semua API mengikuti response format ini:

```json
// Success
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}

// Error
{
  "success": false,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Produk tidak ditemukan",
    "details": {}
  }
}
```

---

*Blueprint ini inline dengan: BP-05 (Tech Stack), BP-06 (Architecture), BP-11 (API Design)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
