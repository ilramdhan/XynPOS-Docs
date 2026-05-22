---
skill_id: SKILL-06
name: XynPOS API Design
category: shared
description: Skill untuk mendesign endpoint baru, review API, dan menulis Swagger docs
version: 1.0.0
applies_to: [api, rest, swagger, webhook]
depends_on: [SKILL-00]
---

# SKILL-06: API Design

## Conventions

```
Base URL:   /api/v1/{resource}
Auth:       Authorization: Bearer {access_token}
Content:    Content-Type: application/json
Idempotent: X-Idempotency-Key: {uuid4}  ← WAJIB untuk semua POST yang create
```

## URL Structure

```
GET    /v1/products              ← List (dengan filter, sort, paginate)
POST   /v1/products              ← Create
GET    /v1/products/:id          ← Detail
PATCH  /v1/products/:id          ← Partial update (bukan PUT)
DELETE /v1/products/:id          ← Delete (soft)

GET    /v1/products/:id/variants ← Sub-resource
POST   /v1/products/:id/variants
```

## Response Format (WAJIB KONSISTEN)

```json
// ✅ Success - single
{ "success": true, "data": { "id": "uuid", "name": "Kopi" } }

// ✅ Success - list
{
  "success": true,
  "data": [{ "id": "uuid" }],
  "meta": { "page": 1, "per_page": 20, "total": 145, "total_pages": 8 }
}

// ✅ Error
{ "success": false, "error": { "code": "PRODUCT_NOT_FOUND", "message": "Produk tidak ditemukan", "http_status": 404 } }

// ✅ Validation error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid",
    "http_status": 422,
    "details": [
      { "field": "selling_price", "message": "Harga harus lebih besar dari 0" },
      { "field": "name", "message": "Nama wajib diisi" }
    ]
  }
}
```

## Standard Error Codes

```
UNAUTHORIZED        401 ← Token tidak valid/expired
FORBIDDEN           403 ← Tidak punya permission
NOT_FOUND           404 ← Resource tidak ditemukan
CONFLICT            409 ← Duplicate resource
VALIDATION_ERROR    422 ← Input tidak valid
RATE_LIMITED        429 ← Terlalu banyak request
PLAN_LIMIT_REACHED  402 ← Butuh upgrade plan
TENANT_SUSPENDED    403 ← Tenant tidak aktif
INTERNAL_ERROR      500 ← Server error
SERVICE_UNAVAILABLE 503 ← Dependency down

Domain-specific:
INSUFFICIENT_STOCK        422
INVALID_PAYMENT_AMOUNT    422
TRANSACTION_ALREADY_VOIDED 409
CASHIER_SESSION_NOT_OPEN  422
```

## Pagination

```
Offset (default untuk report/list):
  GET /v1/transactions?page=2&per_page=20

Cursor (untuk real-time feed):
  GET /v1/transactions?cursor=txn_abc123&limit=20
  Response meta: { "cursor_next": "txn_xyz", "cursor_prev": "txn_abc", "has_next": true }
```

## Common Query Parameters

```
GET /v1/products?
  search=kopi            ← full-text search
  category_id=uuid       ← filter
  is_active=true         ← filter
  outlet_id=uuid         ← scope
  sort=name:asc          ← sorting (field:direction)
  page=1                 ← pagination
  per_page=20
  date_from=2025-01-01   ← date range (ISO date)
  date_to=2025-01-31
```

## All Endpoints Reference

```
AUTH:
POST /v1/auth/register, /login, /logout, /refresh
POST /v1/auth/forgot-password, /reset-password
POST /v1/auth/verify-email, /resend-otp
GET  /v1/auth/me         PATCH /v1/auth/me, /me/password

TENANT & OUTLETS:
GET|PATCH /v1/tenant
GET|POST  /v1/outlets    GET|PATCH|DELETE /v1/outlets/:id

PRODUCTS:
GET|POST     /v1/products
GET|PATCH|DELETE /v1/products/:id
POST         /v1/products/bulk, /products/import
GET|POST     /v1/products/:id/variants
PATCH|DELETE /v1/products/:id/variants/:vid
GET|POST     /v1/categories    PATCH|DELETE /v1/categories/:id
GET|POST     /v1/modifiers     PATCH|DELETE /v1/modifiers/:id

INVENTORY:
GET  /v1/inventory, /inventory/:product_id
POST /v1/inventory/adjust, /inventory/transfer
GET  /v1/inventory/movements, /inventory/low-stock
POST /v1/stocktake    GET /v1/stocktake/:id
PATCH /v1/stocktake/:id/items    POST /v1/stocktake/:id/confirm

POS:
POST /v1/sessions/open    POST /v1/sessions/:id/close
GET  /v1/sessions/current
POST /v1/transactions     GET /v1/transactions
GET  /v1/transactions/:id
POST /v1/transactions/:id/void, /:id/refund
GET  /v1/transactions/:id/receipt
POST /v1/transactions/sync          ← offline batch sync
GET  /v1/orders/held    POST /v1/orders/hold
GET  /v1/tables    PATCH /v1/tables/:id
POST /v1/tables/:id/assign, /:id/transfer

PAYMENT:
POST /v1/payments/qris/create    GET /v1/payments/qris/:ref_id
POST /v1/webhooks/xendit, /webhooks/midtrans

CUSTOMERS:
GET|POST     /v1/customers
GET|PATCH|DELETE /v1/customers/:id
GET /v1/customers/:id/transactions, /:id/points, /:id/debts
POST /v1/customers/:id/debts/pay
DELETE /v1/customers/:id/erase     ← UU PDP right to erasure

REPORTS:
GET /v1/reports/dashboard
GET /v1/reports/sales, /sales/by-product, /sales/by-category
GET /v1/reports/inventory, /reports/profit-loss
POST /v1/reports/export/sales, /export/inventory

USERS & SETTINGS:
GET|POST /v1/users    POST /v1/users/invite
PATCH /v1/users/:id/role    DELETE /v1/users/:id
GET|POST|PATCH|DELETE /v1/roles
GET /v1/audit-logs
GET|PATCH /v1/settings/business, /settings/receipt, /settings/tax

WEBHOOKS (Developer API):
GET|POST /v1/webhooks    PATCH|DELETE /v1/webhooks/:id
POST /v1/webhooks/:id/test
GET /v1/webhooks/:id/deliveries
POST /v1/webhooks/:id/deliveries/:did/retry
```

## Webhook Events

```json
{
  "id": "evt_xynpos_abc123",
  "type": "transaction.completed",
  "tenant_id": "uuid",
  "created_at": "2025-01-01T10:00:00+07:00",
  "data": { ... }
}

// Available events:
// transaction.completed, transaction.voided, transaction.refunded
// payment.received, inventory.low_stock, inventory.out_of_stock
// customer.created, subscription.renewed, subscription.payment_failed
// subscription.cancelled
```

## Idempotency

```go
// POST /v1/transactions dengan X-Idempotency-Key:
// - Jika key baru → proses normal
// - Jika key sudah dipakai (dalam 24 jam) → return cached response
// - Tidak membuat duplikat transaksi

// Implementation: Redis dengan key = "idempotency:{tenant_id}:{key}"
// TTL = 24 jam
```

## Versioning Strategy

```
v1 → Current (semua endpoint aktif)
v2 → Planned untuk breaking changes

Breaking changes (butuh v2):
  - Hapus field dari response
  - Ubah tipe data field
  - Ubah URL atau HTTP method
  
Non-breaking (tetap v1):
  - Tambah field baru ke response
  - Tambah endpoint baru
  - Tambah optional parameter

Deprecation: announce 6 bulan sebelum, maintenance 3 bulan, kemudian shutdown
```

## Checklist API Design

```
[ ] URL mengikuti RESTful convention
[ ] HTTP method semantik (GET=read, POST=create, PATCH=update, DELETE=delete)
[ ] Response pakai standard format
[ ] X-Idempotency-Key untuk POST
[ ] Error codes sudah didefinisikan
[ ] Pagination untuk list endpoints
[ ] Query params untuk filter/sort
[ ] Swagger doc di-update
[ ] Rate limit plan sudah ditentukan
[ ] Breaking change? → pertimbangkan v2
```
