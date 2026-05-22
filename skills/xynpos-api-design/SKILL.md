---
name: xynpos-api-design
description: XynPOS API design and documentation — use when designing new REST endpoints, reviewing existing API design, writing Swagger/OpenAPI annotations, planning webhook events, or ensuring API consistency with XynPOS standards. Triggers when someone needs to add a new endpoint, design a resource URL structure, determine correct HTTP method or status code, document an API with Swagger, or review an API for RESTful compliance. Also triggers for questions about API versioning, idempotency, pagination strategy, or rate limiting design.
license: See LICENSE.txt
---

# XynPOS API Design

All XynPOS APIs follow strict conventions for consistency across 12+ microservices.

## Reference Files
- All endpoint catalog → `references/endpoint-catalog.md`
- Swagger annotation patterns → `references/swagger-patterns.md`
- Webhook events reference → `references/webhooks.md`

## URL Convention

```
Base: /api/v1/{resource}

GET    /v1/products              → List (filter + paginate)
POST   /v1/products              → Create (X-Idempotency-Key required)
GET    /v1/products/:id          → Single resource
PATCH  /v1/products/:id          → Partial update (NEVER PUT)
DELETE /v1/products/:id          → Soft delete

GET    /v1/products/:id/variants → Sub-resource
POST   /v1/products/:id/variants → Sub-resource create

Special actions: POST /v1/transactions/:id/void  (verb on specific resource)
Batch sync:      POST /v1/transactions/sync
Export:          POST /v1/reports/export/sales   → returns download link
```

## Response Format (strict)

```json
// Success — single
{ "success": true, "data": { "id": "uuid", "name": "..." } }

// Success — list  
{ "success": true, "data": [...], "meta": { "page":1,"per_page":20,"total":145,"total_pages":8 } }

// Error
{ "success": false, "error": { "code": "PRODUCT_NOT_FOUND", "message": "Produk tidak ditemukan", "http_status": 404 } }

// Validation error
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "Input tidak valid", "http_status": 422,
  "details": [{ "field": "selling_price", "message": "Harga harus lebih besar dari 0" }] } }
```

## Standard Error Codes

```
UNAUTHORIZED 401 · FORBIDDEN 403 · NOT_FOUND 404 · CONFLICT 409
VALIDATION_ERROR 422 · RATE_LIMITED 429 · PLAN_LIMIT_REACHED 402
INSUFFICIENT_STOCK 422 · TRANSACTION_ALREADY_VOIDED 409
CASHIER_SESSION_NOT_OPEN 422 · INTERNAL_ERROR 500
```

## Swagger Annotation (required for every handler)

```go
// @Summary      Create new product
// @Description  Creates a product in the tenant's catalog.
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        X-Idempotency-Key  header  string  true  "Idempotency key (UUID v4)"
// @Param        request  body  CreateProductRequest  true  "Product data"
// @Success      201  {object}  response.Success{data=ProductResponse}
// @Failure      422  {object}  response.ValidationError
// @Failure      409  {object}  response.Error  "SKU already exists"
// @Security     BearerAuth
// @Router       /v1/products [post]
```

## Design Checklist (new endpoint)

```
[ ] URL follows /{resource}/{id}/{sub-resource} pattern
[ ] HTTP method is semantically correct
[ ] POST that creates → has X-Idempotency-Key requirement
[ ] Response uses standard format
[ ] Error codes defined and added to errors package
[ ] Pagination on list endpoints
[ ] Filter query params documented
[ ] Plan-gate check if feature is plan-limited
[ ] Swagger annotation complete
[ ] Rate limit configured in Kong or middleware
[ ] Breaking change? → consider API version bump
```

## Scripts

`scripts/check_api_consistency.py <service-path>` — validates handlers for standard response usage and Swagger annotations.
