# XynPOS API Standards

## Base URL & Versioning

```
Production:   https://api.xynpos.com/v1
Staging:      https://api-staging.xynpos.com/v1
Local:        http://localhost:8000/v1
```

## Required Headers

```http
Authorization: Bearer {access_token}
Content-Type: application/json
X-Idempotency-Key: {uuid4}   ← REQUIRED for all POST that create resources
X-Device-ID: {device_id}     ← for offline sync endpoints
```

## Response Format (strict — never deviate)

```json
// Single resource success
{ "success": true, "data": { "id": "uuid", ... } }

// List success
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "page": 1, "per_page": 20, "total": 145,
    "total_pages": 8, "has_next": true, "has_prev": false
  }
}

// Error
{
  "success": false,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Produk tidak ditemukan",
    "http_status": 404
  }
}

// Validation error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid",
    "http_status": 422,
    "details": [
      { "field": "selling_price", "message": "Harga harus lebih besar dari 0" }
    ]
  }
}
```

## Standard Error Codes

```
UNAUTHORIZED          401  Token invalid/expired
FORBIDDEN             403  No permission
NOT_FOUND             404  Resource not found
CONFLICT              409  Duplicate resource
VALIDATION_ERROR      422  Input invalid
RATE_LIMITED          429  Too many requests
PLAN_LIMIT_REACHED    402  Feature needs plan upgrade
TENANT_SUSPENDED      403  Tenant inactive
INTERNAL_ERROR        500  Server error
SERVICE_UNAVAILABLE   503  Dependency down

Domain-specific:
INSUFFICIENT_STOCK           422
INVALID_PAYMENT_AMOUNT       422
TRANSACTION_ALREADY_VOIDED   409
CASHIER_SESSION_NOT_OPEN     422
PRODUCT_BARCODE_EXISTS       409
```

## URL Conventions

```
GET    /v1/products              List with filter/sort/paginate
POST   /v1/products              Create (requires X-Idempotency-Key)
GET    /v1/products/:id          Single resource
PATCH  /v1/products/:id          Partial update (never PUT)
DELETE /v1/products/:id          Soft delete

GET    /v1/products/:id/variants Sub-resource list
POST   /v1/products/:id/variants Sub-resource create
```

## Pagination

```
Offset (reports/lists): ?page=1&per_page=20
Cursor (feeds):         ?cursor=txn_abc&limit=20
```

## Query Parameters

```
?search=kopi          full-text search
?category_id=uuid     filter by FK
?is_active=true       boolean filter
?outlet_id=uuid       scope to outlet
?sort=name:asc        sort field:direction
?date_from=2025-01-01 date range (ISO)
?date_to=2025-01-31
?page=1&per_page=20   pagination
```

## Idempotency

```
X-Idempotency-Key: {uuid4}
- Same key within 24h → return cached response (no duplicate created)
- Redis key: "idempotency:{tenant_id}:{key}" TTL=24h
- Required for: POST /transactions, POST /payments/*, POST /customers
```

## Rate Limits (by plan)

| Plan | Global req/min | POS tx/min |
|------|---------------|------------|
| Free | 60 | 60 |
| Starter | 100 | 300 |
| Pro | 500 | 1500 |
| Business | 2000 | 6000 |
| Enterprise | Custom | Custom |

Auth endpoints: 5 login attempts / 15min → block 1h

## Webhook Events

```json
POST {webhook_url}
Headers: X-XynPOS-Signature: sha256={hmac}
         X-XynPOS-Timestamp: {unix_ts}

{
  "id": "evt_xynpos_uuid",
  "type": "transaction.completed",
  "tenant_id": "uuid",
  "created_at": "2025-01-01T10:00:00+07:00",
  "data": { ... }
}

Available events:
  transaction.completed, transaction.voided, transaction.refunded
  payment.received, inventory.low_stock, inventory.out_of_stock
  customer.created, subscription.renewed, subscription.payment_failed
  subscription.cancelled
```
