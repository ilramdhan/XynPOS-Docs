<div align="center">

# 📋 XynPOS Documentation

**Dokumentasi komprehensif untuk XynPOS — POS SaaS by Extended Synaptic**

[![Docs](https://img.shields.io/badge/docs-24%20blueprints-blue?style=flat-square)](docs/)
[![Skills](https://img.shields.io/badge/claude%20skills-10%20skills-purple?style=flat-square)](skills/)
[![Version](https://img.shields.io/badge/version-2.0-green?style=flat-square)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-Proprietary-red?style=flat-square)](#)

[📚 Blueprints](#-blueprints) · [🤖 Claude Skills](#-claude-skills) · [🗺️ Quick Start](#️-quick-start) · [🏗️ Architecture](#️-architecture-overview)

</div>

---

## Tentang XynPOS

**XynPOS** adalah aplikasi Point of Sale (POS) SaaS multi-tenant Indonesia-first yang dibangun oleh **Extended Synaptic (XYN)**. Produk pertama dari ekosistem XYN yang akan mencakup XYN CRM, XYN ERP, dan lainnya.

| | |
|---|---|
| 🎯 **Target** | UMKM (T1) hingga Enterprise chain store (T4) |
| 🌏 **Market** | Indonesia-first, SEA-ready |
| 💳 **Payment** | QRIS, Midtrans, Xendit, Stripe |
| 📱 **Platform** | Web (Next.js) + iOS & Android (Flutter) |
| ⚡ **Backend** | Go microservices + PostgreSQL multi-tenant |

---

## 🗺️ Quick Start

### Untuk Developer Baru
> **Mulai dari sini →** [`docs/blueprints/developer/19-developer-onboarding-guide.md`](docs/blueprints/developer/19-developer-onboarding-guide.md)

### Untuk Tech Lead / Arsitek
> **Mulai dari sini →** [`docs/blueprints/technical/06-system-architecture-blueprint.md`](docs/blueprints/technical/06-system-architecture-blueprint.md)

### Untuk Product / Founder
> **Mulai dari sini →** [`docs/blueprints/business/01-target-market-competitive-analysis.md`](docs/blueprints/business/01-target-market-competitive-analysis.md)

### Untuk DevOps / SRE
> **Mulai dari sini →** [`docs/blueprints/infrastructure/09-infrastructure-devops-blueprint.md`](docs/blueprints/infrastructure/09-infrastructure-devops-blueprint.md)

---

## 📁 Struktur Repo

```
XynPOS-Docs/
│
├── 📋 README.md                      ← Kamu di sini
│
├── 📚 docs/
│   ├── blueprints/
│   │   ├── business/                 ← Target market, finansial, GTM
│   │   ├── product/                  ← MVP features, post-MVP roadmap
│   │   ├── technical/                ← Tech stack, arsitektur, DB schema, API
│   │   ├── infrastructure/           ← DevOps, CI/CD, cloud infra
│   │   ├── developer/                ← Onboarding, dev rules, testing, CLAUDE.md
│   │   └── compliance/               ← Security, legal, UU PDP
│   ├── adr/                          ← Architecture Decision Records
│   └── runbooks/                     ← Operational procedures
│
└── 🤖 skills/
    ├── shared/                       ← Cross-stack skills (context, API, security, review)
    ├── backend/                      ← Go backend skills
    ├── frontend/                     ← Next.js frontend skills
    ├── mobile/                       ← Flutter mobile skills
    ├── infrastructure/               ← DevOps skills
    └── guides/                       ← Skills setup guide & quick reference
```

---

## 📚 Blueprints

### 📊 Business

| # | Dokumen | Deskripsi |
|---|---------|-----------|
| BP-01 | [Target Market & Competitive Analysis](docs/blueprints/business/01-target-market-competitive-analysis.md) | Segmentasi T1–T4, 4 personas, TAM/SAM ~5M, analisis kompetitor |
| BP-02 | [Financial & Subscription Mechanism](docs/blueprints/business/02-financial-subscription-mechanism.md) | 3 model bisnis, pricing Rp0–2jt+, BEP bulan 5–6, proyeksi ARR |
| BP-15 | [Go-To-Market & Launch Blueprint](docs/blueprints/business/15-gtm-launch-blueprint.md) | PLG strategy, 3 phase akuisisi, referral, launch checklist, KPI |

### 📦 Product

| # | Dokumen | Deskripsi |
|---|---------|-----------|
| BP-03 | [MVP Features Blueprint](docs/blueprints/product/03-mvp-features-blueprint.md) | 8 domain, 47 fitur inti, sprint plan 12 minggu |
| BP-04 | [Post-MVP Advanced Features](docs/blueprints/product/04-post-mvp-advanced-features.md) | 6 waves: PO, KDS, Recipe, Promo, e-Faktur, AI forecasting |

### ⚙️ Technical

| # | Dokumen | Deskripsi |
|---|---------|-----------|
| BP-05 | [Tech Stack Blueprint](docs/blueprints/technical/05-tech-stack-blueprint.md) | Stack decisions + rationale: Go, Flutter, Next.js, PostgreSQL |
| BP-06 | [System Architecture Blueprint](docs/blueprints/technical/06-system-architecture-blueprint.md) | Multi-tenant, auth flow, microservice comm, security layers |
| BP-07 | [Project Structure Blueprint](docs/blueprints/technical/07-project-structure-blueprint.md) | Monorepo structure, naming conventions, Makefile commands |
| BP-08 | [Database Schema Blueprint](docs/blueprints/technical/08-database-schema-blueprint.md) | Full SQL schema (global + tenant) + ERD + migration strategy |
| BP-11 | [API Design Blueprint](docs/blueprints/technical/11-api-design-blueprint.md) | All endpoints, request/response format, webhooks, versioning |
| BP-12 | [Mobile App Blueprint](docs/blueprints/technical/12-mobile-app-blueprint.md) | Flutter architecture, offline mode, BT printer, QRIS polling |

### 🏗️ Infrastructure

| # | Dokumen | Deskripsi |
|---|---------|-----------|
| BP-09 | [Infrastructure & DevOps Blueprint](docs/blueprints/infrastructure/09-infrastructure-devops-blueprint.md) | DO ~$176/bln, Docker, GitHub Actions CI/CD, K8s manifests |

### 👨‍💻 Developer

| # | Dokumen | Deskripsi |
|---|---------|-----------|
| BP-13 | [CLAUDE.md (AI Instructions)](docs/blueprints/developer/13-CLAUDE-ai-instructions.md) | Daily reference untuk Claude Code: commands, patterns, rules |
| BP-14 | [Testing Strategy Blueprint](docs/blueprints/developer/14-testing-strategy-blueprint.md) | Test pyramid, unit/integration/E2E, coverage targets, k6 |
| BP-19 | [Developer Onboarding Guide](docs/blueprints/developer/19-developer-onboarding-guide.md) | Setup lokal, akses, workflow, tools, FAQ, checklist |
| BP-20 | [Dev Rules — Backend (Go)](docs/blueprints/developer/20-dev-rules-backend.md) | Law untuk Go: clean arch, error, logging, DB, security, test |
| BP-21 | [Dev Rules — Frontend (Next.js)](docs/blueprints/developer/21-dev-rules-frontend.md) | Law untuk Next.js: component, state, TypeScript, performance |
| BP-22 | [Dev Rules — Mobile (Flutter)](docs/blueprints/developer/22-dev-rules-mobile.md) | Law untuk Flutter: architecture, Riverpod, offline, Either |
| BP-23 | [Dev Rules — Infrastructure](docs/blueprints/developer/23-dev-rules-infrastructure.md) | Law untuk DevOps: Terraform, Docker, K8s, secrets, monitoring |
| BP-24 | [Claude Skills Plan](docs/blueprints/developer/24-claude-skills-plan.md) | Roadmap dan rencana 10 skills untuk AI-assisted development |

### 🔒 Compliance

| # | Dokumen | Deskripsi |
|---|---------|-----------|
| BP-10 | [Security Blueprint](docs/blueprints/compliance/10-security-blueprint.md) | STRIDE threat model, RBAC, injection prevention, UU PDP |
| BP-16 | [Legal & Compliance Blueprint](docs/blueprints/compliance/16-legal-compliance-blueprint.md) | PT pendirian, ToS, Privacy Policy, merek HKI, pajak |

### 📐 Architecture Decision Records

| # | ADR | Keputusan |
|---|-----|-----------|
| ADR-001 | Go sebagai backend language | Performance, concurrency, binary simple |
| ADR-002 | Flutter untuk mobile | 1 codebase iOS+Android, native performance |
| ADR-003 | Schema-per-tenant | Isolasi data terkuat untuk Phase 1 |
| ADR-004 | Monorepo | Tim kecil, shared types, single CI/CD |
| ADR-005 | NATS sebagai message broker | Ringan, low latency, cukup untuk Phase 1 |
| ADR-006 | Cloudflare R2 untuk storage | Zero egress fee, S3-compatible, CDN terintegrasi |
| ADR-007 | JWT + Refresh Token Rotation | Stateless + aman dengan reuse detection |
| ADR-008 | Next.js App Router | SSR/CSR hybrid, Server Components |

> 📄 Detail lengkap: [`docs/adr/17-adr-architecture-decision-records.md`](docs/adr/17-adr-architecture-decision-records.md)

### 📖 Runbooks

| Dokumen | Isi |
|---------|-----|
| [Operational Runbook](docs/runbooks/18-operational-runbook.md) | Service down, DB issues, payment failure, deployment, rollback, security incidents |

---

## 🤖 Claude Skills

Skills untuk AI-assisted development menggunakan Claude. Setup sekali, produktif selamanya.

| Skill | File | Dipakai Untuk |
|-------|------|---------------|
| SKILL-00 | [Project Context](skills/shared/SKILL-00-project-context.md) | **Master skill — selalu di-load pertama** |
| SKILL-01 | [Go Backend](skills/backend/SKILL-01-go-backend.md) | Coding session backend Go |
| SKILL-02 | [Database & SQL](skills/backend/SKILL-02-database-sql.md) | Query, schema, migration |
| SKILL-03 | [Next.js Frontend](skills/frontend/SKILL-03-nextjs-frontend.md) | Web dashboard & POS |
| SKILL-04 | [Flutter Mobile](skills/mobile/SKILL-04-flutter-mobile.md) | Mobile app development |
| SKILL-05 | [DevOps & Infra](skills/infrastructure/SKILL-05-devops-infra.md) | Docker, CI/CD, K8s, Terraform |
| SKILL-06 | [API Design](skills/shared/SKILL-06-api-design.md) | Design endpoint, review API |
| SKILL-07 | [Security Review](skills/shared/SKILL-07-security-review.md) | Security audit, UU PDP compliance |
| SKILL-08 | [Code Review](skills/shared/SKILL-08-code-review.md) | Review PR semua stack |
| SKILL-09 | [Documentation](skills/shared/SKILL-09-documentation.md) | Update blueprint, ADR, docs |
| SKILL-10 | [Sprint Planning](skills/shared/SKILL-10-sprint-planning.md) | Estimasi, task breakdown, roadmap |

### ⚡ Setup Skills dalam 3 Menit

1. Buka **claude.ai** → **Projects** → **+ New Project** → Nama: `XynPOS Development`
2. Klik ⚙️ **Project Settings** → **Custom Instructions**
3. Copy-paste isi **SKILL-00** (wajib) + skill sesuai role kamu
4. Upload `docs/blueprints/developer/13-CLAUDE-ai-instructions.md` sebagai project knowledge

**→ Panduan lengkap:** [`skills/guides/SKILLS-GUIDE.md`](skills/guides/SKILLS-GUIDE.md)  
**→ Quick reference:** [`skills/guides/SKILLS-QUICKREF.md`](skills/guides/SKILLS-QUICKREF.md)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENTS                             │
│  Web Browser (Next.js)    Flutter iOS    Flutter Android │
└─────────────────┬──────────────┬──────────┬─────────────┘
                  └──────────────┼──────────┘
                                 ▼
                    Cloudflare (WAF + CDN + DNS)
                                 ▼
                       API Gateway (Kong)
                    Rate Limit · JWT · Routing
                                 ▼
        ┌──────────┬──────────┬──────────┬──────────┐
        │ Auth Svc │ POS Svc  │ Product  │ Payment  │
        │  :8001   │  :8005   │  :8003   │  :8006   │
        └────┬─────┴────┬─────┴────┬─────┴────┬─────┘
             └──────────┴──────────┴──────────┘
                              ▼
              ┌───────────────────────────┐
              │   PostgreSQL 16           │
              │   (schema-per-tenant)     │
              │   + Redis + Meilisearch   │
              └───────────────────────────┘
                              ▼
                    Cloudflare R2 (Storage)
```

**Tech Stack ringkas:**

| Layer | Stack |
|-------|-------|
| Backend | Go 1.22 + Fiber v2 + gRPC |
| Web | Next.js 14 + TypeScript + Tailwind + shadcn/ui |
| Mobile | Flutter 3 + Dart + Riverpod |
| Database | PostgreSQL 16 (schema-per-tenant) + Redis 7 |
| Storage | Cloudflare R2 |
| Cloud | DigitalOcean → AWS (Phase 3) |

---

## 🗓️ Roadmap

```
Phase 1: MVP (Bulan 1-3)    → Auth, Product, POS Core, Payment, Reports
Phase 2: Launch (Bulan 4-6) → Beta → Public Launch 🚀
Wave 1 (Bulan 7-8)          → Purchase Order, KDS, Shift, Stocktake
Wave 2-3 (Bulan 9-12)       → F&B Deep, Retail Intelligence
Year 2                       → Enterprise, Marketplace, AI Features
```

---

## 📝 Contributing to Docs

### Update Blueprint yang Ada
1. Edit file yang relevan di `docs/blueprints/`
2. Update versi di header dokumen
3. Commit: `docs(bp-XX): [deskripsi perubahan]`

### Tambah ADR Baru
1. Edit `docs/adr/17-adr-architecture-decision-records.md`
2. Tambahkan ADR baru mengikuti template yang ada
3. Commit: `docs(adr): ADR-XXX [judul keputusan]`

### Update Skills
1. Edit file di `skills/` directory
2. Update `version` di frontmatter
3. Commit: `docs(skills): update SKILL-XX [deskripsi]`
4. Update Project Instructions di claude.ai

### Commit Message Convention
```
docs(bp-XX): update [section] — [deskripsi singkat]
docs(adr):   ADR-XXX: [judul keputusan]
docs(skills): update SKILL-XX — [deskripsi]
docs(readme): update [section]
```

---

## 📊 Stats

| Kategori | Jumlah |
|----------|--------|
| Total Blueprints | 24 dokumen |
| Architecture Decision Records | 8 ADR |
| Operational Runbooks | 1 |
| Claude Skills | 10 skills |
| Total Size | ~750KB |

---

<div align="center">

**Extended Synaptic — Building the OS for Indonesian Business**

[XynPOS](https://xynpos.com) · [Extended Synaptic](https://extendedsynaptic.com) · [GitHub](https://github.com/ilramdhan/XynPOS-Docs)

</div>
