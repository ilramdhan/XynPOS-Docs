# XynPOS Service Map

## All 12 Microservices

| Service | Port | Primary Responsibility | DB Schema |
|---------|------|----------------------|-----------|
| `auth-service` | 8001 | Register, login, JWT, refresh token, OAuth, OTP | `auth_svc` + `public_xyn.users` |
| `tenant-service` | 8002 | Tenant CRUD, outlet management, subscription status check | `public_xyn.tenants` |
| `product-service` | 8003 | Products, categories, variants, modifiers, barcode | `tenant_*` |
| `inventory-service` | 8004 | Stock levels, movements, PO, stocktake, transfer | `tenant_*` |
| `pos-service` | 8005 | Transactions, cart, cashier sessions, table mgmt, offline sync | `tenant_*` |
| `payment-service` | 8006 | QRIS, VA, e-wallet, Xendit/Midtrans webhooks, subscription billing | `tenant_*` + `public_xyn` |
| `customer-service` | 8007 | Customer CRM, loyalty points, debt tracking | `tenant_*` |
| `report-service` | 8008 | Sales reports, inventory reports, dashboard, exports (read replica) | `tenant_*` read-only |
| `notification-service` | 8009 | Push (FCM), email (Resend), WA (Wave 5), queue consumer | Redis queue |
| `file-service` | 8010 | Image upload, Cloudflare R2, resize/convert, CDN URL | R2 |
| `subscription-service` | 8011 | Plan management, billing cycles, invoice generation | `public_xyn` |
| `audit-service` | 8012 | Immutable audit log for all sensitive actions | `tenant_*` |

## Shared Packages (`backend/shared/`)

| Package | Path | Purpose |
|---------|------|---------|
| `response` | `shared/pkg/response` | Standard success/error response format |
| `jwt` | `shared/pkg/jwt` | JWT sign/validate, claims struct |
| `database` | `shared/pkg/database` | GORM + PgBouncer connection |
| `redis` | `shared/pkg/redis` | Redis client wrapper |
| `logger` | `shared/pkg/logger` | Zap structured logger |
| `errors` | `shared/pkg/errors` | Domain error types + HTTP mapping |
| `validator` | `shared/pkg/validator` | go-playground/validator setup |
| `pagination` | `shared/pkg/pagination` | Offset + cursor pagination helpers |
| `middleware` | `shared/pkg/middleware` | Auth, tenant, rate-limit, logger middlewares |
| `proto` | `shared/proto/` | Generated protobuf for gRPC |

## Service Internal Structure (every service)

```
{service}/
├── cmd/main.go              Entry point + dependency wiring
├── internal/
│   ├── domain/              Entities, business rules, error vars
│   ├── repository/          Interface + postgres/ implementation
│   ├── usecase/             Business logic (orchestrates repos)
│   ├── delivery/
│   │   ├── http/            Fiber handlers, request/response DTOs
│   │   └── grpc/            gRPC server handlers
│   └── event/               NATS publisher + subscriber
├── migrations/              golang-migrate SQL files
└── config/config.go         Viper env config loader
```

## Health Check Endpoints (every service)

```
GET /health  → liveness  (always UP if process running)
GET /ready   → readiness (DOWN if postgres/redis unreachable)
GET /metrics → Prometheus metrics
```

## gRPC Contracts

```protobuf
// auth.proto
service AuthService {
  rpc ValidateToken(TokenRequest) returns (TokenResponse);
  rpc GetUserPermissions(UserRequest) returns (PermissionsResponse);
}

// inventory.proto  
service InventoryService {
  rpc CheckStock(StockCheckRequest) returns (StockCheckResponse);
  rpc DeductStock(DeductStockRequest) returns (DeductStockResponse);
  rpc ReserveStock(ReserveRequest) returns (ReserveResponse);
}

// product.proto
service ProductService {
  rpc GetProduct(ProductRequest) returns (ProductResponse);
  rpc GetProductBatch(BatchRequest) returns (BatchResponse);
}
```
