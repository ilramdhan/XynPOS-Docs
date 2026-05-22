# XynPOS — Blueprint 06: System Architecture Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Arsitektur Tingkat Tinggi (High-Level Architecture)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENTS                                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│   │  Web Browser │  │  Flutter iOS  │  │ Flutter Droid│                 │
│   │  (Next.js)   │  │  (Mobile App) │  │ (Mobile App) │                 │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└──────────┼─────────────────┼─────────────────┼───────────────────────── ┘
           │                 │                 │
           ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLOUDFLARE EDGE                                  │
│          WAF · DDoS Protection · CDN · SSL Termination                  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (Kong)                              │
│    Rate Limiting · JWT Validation · Request Routing · CORS · Logging    │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────────────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐
│Auth Svc  │ │POS Svc │ │Product │ │Inventory│ │ Report Svc │
│(Go/Fiber)│ │(Go)    │ │Svc (Go)│ │Svc (Go)│ │ (Go)       │
└────┬─────┘ └───┬────┘ └───┬────┘ └───┬────┘ └─────┬──────┘
     │           │          │          │             │
     └───────────┴──────────┴──────────┴─────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │PostgreSQL│   │  Redis   │   │Message Queue │
        │(Primary) │   │(Cache)   │   │(NATS/Kafka)  │
        └────┬─────┘   └──────────┘   └──────┬───────┘
             │                               │
             ▼                               ▼
        ┌──────────┐                  ┌──────────────┐
        │Read      │                  │Notification  │
        │Replica   │                  │Svc (Go)      │
        └──────────┘                  └──────────────┘
```

---

## 2. Multi-Tenant Architecture

### 2.1 Strategi Isolasi Data Tenant

XynPOS menggunakan **hybrid multi-tenancy** yang berkembang sesuai skala:

| Phase | Strategy | Kapan | Pros | Cons |
|-------|----------|-------|------|------|
| **Phase 1** (0–1K tenant) | **Schema per tenant** | Launch–Year 1 | Isolasi kuat, easy backup per tenant | Banyak schema, migration lambat |
| **Phase 2** (1K–10K tenant) | **Row-level dengan tenant_id** | Year 1–2 | Skalabel, migration mudah | Perlu RLS ketat |
| **Phase 3** (10K+ tenant) | **Sharded Database** | Year 2+ | Horizontal scale, performa | Kompleks query |

### 2.2 Schema-per-Tenant Implementation (Phase 1)

```sql
-- Setiap tenant mendapat schema sendiri
-- Contoh: tenant dengan id "tenant_abc123"
CREATE SCHEMA tenant_abc123;

-- Semua tabel dalam schema tenant
CREATE TABLE tenant_abc123.products (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    price DECIMAL(15,2),
    ...
);

-- Global schema untuk data cross-tenant
CREATE SCHEMA public_xyn;
CREATE TABLE public_xyn.tenants (
    id UUID PRIMARY KEY,
    slug VARCHAR(100) UNIQUE,
    name VARCHAR(255),
    subscription_plan VARCHAR(50),
    schema_name VARCHAR(100) UNIQUE,
    ...
);
```

### 2.3 Tenant Context Middleware (Go)

```go
// Middleware: Extract tenant dari JWT, inject ke context
func TenantMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        claims := ExtractJWTClaims(c)
        tenantID := claims.TenantID
        schemaName := "tenant_" + tenantID
        
        // Set PostgreSQL search_path per request
        db.Exec("SET search_path = " + schemaName)
        c.Locals("tenantID", tenantID)
        c.Locals("schema", schemaName)
        return c.Next()
    }
}
```

---

## 3. Authentication & Authorization Architecture

### 3.1 Auth Flow Diagram

```
Client                  API Gateway              Auth Service
  │                         │                        │
  │──── POST /auth/login ───▶│                        │
  │                         │──── Forward request ───▶│
  │                         │                        │ Verify credentials
  │                         │                        │ Generate JWT pair
  │                         │◀── {access, refresh} ──│
  │◀── JWT tokens ──────────│                        │
  │                         │                        │
  │──── GET /products ──────▶│                        │
  │  (Bearer: access_token) │                        │
  │                         │ Validate JWT locally   │
  │                         │ (no round-trip needed) │
  │                         │──── Forward ──────────▶│ Product Service
  │◀── Products data ───────│◀──────────────────────│
```

### 3.2 JWT Structure

```json
// Access Token (15 menit)
{
  "sub": "user_uuid",
  "tenant_id": "tenant_uuid",
  "outlet_id": "outlet_uuid",
  "role": "cashier",
  "permissions": ["pos:create", "pos:read"],
  "plan": "pro",
  "iat": 1234567890,
  "exp": 1234568790
}

// Refresh Token (30 hari) — stored di Redis
{
  "sub": "user_uuid",
  "token_family": "family_uuid",  // Rotation detection
  "iat": 1234567890,
  "exp": 1236567890
}
```

### 3.3 Permission Model

```
Hierarchy: Tenant → Outlet → User → Role → Permissions

Owner      : ALL permissions, semua outlet
Manager    : Read/write produk, laporan semua outlet; no delete tenant
Cashier    : pos:*, customer:read/create, report:self only
Inventory  : inventory:*, product:read/write, no transactions
Viewer     : report:read only, all modules
Custom     : (Enterprise) pilih permission sendiri

Permission Format: "module:action"
Contoh: "pos:create", "product:delete", "report:export", "user:invite"
```

---

## 4. Microservice Communication

### 4.1 Synchronous (REST/gRPC)

Untuk request yang butuh response langsung:

```
Client Request → API Gateway → Service A
                                   ↓ (gRPC internal call)
                               Service B
                                   ↓
                               Response
```

**Kapan pakai gRPC internal:**
- Auth service dipanggil dari semua service untuk validate
- Product service dipanggil dari POS service saat checkout
- Inventory service dipanggil dari POS untuk stok check

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
}
```

### 4.2 Asynchronous (Event-Driven via NATS)

Untuk operasi yang tidak butuh response langsung:

```
POS Service ──publishes──▶ NATS ──subscribes──▶ Notification Service
                                 └────subscribes──▶ Report Service
                                 └────subscribes──▶ Audit Service
                                 └────subscribes──▶ Inventory Service
```

**Event Schema (CloudEvents format):**
```json
{
  "specversion": "1.0",
  "type": "pos.transaction.completed",
  "source": "/services/pos",
  "id": "evt_uuid",
  "time": "2025-01-01T10:00:00Z",
  "tenantid": "tenant_uuid",
  "data": {
    "transaction_id": "txn_uuid",
    "total": 150000,
    "items": [...],
    "payment_method": "cash"
  }
}
```

**Event Topics:**
| Topic | Publisher | Subscribers |
|-------|-----------|------------|
| `pos.transaction.completed` | POS | Inventory, Notification, Report, Audit |
| `pos.transaction.voided` | POS | Inventory, Notification, Audit |
| `inventory.stock.low` | Inventory | Notification |
| `payment.received` | Payment | POS, Notification, Subscription |
| `subscription.plan.changed` | Subscription | Auth (update JWT claims) |
| `user.created` | Auth | Notification (welcome email) |

---

## 5. Data Flow: Transaksi POS

### 5.1 Online Transaction Flow

```
Mobile App / Web
    │
    ├─1──▶ POST /api/v1/pos/transactions
    │       (JWT + cart items)
    │
    ▼
API Gateway
    │ Validate JWT, rate limit
    ├─2──▶ POS Service
    │         │
    │         ├─3──▶ Product Service (gRPC: validate products exist)
    │         ├─4──▶ Inventory Service (gRPC: check & reserve stock)
    │         ├─5──▶ Payment Service (if non-cash: create payment request)
    │         │
    │         ├─6── Save transaction to PostgreSQL
    │         ├─7── Publish event: pos.transaction.created → NATS
    │         │
    │         └─8──▶ Return transaction_id + payment_url
    │
    ├─9── [Async] Inventory: Deduct stock permanently
    ├─9── [Async] Notification: Send receipt
    ├─9── [Async] Report: Update real-time dashboard
    └─9── [Async] Audit: Log transaction
```

### 5.2 Offline Transaction Flow (Mobile)

```
Mobile App (Offline Mode)
    │
    ├─1── Check connectivity: OFFLINE
    ├─2── Save transaction to local Hive DB
    ├─3── Update local product stock (Hive)
    ├─4── Print receipt via Bluetooth printer
    │
    ... [internet restored] ...
    │
    ├─5── Workmanager triggers sync job
    ├─6── Read pending transactions from Hive
    ├─7── POST /api/v1/pos/transactions/batch (sync flag)
    │       ↳ Include: local_created_at, device_id
    │
    ├─8── Server: Validate, dedup (check local_id)
    ├─9── Server: Process normally
    └─10─ Mark local transaction as synced
```

---

## 6. Database Architecture

### 6.1 Connection Flow

```
Services
    │
    ▼
PgBouncer (Connection Pooling)
    │
    ├──▶ PostgreSQL Primary (Read/Write)
    │
    └──▶ PostgreSQL Read Replica (Read-only)
              ↑
              │ Streaming Replication
              │
         Used by: Report Service, Dashboard
```

### 6.2 Database per Service Strategy

Meskipun share satu PostgreSQL cluster (Phase 1), setiap service memiliki **schema sendiri**:

```
PostgreSQL Cluster
├── Schema: public_xyn (global: tenants, subscriptions, billing)
├── Schema: auth_svc (users, refresh_tokens, sessions)
├── Schema: tenant_abc123 (tenant-specific data)
│   ├── products
│   ├── inventory_items
│   ├── transactions
│   ├── customers
│   └── ...
└── Schema: tenant_xyz789
    └── ... (same structure)
```

### 6.3 Redis Key Patterns

```
# Session / JWT Blacklist
session:{user_id}:{device_id}     → JWT refresh token
blacklist:{jti}                    → Blacklisted tokens (TTL = token expiry)

# Rate Limiting
ratelimit:{tenant_id}:{endpoint}  → Counter (TTL 60s)
ratelimit:api:{api_key}           → API rate limit

# Cache
cache:tenant:{tenant_id}:plan     → Subscription plan (TTL 5min)
cache:product:{tenant_id}:{sku}   → Product detail (TTL 10min)
cache:report:{tenant_id}:daily    → Daily summary (TTL 1min)

# Real-time
pubsub:kds:{outlet_id}            → Kitchen display orders
pubsub:stock:{tenant_id}          → Stock updates

# Queue
queue:notification:{priority}     → Notification tasks
queue:sync:{tenant_id}            → Offline sync tasks
```

---

## 7. File & Media Architecture

```
Client Upload (foto produk)
    │
    ▼
File Service (Go)
    │
    ├── Validate: type (jpg/png/webp), size (max 2MB)
    ├── Resize: generate thumbnail (200x200) + medium (800x800)
    ├── Convert: WebP untuk web optimization
    ├── Upload: Cloudflare R2 (S3-compatible)
    │     Bucket: xynpos-media
    │     Path:   /{tenant_id}/products/{product_id}/{size}.webp
    │
    └── Return: CDN URL (via Cloudflare R2 public bucket)
              https://cdn.xynpos.com/{tenant_id}/products/...
```

---

## 8. Payment Architecture

### 8.1 QRIS Dynamic Flow

```
POS Create Order
    │
    ├─1──▶ Payment Service: generate_qris(amount, order_id)
    ├─2──▶ Xendit API: Create QR Code
    │         └──▶ Return: qr_string, qr_image_url, reference_id
    │
    ├─3── Return QR to client
    ├─4── Client display QR (auto-refresh every 5 min)
    │
    ... [User scan & pay] ...
    │
    ├─5── Xendit sends webhook: payment.succeeded
    ├─6── Payment Service validates webhook signature
    ├─7── Update transaction status: pending → paid
    ├─8── Publish event: payment.received → NATS
    ├─9── [Async] POS: Close order
    └─10─ [Async] Notification: Send receipt
```

### 8.2 Subscription Billing Flow

```
Subscription due date reached
    │
    ├─1── Subscription Service: check due tenants (cron job)
    ├─2── Xendit: charge recurring payment
    │
    ├── [SUCCESS] ──▶ Update subscription: extend 30 days
    │                 Send: invoice email
    │
    └── [FAILED] ───▶ Retry: T+1 day, T+3 days
                      Send: payment failed email
                      After 3 failures: downgrade to Free
                      Data retained 30 days
```

---

## 9. Notification Architecture

```
Event Sources (via NATS)
    │
    ▼
Notification Service
    │
    ├── Parse event type
    ├── Load notification template
    ├── Determine channels (push, email, WA)
    │
    ├──▶ Firebase FCM (push notification mobile)
    ├──▶ Resend (email transactional)
    └──▶ WhatsApp Business API (Wave 5)
```

---

## 10. Security Architecture

### 10.1 Defense in Depth

```
Internet
    │
    ├─ Layer 1: Cloudflare (WAF, DDoS, Bot protection)
    ├─ Layer 2: Load Balancer (SSL termination, health check)
    ├─ Layer 3: API Gateway (rate limit, JWT validation, CORS)
    ├─ Layer 4: Service Auth (mTLS between services, Phase 2)
    ├─ Layer 5: Database (RLS, encrypted at rest, connection auth)
    └─ Layer 6: Application (input validation, parameterized query)
```

### 10.2 Secrets Management

```
Development  → .env.local (gitignored)
Staging      → Doppler (synced to environment)
Production   → Doppler / HashiCorp Vault (Phase 2)
              Never hardcode secrets in code or Docker image
```

---

## 11. Disaster Recovery & Business Continuity

| Aspek | SLA | Mekanisme |
|-------|-----|-----------|
| **RTO** (Recovery Time Objective) | < 1 jam | Automated failover + runbook |
| **RPO** (Recovery Point Objective) | < 15 menit | Continuous WAL streaming + 15-min snapshots |
| **Database Backup** | Daily full + continuous WAL | Automated ke R2/S3 |
| **Multi-region Failover** | Phase 2+ | DNS failover ke region backup |
| **Offline Mode** | 100% mobile functionality | Hive + SQLite local DB |

---

## 12. Scalability Design

### 12.1 Horizontal Scaling

Setiap microservice adalah **stateless** → bisa di-scale dengan menambah instance:

```
Kong Load Balancer
    ├──▶ POS Service Instance 1
    ├──▶ POS Service Instance 2
    └──▶ POS Service Instance 3
```

### 12.2 Rate Limiting per Plan

| Plan | API Rate Limit | POS Transaction/sec |
|------|---------------|---------------------|
| Free | 10 req/min | 1 TPS |
| Starter | 100 req/min | 10 TPS |
| Pro | 500 req/min | 50 TPS |
| Business | 2000 req/min | 200 TPS |
| Enterprise | Custom | Custom |

---

*Blueprint ini inline dengan: BP-05 (Tech Stack), BP-07 (Project Structure), BP-08 (DB Schema), BP-09 (Infrastructure), BP-10 (Security)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
