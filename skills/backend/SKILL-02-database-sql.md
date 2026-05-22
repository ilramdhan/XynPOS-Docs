---
skill_id: SKILL-02
name: XynPOS Database & SQL
category: backend
description: Skill untuk query PostgreSQL, schema design, migration, dan optimization
version: 1.0.0
applies_to: [database, postgresql, migration, schema]
depends_on: [SKILL-00]
---

# SKILL-02: Database & SQL

## Architecture

```
PostgreSQL Cluster
├── Schema: public_xyn          ← Global: tenants, subscriptions, users, invoices
├── Schema: auth_svc            ← Auth: refresh_tokens, otps
├── Schema: tenant_{uuid}       ← Per-tenant (semua tabel bisnis)
│   ├── outlets, tenant_users, roles
│   ├── products, product_variants, categories, units
│   ├── modifier_groups, modifiers
│   ├── inventory, stock_movements
│   ├── cashier_sessions, transactions, transaction_items
│   ├── transaction_payments, transaction_discounts
│   ├── customers, loyalty_point_logs, customer_debts
│   ├── tables, table_areas
│   └── promotions
└── PgBouncer → connection pooling (port 6432)
```

## Conventions

```sql
-- Primary key: UUID v4
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- Soft delete
deleted_at TIMESTAMPTZ  -- NULL = active, filled = deleted

-- Audit fields  
created_at TIMESTAMPTZ DEFAULT NOW()
updated_at TIMESTAMPTZ DEFAULT NOW()
created_by UUID
updated_by UUID

-- Datetime: ALWAYS TIMESTAMPTZ (bukan TIMESTAMP)
-- Naming: snake_case
-- FK: always add index
```

## Query Rules

```sql
-- ✅ Parameterized query (WAJIB)
db.Where("name = ?", name).Find(&products)
db.Raw("SELECT id, name FROM products WHERE outlet_id = ?", outletID).Scan(&result)

-- ❌ String concat (SQL INJECTION!)
db.Exec("SELECT * FROM products WHERE name = '" + name + "'")

-- ✅ Specify columns
db.Select("id", "name", "selling_price").Find(&products)

-- ❌ No SELECT *
db.Find(&products)  -- loads all columns unnecessarily

-- ✅ Always paginate list queries
db.Limit(perPage).Offset((page-1)*perPage).Find(&items)

-- ✅ Use context for timeout
db.WithContext(ctx).Where(...).Find(&items)
```

## Schema Search Path (Multi-tenant)

```go
// Middleware sudah handle ini — SELALU lewat middleware
// Jika butuh raw execution, sanitize dulu:
schemaName := "tenant_" + sanitizeTenantID(tenantID)
// Valid: hanya lowercase alphanumeric + underscore
if !regexp.MustCompile(`^tenant_[a-z0-9]{8,}$`).MatchString(schemaName) {
    return ErrInvalidTenant
}
db.Exec("SET search_path = " + schemaName) // safe setelah sanitize
```

## Key Table Relationships

```
outlets ──< tenant_users >── users (global)
outlets ──< transactions ──< transaction_items ──▶ products
                   │         └──< transaction_item_modifiers ──▶ modifiers
                   ├──▶ customers ──< loyalty_point_logs
                   └──< transaction_payments
products ──< product_variants
products ──< product_modifier_groups ──▶ modifier_groups ──< modifiers
outlets  ──< inventory ──▶ products
outlets  ──< stock_movements ──▶ products
outlets  ──< tables ──▶ transactions
outlets  ──< cashier_sessions ──▶ transactions
```

## Important Indexes

```sql
-- Product search (GIN trigram)
CREATE INDEX idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);

-- Transaction reporting
CREATE INDEX idx_transactions_outlet_date ON transactions(outlet_id, created_at DESC, status);

-- FK indexes (wajib di semua FK)
CREATE INDEX idx_transactions_customer ON transactions(customer_id) WHERE customer_id IS NOT NULL;
CREATE INDEX idx_stock_movements_product ON stock_movements(product_id, outlet_id, created_at DESC);
CREATE INDEX idx_customers_phone ON customers(phone) WHERE deleted_at IS NULL;

-- Offline sync
CREATE INDEX idx_transactions_local_id ON transactions(local_id) WHERE local_id IS NOT NULL;
```

## Migration Rules

```bash
# Naming: {version}_{description}.up.sql & .down.sql
# Contoh:
000001_create_outlets.up.sql
000001_create_outlets.down.sql

# Run migration untuk tenant tertentu
migrate -path ./migrations \
  -database "postgres://xynpos:pass@localhost/xynpos?search_path=tenant_abc123" up

# Run untuk semua tenant aktif
for TENANT in $(psql $DB_URL -t -c "SELECT schema_name FROM public_xyn.tenants WHERE status='active'"); do
  migrate -path ./migrations -database "$DB_URL?search_path=$TENANT" up
done

# Rules:
# ✅ Migration harus idempotent
# ✅ Selalu ada down migration
# ❌ JANGAN modify migration yang sudah di-deploy
# ❌ JANGAN drop column langsung — deprecated dulu, hapus sprint berikutnya
```

## Performance Optimization

```sql
-- Cek slow queries
SELECT pid, now() - query_start AS duration, query, state
FROM pg_stat_activity
WHERE (now() - query_start) > interval '5 seconds'
ORDER BY duration DESC;

-- EXPLAIN ANALYZE untuk query lambat
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM transactions
WHERE outlet_id = 'uuid' AND created_at > NOW() - INTERVAL '30 days';

-- Check index usage
SELECT relname, idx_scan, seq_scan
FROM pg_stat_user_tables
WHERE schemaname = 'tenant_abc123'
ORDER BY seq_scan DESC;
```

## Data Retention

| Data | Retention | Action |
|------|-----------|--------|
| Tenant Free (cancel) | 30 hari | Hard delete schema |
| Tenant Paid (cancel) | 1 tahun | Archive cold storage |
| Refresh tokens | 30 hari | Auto-expire |
| OTP | 1 jam | Auto-expire |
| Audit logs | 2 tahun | Archive |
| Soft-deleted records | 90 hari | Hard delete via cron |
