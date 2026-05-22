---
name: xynpos-database
description: XynPOS database, SQL, and migration expert — use when writing PostgreSQL queries, designing schema, creating migrations, optimizing slow queries, working with multi-tenant schema isolation, or managing database changes. Triggers when someone needs to write a SQL migration, add an index, debug a slow query, design a new table, work with GORM, or understand how the tenant schema model works. Also use when asked about data retention, backup strategy, or PostgreSQL configuration.
license: See LICENSE.txt
---

# XynPOS Database & SQL

XynPOS uses PostgreSQL 16 with schema-per-tenant isolation. Every query runs within a tenant schema set via `search_path` from JWT middleware.

## Quick Reference
- Schema model & key tables → `references/schema-guide.md`
- GORM patterns → `references/gorm-patterns.md`
- Migration conventions → `references/migrations.md`

## Architecture

```
PostgreSQL 16 (DO Managed)
    ↓ PgBouncer (port 6432, connection pooling)
    ├── Primary  → all writes + reads
    └── Replica  → report-service reads only

Schemas:
  public_xyn    tenants, subscriptions, invoices, users
  auth_svc      refresh_tokens, otps  
  tenant_{uuid} all business data per tenant
```

## Naming Conventions

```sql
-- Primary key: always UUID v4
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- Soft delete (never hard-delete business data)
deleted_at TIMESTAMPTZ  -- NULL = active

-- Audit fields on every table
created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
created_by UUID
updated_by UUID

-- Naming: snake_case, no abbreviations
-- Always TIMESTAMPTZ (not TIMESTAMP — timezone-aware)
-- Always add index on every FK column
```

## Critical Query Rules

```go
// ✅ ALWAYS: parameterized, with context, specify columns
db.WithContext(ctx).
    Select("id", "name", "selling_price", "stock").
    Where("is_active = ? AND deleted_at IS NULL", true).
    Limit(perPage).Offset((page-1)*perPage).
    Find(&products)

// ❌ NEVER: string concatenation → SQL injection
db.Exec("SELECT * FROM products WHERE name = '" + name + "'")

// ❌ NEVER: SELECT * 
db.Find(&products)  // loads all columns

// ✅ Multi-step: always use transaction
db.Transaction(func(tx *gorm.DB) error {
    if err := tx.Model(&inv).Update(...).Error; err != nil { return err }
    return tx.Create(&transaction).Error
})
```

## Scripts

Use `scripts/check_query.py <file>` to scan for query violations.
Use `scripts/gen_migration.py <name>` to scaffold a new migration file.
