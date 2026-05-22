# XynPOS Architecture Reference

## High-Level System Diagram

```
Clients (Web Browser / Flutter iOS / Flutter Android)
    ↓
Cloudflare Edge (WAF + DDoS + CDN + SSL termination)
    ↓
DO Load Balancer
    ↓
Kong API Gateway (JWT validation · Rate limiting · Routing · CORS)
    ↓ (routes to microservices)
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│auth :8001│pos  :8005│prod :8003│inv  :8004│pay  :8006│
│tenant:8002│rpt :8008│cust :8007│notif:8009│file :8010│
│sub  :8011│audit:8012│          │          │          │
└────┬─────┴──────────┴──────────┴──────────┴──────────┘
     ↓ (async events)
   NATS message broker
     ↓ (subscribers)
Inventory · Notification · Report · Audit services
     ↓
PostgreSQL 16 (PgBouncer pool) + Redis 7 + Meilisearch
     ↓
Cloudflare R2 (object storage)
```

## Service Communication

**Synchronous** (REST/gRPC for real-time):
- Client → API Gateway → Service (REST)
- Service → Service (gRPC for internal calls)

**Asynchronous** (NATS events):
- `pos.transaction.completed` → Inventory, Notification, Report, Audit
- `pos.transaction.voided` → Inventory, Notification, Audit
- `inventory.stock.low` → Notification
- `payment.received` → POS, Notification, Subscription
- `subscription.plan.changed` → Auth (update JWT claims cache)

CloudEvents schema for all events:
```json
{
  "specversion": "1.0",
  "type": "pos.transaction.completed",
  "source": "/services/pos",
  "id": "evt_uuid",
  "tenantid": "tenant_uuid",
  "data": { ... }
}
```

## Authentication Flow

```
1. Client POST /v1/auth/login
2. Auth Service validates credentials, generates JWT pair
3. Access token (15min, RS256) returned to client
4. Kong validates JWT locally on every request (no roundtrip)
5. Refresh token (30 days) stored hashed in Redis
6. Token rotation: each refresh revokes old token
7. Reuse detection: family-based — if old token reused, revoke entire family
```

## Transaction Flow (POS)

```
1. POST /v1/pos/transactions (JWT + cart)
2. POS Service → validate products (gRPC Product)
3. POS Service → check/reserve stock (gRPC Inventory)
4. POS Service → create payment request if non-cash
5. POS Service → save to PostgreSQL
6. POS Service → publish pos.transaction.created → NATS
7. [async] Inventory deducts stock permanently
8. [async] Notification sends receipt
9. [async] Report updates real-time dashboard
10. Return transaction_id to client
```

## Offline Transaction Flow (Mobile)

```
1. Connectivity check → OFFLINE detected
2. Save to Hive local DB with local_id (UUID)
3. Update local stock (optimistic)
4. Print via Bluetooth printer
-- [internet restored] --
5. WorkManager triggers sync job
6. POST /v1/transactions/sync (batch with local_ids)
7. Server deduplicates by local_id (idempotency)
8. Server processes normally
9. Mark local transactions as synced
```

## Database Architecture

```
PostgreSQL Cluster (DO Managed)
    ↓ PgBouncer (connection pool, port 6432)
    ├── Primary (read/write) ← all writes
    └── Read Replica ← report-service, heavy analytics

Redis 7:
  session:{user}:{device}        JWT refresh token
  blacklist:{jti}                Revoked tokens (TTL = expiry)
  ratelimit:{tenant}:{endpoint}  Rate limit counter (TTL 60s)
  cache:tenant:{id}:plan         Subscription plan (TTL 5min)
  pubsub:kds:{outlet}            Kitchen display orders
```

## Infrastructure Phases

| Phase | Cloud | Tenants | Monthly Cost |
|-------|-------|---------|-------------|
| 1 | DigitalOcean (SGP) | 0–500 | ~$176 |
| 2 | DOKS (K8s on DO) | 500–10K | ~$600 |
| 3 | AWS (ap-southeast-1) | 10K+ | Custom |

## Security Layers (Defense in Depth)

```
L1: Cloudflare (WAF, DDoS, Bot protection)
L2: Load Balancer (SSL termination, health check)
L3: Kong (rate limit, JWT validation, CORS)
L4: mTLS (Phase 2: service-to-service auth)
L5: PostgreSQL RLS + encrypted at-rest
L6: Application (input validation, parameterized SQL)
```
