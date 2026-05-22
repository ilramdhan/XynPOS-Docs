---
skill_id: SKILL-00
name: XynPOS Project Context
category: shared
description: Master context skill — wajib di-load pertama untuk semua sesi development XynPOS
version: 1.0.0
applies_to: [all]
---

# SKILL-00: XynPOS Project Context (Master)

## Tentang Proyek

XynPOS adalah aplikasi **Point of Sale (POS) SaaS multi-tenant** buatan **Extended Synaptic (XYN)** — produk pertama dari ekosistem yang akan mencakup XYN CRM, XYN ERP, dan lainnya.

Target pasar: UMKM (T1) hingga Enterprise chain store (T4), Indonesia-first, SEA-ready.

## Tech Stack Ringkas

| Layer | Stack |
|-------|-------|
| Backend | Go 1.22 + Fiber v2, microservice, gRPC antar-service |
| Web | Next.js 14 + TypeScript + Tailwind + shadcn/ui + TanStack Query + Zustand |
| Mobile | Flutter 3 + Dart + Riverpod + go_router |
| Database | PostgreSQL 16 (schema-per-tenant) + Redis 7 + Meilisearch |
| Queue | NATS (Phase 1) → Kafka (Phase 2) |
| Storage | Cloudflare R2 (S3-compatible, zero egress fee) |
| Cloud | DigitalOcean (Phase 1) → AWS (Phase 3) |
| Payment | Xendit + Midtrans + Stripe |

## Arsitektur Multi-Tenant

- Setiap tenant punya PostgreSQL schema sendiri: `tenant_{uuid}`
- Middleware set `search_path` per request dari JWT claims
- Global schema `public_xyn`: tenants, subscriptions, invoices, users
- Auth schema `auth_svc`: refresh_tokens, otps
- **TIDAK BOLEH** ada cross-tenant data leakage dalam kondisi apapun

## API Standard

```
Base URL:  /api/v1/{resource}
Auth:      Authorization: Bearer {access_token}

Success:   { "success": true, "data": {...} }
List:      { "success": true, "data": [...], "meta": { "page":1, "per_page":20, "total":100 } }
Error:     { "success": false, "error": { "code": "ERROR_CODE", "message": "..." } }
```

## Struktur Repository (Monorepo)

```
xynpos/
├── backend/services/{service}/  ← 12 Go microservices
├── backend/shared/              ← Shared Go packages (jwt, db, logger, response, errors)
├── frontend/apps/web-pos/       ← Web kasir interface
├── frontend/apps/web-dashboard/ ← Owner/manager dashboard
├── mobile/xynpos_mobile/        ← Flutter app
├── infra/                       ← Terraform, K8s, Docker
└── docs/                        ← Documentation (repository ini)
```

## Service Ports

| Service | Port | Fungsi |
|---------|------|--------|
| auth-service | 8001 | Auth, JWT, OAuth |
| tenant-service | 8002 | Tenant, outlet, subscription |
| product-service | 8003 | Produk, kategori, variant |
| inventory-service | 8004 | Stok, movement, PO |
| pos-service | 8005 | Transaksi, cart, session |
| payment-service | 8006 | Payment gateway integration |
| customer-service | 8007 | CRM dasar, loyalty, hutang |
| report-service | 8008 | Laporan, analytics, export |
| notification-service | 8009 | Push, email, WA |
| file-service | 8010 | Upload, R2 management |
| subscription-service | 8011 | Billing, plan, invoice |
| audit-service | 8012 | Audit log, activity |

## Subscription Plans

| Plan | Harga/Bulan | Outlets | Users |
|------|-------------|---------|-------|
| Free | Rp 0 | 1 | 1 |
| Starter | Rp 149.000 | 1 | 3 |
| Pro | Rp 349.000 | 3 | 10 |
| Business | Rp 749.000 | 10 | 30 |
| Enterprise | Custom (min 2jt) | Unlimited | Unlimited |

## Blueprint References

Semua keputusan ada di `docs/blueprints/`. Saat ada pertanyaan arsitektur, referensikan:
- Keputusan teknis → `docs/adr/`
- Fitur → `docs/blueprints/product/`
- Tech stack → `docs/blueprints/technical/`
- Dev rules → `docs/blueprints/developer/`

## Instruksi untuk Claude

Saat membantu development XynPOS:
1. Selalu ikuti dev rules yang ada di `docs/blueprints/developer/`
2. Gunakan standard response format dari `shared/pkg/response`
3. Tenant context HANYA dari JWT, tidak pernah dari request body/query
4. Referensikan blueprint yang relevan saat ada design decision
5. Jika ada keputusan arsitektur baru → sarankan buat ADR baru di `docs/adr/`
