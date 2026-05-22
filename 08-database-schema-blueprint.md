# XynPOS — Blueprint 08: Database Schema Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Database Design Principles

- **UUID v4** untuk semua primary key (portable, tidak guessable)
- **Soft delete** dengan `deleted_at` timestamp (data tidak benar-benar dihapus)
- **Audit fields** di semua tabel: `created_at`, `updated_at`, `created_by`, `updated_by`
- **Schema per tenant** (Phase 1) — diawali dengan prefix `tenant_`
- **Naming**: snake_case untuk semua nama tabel dan kolom
- **Indexes** wajib di semua foreign key dan kolom yang sering di-query

---

## 2. Global Schema (public_xyn)

Schema ini berisi data level platform (cross-tenant).

### 2.1 Tabel `tenants`

```sql
CREATE TABLE public_xyn.tenants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(100) UNIQUE NOT NULL,          -- xynpos.com/tenant/[slug]
    name            VARCHAR(255) NOT NULL,
    schema_name     VARCHAR(100) UNIQUE NOT NULL,           -- tenant_abc123
    owner_user_id   UUID NOT NULL,
    
    -- Business info
    business_type   VARCHAR(50),                           -- retail, fnb, pharmacy, etc
    logo_url        TEXT,
    phone           VARCHAR(20),
    email           VARCHAR(255),
    address         TEXT,
    city            VARCHAR(100),
    country         VARCHAR(10) DEFAULT 'ID',
    timezone        VARCHAR(50) DEFAULT 'Asia/Jakarta',
    currency        VARCHAR(10) DEFAULT 'IDR',
    npwp            VARCHAR(30),
    
    -- Status
    status          VARCHAR(20) DEFAULT 'active',          -- active, suspended, deleted
    is_verified     BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_tenants_slug ON public_xyn.tenants(slug);
CREATE INDEX idx_tenants_owner ON public_xyn.tenants(owner_user_id);
```

### 2.2 Tabel `users` (Global Auth)

```sql
CREATE TABLE public_xyn.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    phone           VARCHAR(20),
    password_hash   TEXT,                                  -- NULL jika OAuth only
    name            VARCHAR(255) NOT NULL,
    avatar_url      TEXT,
    
    -- OAuth
    google_id       VARCHAR(255) UNIQUE,
    
    -- Status
    is_active       BOOLEAN DEFAULT TRUE,
    email_verified  BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMPTZ,
    last_login_at   TIMESTAMPTZ,
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON public_xyn.users(email);
```

### 2.3 Tabel `subscriptions`

```sql
CREATE TABLE public_xyn.subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES public_xyn.tenants(id),
    
    plan            VARCHAR(50) NOT NULL,                  -- free, starter, pro, business, enterprise
    status          VARCHAR(20) NOT NULL,                  -- active, trial, past_due, cancelled
    
    -- Trial
    trial_started_at TIMESTAMPTZ,
    trial_ends_at   TIMESTAMPTZ,
    is_trial        BOOLEAN DEFAULT FALSE,
    
    -- Billing
    billing_cycle   VARCHAR(20) DEFAULT 'monthly',        -- monthly, yearly
    amount          DECIMAL(15,2),
    currency        VARCHAR(10) DEFAULT 'IDR',
    
    -- Period
    current_period_start TIMESTAMPTZ,
    current_period_end   TIMESTAMPTZ,
    
    -- Payment
    payment_gateway VARCHAR(50),                          -- xendit, midtrans, stripe
    gateway_subscription_id VARCHAR(255),
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    cancelled_at    TIMESTAMPTZ
);

CREATE INDEX idx_subs_tenant ON public_xyn.subscriptions(tenant_id);
CREATE INDEX idx_subs_status ON public_xyn.subscriptions(status);
```

### 2.4 Tabel `invoices`

```sql
CREATE TABLE public_xyn.invoices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES public_xyn.tenants(id),
    subscription_id UUID REFERENCES public_xyn.subscriptions(id),
    
    invoice_number  VARCHAR(50) UNIQUE NOT NULL,           -- INV-2025-0001
    status          VARCHAR(20) NOT NULL,                  -- pending, paid, failed, cancelled
    
    amount          DECIMAL(15,2) NOT NULL,
    tax_amount      DECIMAL(15,2) DEFAULT 0,
    total_amount    DECIMAL(15,2) NOT NULL,
    currency        VARCHAR(10) DEFAULT 'IDR',
    
    due_date        DATE,
    paid_at         TIMESTAMPTZ,
    payment_gateway VARCHAR(50),
    gateway_payment_id VARCHAR(255),
    
    pdf_url         TEXT,
    
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 3. Auth Schema (auth_svc)

```sql
-- Refresh tokens untuk JWT rotation
CREATE TABLE auth_svc.refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    tenant_id       UUID NOT NULL,
    token_hash      VARCHAR(255) UNIQUE NOT NULL,          -- bcrypt hash of token
    token_family    UUID NOT NULL,                         -- Detect token reuse
    device_id       VARCHAR(255),
    device_name     VARCHAR(255),
    ip_address      INET,
    is_revoked      BOOLEAN DEFAULT FALSE,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- OTP untuk email verification & password reset
CREATE TABLE auth_svc.otps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    type            VARCHAR(50) NOT NULL,                  -- email_verify, password_reset
    code            VARCHAR(10) NOT NULL,                  -- 6-digit OTP
    is_used         BOOLEAN DEFAULT FALSE,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. Tenant Schema (per tenant)

Setiap tenant memiliki salinan schema berikut dalam namespace mereka sendiri.

### 4.1 Outlets & Users

```sql
-- Outlet / Lokasi bisnis
CREATE TABLE outlets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(50) UNIQUE,                    -- Kode outlet: JKT-01
    address         TEXT,
    phone           VARCHAR(20),
    city            VARCHAR(100),
    
    -- Settings
    is_active       BOOLEAN DEFAULT TRUE,
    opening_time    TIME,
    closing_time    TIME,
    timezone        VARCHAR(50) DEFAULT 'Asia/Jakarta',
    
    -- POS Settings
    receipt_header  TEXT,
    receipt_footer  TEXT,
    print_copies    SMALLINT DEFAULT 1,
    
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- User membership dalam tenant (bisa 1 user di multiple tenant)
CREATE TABLE tenant_users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,                         -- References public_xyn.users
    role_id         UUID NOT NULL REFERENCES roles(id),
    
    -- Outlet scope
    all_outlets     BOOLEAN DEFAULT FALSE,                 -- Access ke semua outlet
    
    -- Status
    status          VARCHAR(20) DEFAULT 'active',          -- active, invited, suspended
    invited_at      TIMESTAMPTZ,
    joined_at       TIMESTAMPTZ,
    
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    
    UNIQUE(user_id)                                        -- 1 user per tenant
);

-- Outlet access per user
CREATE TABLE tenant_user_outlets (
    tenant_user_id  UUID NOT NULL REFERENCES tenant_users(id),
    outlet_id       UUID NOT NULL REFERENCES outlets(id),
    PRIMARY KEY (tenant_user_id, outlet_id)
);

-- Roles
CREATE TABLE roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,                 -- owner, manager, cashier, etc
    is_system       BOOLEAN DEFAULT FALSE,                 -- System roles tidak bisa dihapus
    permissions     JSONB NOT NULL DEFAULT '[]',           -- ["pos:create", "report:read"]
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Kasir PIN (terpisah dari password akun)
CREATE TABLE cashier_pins (
    tenant_user_id  UUID PRIMARY KEY REFERENCES tenant_users(id),
    pin_hash        TEXT NOT NULL,                         -- bcrypt
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.2 Products & Inventory

```sql
-- Kategori produk
CREATE TABLE categories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id       UUID REFERENCES categories(id),        -- NULL = root category
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(255) UNIQUE,
    icon            VARCHAR(100),
    color           VARCHAR(7),                            -- #HEXCOLOR
    sort_order      INTEGER DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Unit satuan
CREATE TABLE units (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(50) NOT NULL,                  -- pcs, kg, liter, box
    abbreviation    VARCHAR(10)
);

-- Produk
CREATE TABLE products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id     UUID REFERENCES categories(id),
    unit_id         UUID REFERENCES units(id),
    
    -- Identity
    name            VARCHAR(255) NOT NULL,
    sku             VARCHAR(100) UNIQUE,                   -- Auto-generated atau manual
    barcode         VARCHAR(100),
    description     TEXT,
    image_url       TEXT,
    
    -- Pricing
    cost_price      DECIMAL(15,2) DEFAULT 0,              -- HPP / harga modal
    selling_price   DECIMAL(15,2) NOT NULL,
    tax_included    BOOLEAN DEFAULT TRUE,                  -- Harga sudah include PPN
    tax_rate        DECIMAL(5,2) DEFAULT 11.00,            -- % PPN
    
    -- Settings
    is_active       BOOLEAN DEFAULT TRUE,
    track_inventory BOOLEAN DEFAULT TRUE,
    allow_negative_stock BOOLEAN DEFAULT FALSE,
    min_stock       DECIMAL(15,3) DEFAULT 0,               -- Alert threshold
    
    -- Metadata
    created_by      UUID,
    updated_by      UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_category ON products(category_id);

-- Variant produk (contoh: ukuran, warna)
CREATE TABLE product_variants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,                 -- "Large / Hot"
    sku             VARCHAR(100) UNIQUE,
    barcode         VARCHAR(100),
    selling_price   DECIMAL(15,2),                        -- NULL = inherit dari produk
    cost_price      DECIMAL(15,2),
    image_url       TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    sort_order      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Modifier groups (F&B add-ons)
CREATE TABLE modifier_groups (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,                 -- "Pilih Ukuran", "Extra"
    is_required     BOOLEAN DEFAULT FALSE,
    min_selections  SMALLINT DEFAULT 0,
    max_selections  SMALLINT DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE modifiers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id        UUID NOT NULL REFERENCES modifier_groups(id),
    name            VARCHAR(255) NOT NULL,                 -- "Large", "Extra Shot"
    price_adjustment DECIMAL(15,2) DEFAULT 0,             -- Bisa negatif (diskon)
    is_active       BOOLEAN DEFAULT TRUE,
    sort_order      INTEGER DEFAULT 0
);

-- Relasi produk ↔ modifier group
CREATE TABLE product_modifier_groups (
    product_id      UUID NOT NULL REFERENCES products(id),
    modifier_group_id UUID NOT NULL REFERENCES modifier_groups(id),
    PRIMARY KEY (product_id, modifier_group_id)
);

-- Stok per outlet
CREATE TABLE inventory (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id       UUID NOT NULL REFERENCES outlets(id),
    product_id      UUID REFERENCES products(id),
    variant_id      UUID REFERENCES product_variants(id),
    
    quantity        DECIMAL(15,3) NOT NULL DEFAULT 0,
    reserved_qty    DECIMAL(15,3) DEFAULT 0,               -- Dipesan tapi belum bayar
    
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK (product_id IS NOT NULL OR variant_id IS NOT NULL),
    UNIQUE (outlet_id, product_id, variant_id)
);

-- Riwayat pergerakan stok
CREATE TABLE stock_movements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id       UUID NOT NULL REFERENCES outlets(id),
    product_id      UUID REFERENCES products(id),
    variant_id      UUID REFERENCES product_variants(id),
    
    type            VARCHAR(50) NOT NULL,                  -- sale, purchase, adjustment, transfer_in, transfer_out
    quantity        DECIMAL(15,3) NOT NULL,                -- Positif = masuk, negatif = keluar
    quantity_before DECIMAL(15,3) NOT NULL,
    quantity_after  DECIMAL(15,3) NOT NULL,
    
    reference_id    UUID,                                  -- transaction_id, po_id, etc
    reference_type  VARCHAR(50),                           -- transaction, purchase_order, adjustment
    notes           TEXT,
    
    created_by      UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stock_movements_product ON stock_movements(product_id, outlet_id);
CREATE INDEX idx_stock_movements_created ON stock_movements(created_at DESC);
```

### 4.3 Transactions (Core POS)

```sql
-- Sesi kasir (shift)
CREATE TABLE cashier_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id       UUID NOT NULL REFERENCES outlets(id),
    cashier_user_id UUID NOT NULL,
    
    opened_at       TIMESTAMPTZ DEFAULT NOW(),
    closed_at       TIMESTAMPTZ,
    
    opening_cash    DECIMAL(15,2) DEFAULT 0,
    closing_cash    DECIMAL(15,2),
    expected_cash   DECIMAL(15,2),
    cash_difference DECIMAL(15,2),
    
    notes           TEXT,
    status          VARCHAR(20) DEFAULT 'open'             -- open, closed
);

-- Transaksi utama
CREATE TABLE transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id       UUID NOT NULL REFERENCES outlets(id),
    session_id      UUID REFERENCES cashier_sessions(id),
    customer_id     UUID REFERENCES customers(id),
    cashier_user_id UUID NOT NULL,
    
    -- Order info
    transaction_number VARCHAR(50) UNIQUE NOT NULL,        -- TXN-20250101-001
    type            VARCHAR(30) DEFAULT 'sale',            -- sale, refund, void
    status          VARCHAR(30) DEFAULT 'completed',       -- pending, completed, voided, refunded
    
    -- Table (F&B)
    table_id        UUID REFERENCES tables(id),
    table_name      VARCHAR(50),
    pax             SMALLINT DEFAULT 1,                    -- Jumlah tamu
    
    -- Amounts
    subtotal        DECIMAL(15,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    tax_amount      DECIMAL(15,2) DEFAULT 0,
    service_charge  DECIMAL(15,2) DEFAULT 0,
    total_amount    DECIMAL(15,2) NOT NULL DEFAULT 0,
    
    -- Payment
    paid_amount     DECIMAL(15,2) DEFAULT 0,
    change_amount   DECIMAL(15,2) DEFAULT 0,
    payment_status  VARCHAR(30) DEFAULT 'unpaid',          -- unpaid, partial, paid
    
    -- Offline sync
    local_id        VARCHAR(100),                          -- Client-side ID (offline)
    synced_at       TIMESTAMPTZ,
    created_offline BOOLEAN DEFAULT FALSE,
    
    notes           TEXT,
    
    -- Void info
    voided_at       TIMESTAMPTZ,
    voided_by       UUID,
    void_reason     TEXT,
    
    created_by      UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_outlet_date ON transactions(outlet_id, created_at DESC);
CREATE INDEX idx_transactions_number ON transactions(transaction_number);
CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_local_id ON transactions(local_id) WHERE local_id IS NOT NULL;

-- Item dalam transaksi
CREATE TABLE transaction_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    product_id      UUID REFERENCES products(id),
    variant_id      UUID REFERENCES product_variants(id),
    
    product_name    VARCHAR(255) NOT NULL,                 -- Snapshot nama saat transaksi
    variant_name    VARCHAR(255),
    sku             VARCHAR(100),
    
    quantity        DECIMAL(15,3) NOT NULL,
    unit_price      DECIMAL(15,2) NOT NULL,
    cost_price      DECIMAL(15,2),                        -- Snapshot HPP
    discount_amount DECIMAL(15,2) DEFAULT 0,
    tax_amount      DECIMAL(15,2) DEFAULT 0,
    subtotal        DECIMAL(15,2) NOT NULL,
    
    notes           TEXT,
    sort_order      INTEGER DEFAULT 0,
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Modifier yang dipilih dalam item transaksi
CREATE TABLE transaction_item_modifiers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_item_id UUID NOT NULL REFERENCES transaction_items(id),
    modifier_id     UUID REFERENCES modifiers(id),
    modifier_name   VARCHAR(255) NOT NULL,                 -- Snapshot
    price_adjustment DECIMAL(15,2) DEFAULT 0
);

-- Pembayaran (bisa split payment)
CREATE TABLE transaction_payments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    
    method          VARCHAR(50) NOT NULL,                  -- cash, qris, transfer, ewallet, credit, debt
    amount          DECIMAL(15,2) NOT NULL,
    
    -- For non-cash payments
    payment_gateway VARCHAR(50),                          -- xendit, midtrans
    gateway_ref_id  VARCHAR(255),
    gateway_status  VARCHAR(50),
    
    -- For debt/credit
    is_debt         BOOLEAN DEFAULT FALSE,
    
    paid_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Diskon yang diaplikasikan
CREATE TABLE transaction_discounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(id),
    
    type            VARCHAR(50),                           -- manual, promo_code, loyalty_points
    promo_id        UUID REFERENCES promotions(id),
    
    name            VARCHAR(255),
    discount_amount DECIMAL(15,2) NOT NULL,
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.4 Customers & Loyalty

```sql
CREATE TABLE customers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    name            VARCHAR(255) NOT NULL,
    phone           VARCHAR(20),
    email           VARCHAR(255),
    date_of_birth   DATE,
    address         TEXT,
    gender          VARCHAR(10),
    
    -- Loyalty
    loyalty_points  INTEGER DEFAULT 0,
    total_spending  DECIMAL(15,2) DEFAULT 0,
    total_visits    INTEGER DEFAULT 0,
    
    -- Debt
    credit_limit    DECIMAL(15,2) DEFAULT 0,
    outstanding_debt DECIMAL(15,2) DEFAULT 0,
    
    notes           TEXT,
    tags            TEXT[],                               -- Array of tags: ['VIP', 'Grosir']
    
    created_by      UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_name ON customers(name);

-- Riwayat poin loyalitas
CREATE TABLE loyalty_point_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id     UUID NOT NULL REFERENCES customers(id),
    transaction_id  UUID REFERENCES transactions(id),
    
    type            VARCHAR(30) NOT NULL,                  -- earn, redeem, expire, adjustment
    points          INTEGER NOT NULL,                      -- Positif = earn, negatif = redeem
    points_balance  INTEGER NOT NULL,                      -- Balance setelah transaksi ini
    description     TEXT,
    
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Hutang pelanggan
CREATE TABLE customer_debts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id     UUID NOT NULL REFERENCES customers(id),
    transaction_id  UUID REFERENCES transactions(id),
    
    amount          DECIMAL(15,2) NOT NULL,
    paid_amount     DECIMAL(15,2) DEFAULT 0,
    remaining       DECIMAL(15,2) NOT NULL,
    
    status          VARCHAR(20) DEFAULT 'outstanding',     -- outstanding, partial, paid
    due_date        DATE,
    paid_at         TIMESTAMPTZ,
    
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.5 Tables Management (F&B)

```sql
CREATE TABLE table_areas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id       UUID NOT NULL REFERENCES outlets(id),
    name            VARCHAR(100) NOT NULL,                 -- "Indoor", "Outdoor", "VIP"
    sort_order      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tables (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id       UUID NOT NULL REFERENCES outlets(id),
    area_id         UUID REFERENCES table_areas(id),
    
    name            VARCHAR(50) NOT NULL,                  -- "Meja 1", "Table A"
    capacity        SMALLINT DEFAULT 4,
    
    -- Position for floor plan
    pos_x           DECIMAL(8,2),
    pos_y           DECIMAL(8,2),
    width           DECIMAL(8,2),
    height          DECIMAL(8,2),
    
    status          VARCHAR(20) DEFAULT 'available',       -- available, occupied, reserved, cleaning
    current_transaction_id UUID REFERENCES transactions(id),
    
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.6 Promotions

```sql
CREATE TABLE promotions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(50) UNIQUE,                    -- Kode promo (opsional)
    description     TEXT,
    
    type            VARCHAR(50) NOT NULL,                  -- percentage, fixed, buy_x_get_y, bundle
    discount_value  DECIMAL(15,2),                        -- Nilai diskon
    discount_percent DECIMAL(5,2),                        -- Persentase diskon
    
    -- Conditions
    min_purchase    DECIMAL(15,2),                        -- Minimum pembelian
    max_discount    DECIMAL(15,2),                        -- Maks diskon (untuk %)
    
    -- Validity
    starts_at       TIMESTAMPTZ,
    ends_at         TIMESTAMPTZ,
    
    -- Usage limit
    usage_limit     INTEGER,                              -- NULL = unlimited
    usage_count     INTEGER DEFAULT 0,
    per_customer_limit SMALLINT DEFAULT 1,
    
    -- Scope
    applies_to      VARCHAR(30) DEFAULT 'all',            -- all, category, product
    applicable_ids  UUID[],                               -- IDs of category/product
    
    is_active       BOOLEAN DEFAULT TRUE,
    
    created_by      UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 5. Entity Relationship Diagram (Ringkasan)

```
TENANT SCHEMA ERD (Simplified)

outlets ──< tenant_users >── users(global)
   │
   ├──< transactions ──< transaction_items ──▶ products
   │         │                                    │
   │         ▶ customers                          ├──< product_variants
   │         │                                    └──< modifier_groups ──< modifiers
   │         └──< transaction_payments
   │
   ├──< inventory ──▶ products
   ├──< stock_movements ──▶ products
   ├──< tables ──▶ transactions
   └──< cashier_sessions ──▶ transactions


GLOBAL SCHEMA ERD

tenants ──< subscriptions
        ──< invoices
        ──< tenant_users
users   ──< refresh_tokens
        ──< otps
```

---

## 6. Database Migration Strategy

### 6.1 Migration untuk Tenant Baru

```bash
# Saat tenant baru registrasi, jalankan migration untuk schema mereka:
# 1. Create schema
CREATE SCHEMA tenant_{uuid};

# 2. Jalankan semua migration SQL
SET search_path = tenant_{uuid};
migrate -path ./migrations -database "..." up

# 3. Insert seed data (default roles, units, dll)
```

### 6.2 Migration Tool

```go
// Menggunakan golang-migrate
m, err := migrate.New(
    "file://migrations",
    "postgres://user:pass@host/db?search_path=tenant_"+tenantID,
)
m.Up()
```

### 6.3 Versioning

```
migrations/
├── 000001_create_outlets.up.sql
├── 000001_create_outlets.down.sql
├── 000002_create_products.up.sql
├── 000002_create_products.down.sql
...
```

---

## 7. Indexing Strategy

### Critical Indexes (must-have)

```sql
-- Products: sering di-search
CREATE INDEX CONCURRENTLY idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = TRUE;

-- Transactions: laporan per periode
CREATE INDEX idx_transactions_date ON transactions(outlet_id, created_at DESC, status);

-- Stock movements: riwayat stok
CREATE INDEX idx_movements_product_date ON stock_movements(product_id, created_at DESC);

-- Customers: search by phone
CREATE INDEX idx_customers_phone ON customers(phone) WHERE deleted_at IS NULL;
```

---

## 8. Data Retention Policy

| Data | Retention | Aksi Setelah Expired |
|------|-----------|---------------------|
| Transaksi aktif | Permanen (per plan) | — |
| Tenant Free (cancel > 30 hari) | 30 hari | Hard delete schema |
| Tenant Paid (cancel > 1 tahun) | 1 tahun | Archive to cold storage |
| Refresh tokens | 30 hari | Auto-expire |
| OTP | 1 jam | Auto-expire |
| Audit logs | 2 tahun | Archive |
| Soft-deleted records | 90 hari | Hard delete via cron |

---

*Blueprint ini inline dengan: BP-06 (Architecture), BP-07 (Project Structure), BP-10 (Security/RLS)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
