---
name: xynpos-context
description: XynPOS master project context — loads essential architecture, stack, conventions, and service map for the XynPOS POS SaaS application by Extended Synaptic. Use this skill at the start of ANY XynPOS development session, or whenever you need to answer questions about the project architecture, service responsibilities, tech stack choices, API standards, multi-tenancy model, subscription plans, or codebase conventions. Also triggers when a developer asks "how does XynPOS work", "what stack do we use", "where does X live in the codebase", or starts working on any XynPOS feature.
license: See LICENSE.txt
---

# XynPOS — Master Project Context

XynPOS is a **multi-tenant SaaS Point of Sale** application by **Extended Synaptic (XYN)**. Load this skill at the start of every XynPOS dev session to get full project orientation.

## Quick Load

Read the relevant reference files based on what you need:
- Architecture overview → `references/architecture.md`
- Full service map & ports → `references/services.md`  
- API standards → `references/api-standards.md`
- Subscription plans & limits → `references/plans.md`

## Project at a Glance

| Dimension | Detail |
|-----------|--------|
| Product | Point of Sale SaaS, Indonesia-first |
| Company | Extended Synaptic (XYN) |
| Segments | T1 UMKM → T4 Enterprise |
| Primary market | Indonesia, SEA expansion Year 2 |
| Repository | github.com/extendedsynaptic/xynpos (monorepo) |
| Docs repo | github.com/ilramdhan/XynPOS-Docs |

## Tech Stack Summary

| Layer | Stack |
|-------|-------|
| **Backend** | Go 1.22 + Fiber v2 + gRPC (inter-service) |
| **Web** | Next.js 14 + TypeScript + Tailwind + shadcn/ui |
| **Mobile** | Flutter 3 + Dart + Riverpod + go_router |
| **Database** | PostgreSQL 16 (schema-per-tenant) + Redis 7 |
| **Search** | Meilisearch |
| **Queue** | NATS → Kafka (Phase 2) |
| **Storage** | Cloudflare R2 (S3-compatible, zero egress) |
| **Cloud** | DigitalOcean → AWS Phase 3 |
| **Payment** | Xendit + Midtrans + Stripe |
| **Push** | Firebase FCM |

## Multi-Tenancy Model

Every tenant gets an isolated PostgreSQL schema `tenant_{uuid}`. The API Gateway middleware sets `search_path` from JWT claims before every request. **There must be zero cross-tenant data access under any circumstances.**

```
Schemas:
  public_xyn    → tenants, subscriptions, invoices, users (global)
  auth_svc      → refresh_tokens, otps
  tenant_{uuid} → all business data (products, transactions, customers…)
```

## API Standard (non-negotiable)

```json
// Success
{ "success": true, "data": { ... } }
{ "success": true, "data": [...], "meta": { "page":1, "per_page":20, "total":100 } }

// Error
{ "success": false, "error": { "code": "PRODUCT_NOT_FOUND", "message": "...", "http_status": 404 } }
```

Base URL: `/api/v1/` · Auth: `Authorization: Bearer {token}`

## Critical Security Rules

1. `tenantID` **always** from `c.Locals("tenantID")` (JWT) — never from request body/query
2. All SQL via GORM parameterized — never string concatenation
3. No secrets in code, Dockerfiles, or logs
4. Sensitive data (password, PIN, NPWP) never logged

## Monorepo Layout

```
xynpos/
├── backend/services/{service}/   12 Go microservices
├── backend/shared/               shared packages: jwt, db, response, errors, logger
├── frontend/apps/web-pos/        Kasir interface (Next.js)
├── frontend/apps/web-dashboard/  Owner dashboard (Next.js)
├── mobile/xynpos_mobile/         Flutter iOS + Android
└── infra/                        Terraform, K8s, Docker
```

For deep detail on any topic, read the appropriate reference file.
