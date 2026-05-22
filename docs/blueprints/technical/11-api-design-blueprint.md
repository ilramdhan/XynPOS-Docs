# XynPOS — Blueprint 11: API Design Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. API Design Principles

- **RESTful** — Resource-based URL, HTTP verbs semantik
- **Versioned** — `/api/v1/...` dari awal, mudah migrate ke v2
- **Consistent** — Semua response menggunakan format yang sama
- **Descriptive errors** — Error message informatif (bukan "error 500")
- **Pagination default** — Semua list endpoint paginasi secara default
- **Idempotent** — POST create pakai idempotency key untuk retry aman

---

## 2. Base URL & Versioning

```
Production:   https://api.xynpos.com/v1
Staging:      https://api-staging.xynpos.com/v1
Development:  http://localhost:8000/v1

Format URL:   /v1/{resource}/{id}/{sub-resource}
```

---

## 3. Authentication

### 3.1 Request Headers

```http
Authorization: Bearer <access_token>
X-Tenant-ID: <tenant_id>           # Optional — bisa dari JWT
Content-Type: application/json
Accept: application/json
X-Idempotency-Key: <uuid>          # Untuk POST yang create resource
X-Device-ID: <device_id>           # Untuk offline sync
```

### 3.2 Token Refresh Flow

```http
POST /v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGci..."
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",  // Rotate — token lama invalid
    "expires_in": 900                 // 15 menit dalam detik
  }
}
```

---

## 4. Standard Response Format

### 4.1 Success Response

```json
// Single resource
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Kopi Susu",
    "price": 25000
  }
}

// List with pagination
{
  "success": true,
  "data": [
    { "id": "...", "name": "Kopi Susu" },
    { "id": "...", "name": "Es Teh" }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 145,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### 4.2 Error Response

```json
// Single error
{
  "success": false,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Produk tidak ditemukan",
    "http_status": 404
  }
}

// Validation errors (multiple fields)
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid",
    "http_status": 422,
    "details": [
      {
        "field": "selling_price",
        "message": "Harga jual harus lebih besar dari 0"
      },
      {
        "field": "name",
        "message": "Nama produk wajib diisi"
      }
    ]
  }
}
```

### 4.3 Standard Error Codes

| Code | HTTP | Deskripsi |
|------|------|-----------|
| `UNAUTHORIZED` | 401 | Token tidak valid atau expired |
| `FORBIDDEN` | 403 | Tidak punya permission |
| `NOT_FOUND` | 404 | Resource tidak ditemukan |
| `CONFLICT` | 409 | Resource sudah ada (duplicate) |
| `VALIDATION_ERROR` | 422 | Input tidak valid |
| `RATE_LIMITED` | 429 | Terlalu banyak request |
| `PLAN_LIMIT_REACHED` | 402 | Fitur butuh upgrade plan |
| `TENANT_SUSPENDED` | 403 | Tenant tidak aktif |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Dependency down |

---

## 5. API Endpoint Reference

### 5.1 Auth Endpoints

```
POST   /v1/auth/register              # Registrasi tenant baru
POST   /v1/auth/login                 # Login
POST   /v1/auth/logout                # Logout (revoke refresh token)
POST   /v1/auth/refresh               # Refresh access token
POST   /v1/auth/forgot-password       # Request reset password
POST   /v1/auth/reset-password        # Reset password dengan token
POST   /v1/auth/verify-email          # Verifikasi email dengan OTP
POST   /v1/auth/resend-otp            # Kirim ulang OTP
GET    /v1/auth/me                    # Get profil user yang login
PATCH  /v1/auth/me                    # Update profil
PATCH  /v1/auth/me/password           # Ganti password
GET    /v1/auth/sessions              # List aktif sessions
DELETE /v1/auth/sessions/:id          # Revoke session spesifik
```

### 5.2 Tenant & Outlet Endpoints

```
GET    /v1/tenant                     # Get info tenant
PATCH  /v1/tenant                     # Update info tenant
GET    /v1/tenant/subscription        # Status subscription
POST   /v1/tenant/subscription/upgrade # Upgrade plan

GET    /v1/outlets                    # List outlet
POST   /v1/outlets                    # Buat outlet baru
GET    /v1/outlets/:id                # Detail outlet
PATCH  /v1/outlets/:id                # Update outlet
DELETE /v1/outlets/:id                # Non-aktifkan outlet
```

### 5.3 Product Endpoints

```
GET    /v1/products                   # List produk (filter, search, paginate)
POST   /v1/products                   # Buat produk baru
GET    /v1/products/:id               # Detail produk
PATCH  /v1/products/:id               # Update produk
DELETE /v1/products/:id               # Soft delete produk

POST   /v1/products/bulk              # Bulk create via JSON array
POST   /v1/products/import            # Import via CSV/Excel upload

GET    /v1/products/:id/variants      # List variant produk
POST   /v1/products/:id/variants      # Tambah variant
PATCH  /v1/products/:id/variants/:vid # Update variant
DELETE /v1/products/:id/variants/:vid # Delete variant

GET    /v1/categories                 # List kategori (tree structure)
POST   /v1/categories                 # Buat kategori
PATCH  /v1/categories/:id             # Update kategori
DELETE /v1/categories/:id             # Delete kategori
POST   /v1/categories/reorder         # Reorder kategori

GET    /v1/modifiers                  # List modifier groups
POST   /v1/modifiers                  # Buat modifier group
PATCH  /v1/modifiers/:id              # Update modifier group
DELETE /v1/modifiers/:id              # Delete modifier group
```

**Query params untuk GET /v1/products:**
```
GET /v1/products?
  search=kopi          # Full-text search
  category_id=uuid     # Filter by kategori
  is_active=true       # Filter status
  track_inventory=true # Filter yang punya stok
  outlet_id=uuid       # Tampilkan dengan stok per outlet
  sort=name:asc        # Sorting
  page=1               # Pagination
  per_page=20
  low_stock=true       # Hanya produk stok hampir habis
```

### 5.4 Inventory Endpoints

```
GET    /v1/inventory                  # List stok semua produk (per outlet)
GET    /v1/inventory/:product_id      # Stok produk di semua outlet
POST   /v1/inventory/adjust           # Manual adjustment stok

GET    /v1/inventory/movements        # Riwayat pergerakan stok
GET    /v1/inventory/low-stock        # Produk dengan stok hampir habis

POST   /v1/inventory/transfer         # Transfer stok antar outlet
GET    /v1/inventory/transfers        # List transfer

# Stocktake (Wave 1)
POST   /v1/stocktake                  # Buat sesi stocktake
GET    /v1/stocktake/:id              # Detail sesi
PATCH  /v1/stocktake/:id/items        # Input hitungan fisik
POST   /v1/stocktake/:id/confirm      # Konfirmasi dan apply adjustment
```

### 5.5 POS / Transaction Endpoints

```
# Kasir session
POST   /v1/sessions/open              # Buka shift kasir
POST   /v1/sessions/:id/close         # Tutup shift kasir
GET    /v1/sessions/current           # Shift yang sedang aktif

# Transaksi
POST   /v1/transactions               # Buat transaksi (checkout)
GET    /v1/transactions               # List transaksi
GET    /v1/transactions/:id           # Detail transaksi
POST   /v1/transactions/:id/void      # Void transaksi
POST   /v1/transactions/:id/refund    # Refund transaksi
GET    /v1/transactions/:id/receipt   # Get data untuk cetak struk

# Batch sync (offline)
POST   /v1/transactions/sync          # Sync transaksi offline

# Hold orders
GET    /v1/orders/held                # List order yang di-hold
POST   /v1/orders/hold                # Hold order
GET    /v1/orders/held/:id            # Get held order
DELETE /v1/orders/held/:id            # Hapus held order
POST   /v1/orders/held/:id/resume     # Resume held order → cart

# Table management (F&B)
GET    /v1/tables                     # List meja dan status
POST   /v1/tables                     # Buat meja
PATCH  /v1/tables/:id                 # Update meja
POST   /v1/tables/:id/assign          # Assign transaksi ke meja
POST   /v1/tables/:id/transfer        # Pindah ke meja lain
POST   /v1/tables/:id/merge           # Gabung dua meja
```

**POST /v1/transactions — Request Body:**
```json
{
  "outlet_id": "uuid",
  "session_id": "uuid",
  "customer_id": "uuid",        // Optional
  "table_id": "uuid",           // Optional (F&B)
  "pax": 2,                     // Optional (F&B)
  "items": [
    {
      "product_id": "uuid",
      "variant_id": "uuid",     // Optional
      "quantity": 2,
      "unit_price": 25000,
      "discount_amount": 0,
      "notes": "Less sugar",    // Optional
      "modifiers": [
        {
          "modifier_id": "uuid",
          "price_adjustment": 5000
        }
      ]
    }
  ],
  "discount_amount": 5000,      // Total diskon
  "promo_code": "SAVE10",       // Optional
  "payments": [
    {
      "method": "cash",
      "amount": 50000
    },
    {
      "method": "qris",
      "amount": 5000
    }
  ],
  "notes": "Special request",
  
  // Untuk offline sync
  "local_id": "device_uuid_timestamp",
  "created_offline": true,
  "local_created_at": "2025-01-01T10:00:00+07:00"
}
```

### 5.6 Payment Endpoints

```
# QRIS
POST   /v1/payments/qris/create       # Generate QRIS dynamic
GET    /v1/payments/qris/:ref_id      # Cek status QRIS
POST   /v1/payments/qris/cancel/:ref  # Batalkan QRIS

# Virtual Account
POST   /v1/payments/va/create         # Generate VA
GET    /v1/payments/va/:va_number     # Cek status VA

# Webhook receivers (untuk gateway callback)
POST   /v1/webhooks/xendit            # Xendit webhook
POST   /v1/webhooks/midtrans          # Midtrans webhook
```

### 5.7 Customer Endpoints

```
GET    /v1/customers                  # List pelanggan
POST   /v1/customers                  # Buat pelanggan
GET    /v1/customers/:id              # Detail pelanggan
PATCH  /v1/customers/:id             # Update pelanggan
DELETE /v1/customers/:id              # Soft delete

GET    /v1/customers/:id/transactions # Riwayat transaksi
GET    /v1/customers/:id/points       # Saldo poin loyalitas
GET    /v1/customers/:id/debts        # Hutang outstanding

POST   /v1/customers/:id/debts/pay    # Bayar hutang
DELETE /v1/customers/:id/erase        # Hapus data PII (UU PDP)
```

### 5.8 Report Endpoints

```
# Dashboard
GET    /v1/reports/dashboard          # Summary hari ini

# Sales reports
GET    /v1/reports/sales              # Laporan penjualan
GET    /v1/reports/sales/by-product   # Per produk
GET    /v1/reports/sales/by-category  # Per kategori
GET    /v1/reports/sales/by-cashier   # Per kasir
GET    /v1/reports/sales/by-payment   # Per metode pembayaran
GET    /v1/reports/sales/by-hour      # Per jam (heat map)

# Inventory reports
GET    /v1/reports/inventory          # Stok saat ini
GET    /v1/reports/inventory/movements # Pergerakan stok

# Financial reports
GET    /v1/reports/profit-loss        # Laba rugi sederhana
GET    /v1/reports/customer-debt      # Hutang pelanggan

# Export
POST   /v1/reports/export/sales       # Export ke PDF/Excel
POST   /v1/reports/export/inventory   # Export stok
```

**Query params untuk semua report:**
```
GET /v1/reports/sales?
  outlet_id=uuid              # Filter outlet (atau "all")
  date_from=2025-01-01        # Tanggal mulai (ISO date)
  date_to=2025-01-31          # Tanggal akhir
  group_by=day|week|month     # Granularity
  format=json|pdf|excel       # Export format
```

### 5.9 User Management Endpoints

```
GET    /v1/users                      # List user dalam tenant
POST   /v1/users/invite               # Undang user baru
GET    /v1/users/:id                  # Detail user
PATCH  /v1/users/:id/role             # Ganti role user
PATCH  /v1/users/:id/outlets          # Update outlet access
DELETE /v1/users/:id                  # Remove dari tenant
POST   /v1/users/:id/suspend          # Suspend user

GET    /v1/roles                      # List roles
POST   /v1/roles                      # Buat custom role
PATCH  /v1/roles/:id                  # Update role
DELETE /v1/roles/:id                  # Delete custom role

GET    /v1/audit-logs                 # Riwayat audit log
```

### 5.10 Settings Endpoints

```
GET    /v1/settings/business          # Pengaturan bisnis
PATCH  /v1/settings/business          # Update pengaturan
GET    /v1/settings/receipt           # Template struk
PATCH  /v1/settings/receipt           # Update template struk
GET    /v1/settings/tax               # Pengaturan pajak
PATCH  /v1/settings/tax               # Update pajak
GET    /v1/settings/notifications     # Preferensi notifikasi
PATCH  /v1/settings/notifications     # Update preferensi
```

---

## 6. Pagination

### 6.1 Offset Pagination (default untuk report)

```
GET /v1/transactions?page=2&per_page=20

Response:
{
  "data": [...],
  "meta": {
    "page": 2,
    "per_page": 20,
    "total": 485,
    "total_pages": 25,
    "has_next": true,
    "has_prev": true
  }
}
```

### 6.2 Cursor Pagination (untuk real-time feeds)

```
GET /v1/transactions?cursor=txn_abc123&limit=20&direction=before

Response:
{
  "data": [...],
  "meta": {
    "cursor_next": "txn_xyz789",
    "cursor_prev": "txn_abc001",
    "has_next": true,
    "has_prev": false,
    "limit": 20
  }
}
```

---

## 7. Idempotency

Semua POST yang create resource mendukung idempotency key:

```http
POST /v1/transactions
X-Idempotency-Key: a7f8c921-4d2e-4b8f-9a1c-7e3d5f2a1b4c

# Jika key sudah dipakai dalam 24 jam:
# → Return response yang sama persis (cached)
# → Tidak membuat transaksi duplikat
```

---

## 8. Webhooks (untuk Developer/Enterprise)

### 8.1 Webhook Config

```
POST /v1/webhooks                     # Register webhook URL
GET  /v1/webhooks                     # List webhooks
PATCH /v1/webhooks/:id                # Update webhook
DELETE /v1/webhooks/:id               # Delete webhook
POST /v1/webhooks/:id/test            # Test webhook
GET  /v1/webhooks/:id/deliveries      # Riwayat delivery
POST /v1/webhooks/:id/deliveries/:did/retry # Retry delivery
```

### 8.2 Webhook Events

```json
// POST ke webhook URL Anda
{
  "id": "evt_xynpos_abc123",
  "type": "transaction.completed",
  "tenant_id": "tenant_uuid",
  "created_at": "2025-01-01T10:00:00+07:00",
  "data": {
    "transaction_id": "txn_uuid",
    "outlet_id": "outlet_uuid",
    "total_amount": 75000,
    "payment_method": "qris",
    "items_count": 3
  }
}

// Signature header untuk validasi:
X-XynPOS-Signature: sha256=<hmac_signature>
X-XynPOS-Timestamp: 1735689600
```

### 8.3 Available Webhook Events

```
transaction.completed      # Transaksi selesai
transaction.voided         # Transaksi di-void
transaction.refunded       # Transaksi di-refund
payment.received           # Pembayaran diterima
inventory.low_stock        # Stok mendekati minimum
inventory.out_of_stock     # Stok habis
customer.created           # Pelanggan baru dibuat
subscription.renewed       # Subscription berhasil diperbarui
subscription.payment_failed # Pembayaran subscription gagal
subscription.cancelled     # Subscription dibatalkan
```

---

## 9. Real-time (WebSocket)

Untuk fitur yang butuh update real-time:

```javascript
// Connect ke WebSocket
const ws = new WebSocket('wss://api.xynpos.com/v1/ws?token=<access_token>');

// Subscribe ke channel
ws.send(JSON.stringify({
  action: "subscribe",
  channels: [
    "kds:outlet_uuid",           // Kitchen Display updates
    "tables:outlet_uuid",        // Table status updates
    "payment:transaction_uuid"   // Payment status real-time
  ]
}));

// Receive events
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { type: "kds.order_ready", data: {...} }
};
```

---

## 10. API Versioning Strategy

| Versi | Status | Catatan |
|-------|--------|---------|
| v1 | 🟢 Current | Semua endpoint aktif |
| v2 | 🟡 Planned | Breaking changes jika ada |

**Breaking changes** (akan bumping ke v2):
- Menghapus field dari response
- Mengubah tipe data field
- Mengubah method atau URL endpoint
- Mengubah authentication mechanism

**Non-breaking** (tetap v1):
- Menambah field baru ke response
- Menambah endpoint baru
- Menambah optional parameter

**Deprecation policy:**
- Announce deprecation 6 bulan sebelumnya
- Maintenance mode (no new features) 3 bulan
- Shutdown dengan redirect ke v2

---

## 11. API Documentation

- **Swagger UI:** `https://api.xynpos.com/docs`
- **OpenAPI Spec:** `https://api.xynpos.com/openapi.json`
- **Postman Collection:** Link di developer portal
- **Sandbox Environment:** `https://api-sandbox.xynpos.com/v1`

---

*Blueprint ini inline dengan: BP-06 (Architecture), BP-10 (Security), BP-07 (Project Structure)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
