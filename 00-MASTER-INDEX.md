# XynPOS — Master Blueprint Index
> Extended Synaptic | Version 2.0 | Confidential

---

## 📋 Daftar Semua Blueprint (24 Dokumen)

| # | Nama Blueprint | File | Deskripsi Singkat |
|---|----------------|------|-------------------|
| 00 | **Master Index** | `00-MASTER-INDEX.md` | Dokumen ini — roadmap dan cross-reference |
| 01 | **Target Market & Competitive Analysis** | `01-target-market-competitive-analysis.md` | Segmentasi T1–T4, 4 personas, TAM/SAM, kompetitor |
| 02 | **Financial & Subscription Mechanism** | `02-financial-subscription-mechanism.md` | 3 model bisnis, pricing, BEP bulan 5–6, proyeksi ARR |
| 03 | **MVP Features Blueprint** | `03-mvp-features-blueprint.md` | 8 domain, 47 fitur, sprint plan 12 minggu |
| 04 | **Post-MVP Advanced Features** | `04-post-mvp-advanced-features.md` | 6 wave: PO, KDS, Recipe, Promo, e-Faktur, AI |
| 05 | **Tech Stack Blueprint** | `05-tech-stack-blueprint.md` | Go + Fiber, Next.js 14, Flutter 3, PostgreSQL, Redis |
| 06 | **System Architecture Blueprint** | `06-system-architecture-blueprint.md` | Multi-tenant, auth flow, microservice, security layers |
| 07 | **Project Structure Blueprint** | `07-project-structure-blueprint.md` | Monorepo, folder structure Go/Next.js/Flutter/Infra |
| 08 | **Database Schema Blueprint** | `08-database-schema-blueprint.md` | Full SQL schema: global + tenant tables + migration |
| 09 | **Infrastructure & DevOps Blueprint** | `09-infrastructure-devops-blueprint.md` | DO infra, Docker, GitHub Actions CI/CD, K8s |
| 10 | **Security Blueprint** | `10-security-blueprint.md` | STRIDE, RBAC, injection prevention, audit log, UU PDP |
| 11 | **API Design Blueprint** | `11-api-design-blueprint.md` | REST endpoints, request/response format, webhooks |
| 12 | **Mobile App Blueprint** | `12-mobile-app-blueprint.md` | Flutter arch, offline mode, BT printer, QRIS polling |
| 13 | **CLAUDE.md (AI Instructions)** | `13-CLAUDE-ai-instructions.md` | Instruksi Claude Code: commands, conventions, rules |
| 14 | **Testing Strategy Blueprint** | `14-testing-strategy-blueprint.md` | Unit/integration/E2E, coverage targets, k6 load test |
| 15 | **Go-To-Market & Launch Blueprint** | `15-gtm-launch-blueprint.md` | PLG strategy, 3 phase, referral, launch checklist |
| 16 | **Legal & Compliance Blueprint** | `16-legal-compliance-blueprint.md` | PT pendirian, ToS, Privacy Policy, UU PDP, HKI |
| 17 | **ADR — Architecture Decision Records** | `17-adr-architecture-decision-records.md` | 8 ADR: Go, Flutter, multi-tenancy, monorepo, NATS, R2 |
| 18 | **Operational Runbook** | `18-operational-runbook.md` | Prosedur operasional: service down, DB, payment, deploy |
| 19 | **Developer Onboarding Guide** | `19-developer-onboarding-guide.md` | Setup lokal, akses, workflow, FAQ untuk dev baru |
| 20 | **Dev Rules — Backend (Go)** | `20-dev-rules-backend.md` | Rules wajib: clean arch, error handling, security, test |
| 21 | **Dev Rules — Frontend (Next.js)** | `21-dev-rules-frontend.md` | Rules wajib: component rules, state, TypeScript, perf |
| 22 | **Dev Rules — Mobile (Flutter)** | `22-dev-rules-mobile.md` | Rules wajib: architecture, Riverpod, offline, Either |
| 23 | **Dev Rules — Infrastructure** | `23-dev-rules-infrastructure.md` | Rules wajib: Terraform, Docker, K8s, secrets, monitoring |
| 24 | **Claude Skills Plan** | `24-claude-skills-plan.md` | 10 skills untuk AI-assisted development XynPOS |

---

## 📚 Recommended Reading Order

### 👔 Founder / Decision Maker
1. `01` → Pahami target market dan kompetitor
2. `02` → Model bisnis dan proyeksi keuangan
3. `03` → Apa yang dibangun di MVP
4. `15` → Bagaimana launch dan akuisisi
5. `16` → Legal dan compliance yang harus disiapkan

### 👨‍💻 Lead Developer (Backend Go)
1. `05` → Tech stack decisions
2. `06` → System architecture
3. `07` → Project structure
4. `08` → Database schema
5. `20` → Backend dev rules (**wajib sebelum mulai coding**)
6. `13` → CLAUDE.md untuk daily reference
7. `17` → ADR untuk memahami keputusan arsitektur

### 🖥️ Frontend Developer (Next.js)
1. `05` → Tech stack (bagian frontend)
2. `07` → Project structure (bagian frontend)
3. `11` → API endpoints yang dipakai
4. `21` → Frontend dev rules (**wajib sebelum mulai coding**)
5. `13` → CLAUDE.md

### 📱 Mobile Developer (Flutter)
1. `12` → Mobile app blueprint
2. `05` → Tech stack (bagian mobile)
3. `07` → Project structure (bagian mobile)
4. `22` → Mobile dev rules (**wajib sebelum mulai coding**)
5. `11` → API yang dipakai

### 🔧 DevOps / SRE
1. `09` → Infrastruktur dan CI/CD
2. `06` → Arsitektur (konteks deployment)
3. `10` → Security requirements
4. `23` → Infrastructure dev rules (**wajib**)
5. `18` → Operational runbook

### 🆕 Developer Baru (Any Role)
1. `19` → **Mulai dari sini** — Developer Onboarding Guide
2. Kemudian ikuti reading order sesuai role di atas

---

## 🔗 Cross-Reference Matrix

| Blueprint | Terkait Erat Dengan |
|-----------|---------------------|
| BP-01 (Market) | BP-02 (pricing), BP-03 (features/segmen), BP-15 (GTM) |
| BP-02 (Financial) | BP-01, BP-03 (plan features), BP-15, BP-16 (pajak) |
| BP-03 (MVP) | BP-04, BP-05, BP-08 (schema), BP-12 (mobile) |
| BP-04 (Post-MVP) | BP-03, BP-05, BP-02 (plan features) |
| BP-05 (Tech Stack) | BP-06, BP-07, BP-09 |
| BP-06 (Architecture) | BP-05, BP-07, BP-08, BP-10 |
| BP-07 (Structure) | BP-05, BP-06, BP-11, BP-13 |
| BP-08 (DB Schema) | BP-06, BP-07, BP-10 (security/RLS) |
| BP-09 (Infra/DevOps) | BP-05, BP-06, BP-10, BP-23 |
| BP-10 (Security) | BP-06, BP-09, BP-11, BP-16 (UU PDP) |
| BP-11 (API) | BP-06, BP-07, BP-10 |
| BP-12 (Mobile) | BP-03, BP-05, BP-07, BP-22 |
| BP-13 (CLAUDE.md) | **Semua** — daily dev reference |
| BP-14 (Testing) | BP-07, BP-09 (CI/CD) |
| BP-15 (GTM) | BP-01, BP-02, BP-16 |
| BP-16 (Legal) | BP-02 (billing), BP-10 (UU PDP), BP-15 |
| BP-17 (ADR) | BP-05, BP-06 (decisions) |
| BP-18 (Runbook) | BP-09 (infra), BP-10 (security incidents) |
| BP-19 (Onboarding) | **Semua** — entry point untuk dev baru |
| BP-20 (BE Rules) | BP-06, BP-07, BP-08, BP-14 |
| BP-21 (FE Rules) | BP-07, BP-11, BP-14 |
| BP-22 (Mobile Rules) | BP-07, BP-12, BP-14 |
| BP-23 (Infra Rules) | BP-09, BP-10, BP-18 |
| BP-24 (Claude Skills) | **Semua** — AI-assisted dev |

---

## 🗓️ Development Timeline

```
PHASE 0 — Pre-Development (Bulan 0)
├── ✅ Semua blueprint selesai
├── Pendirian PT Extended Synaptic Indonesia
├── Daftar merek XynPOS ke DJKI
├── Setup monorepo GitHub
└── Hire Flutter dev + UI/UX freelance

PHASE 1 — MVP Development (Bulan 1–3, 6 Sprint × 2 minggu)
├── Sprint 1–2: Auth service, Tenant service, infra lokal
├── Sprint 3–4: Product service (CRUD, kategori, variant)
├── Sprint 5–6: POS Core (kasir screen, cart, checkout)
└── Sprint 7–8: Payment (cash, QRIS) + Inventory dasar

PHASE 2 — Complete MVP + Beta (Bulan 4–6)
├── Sprint 9–10: Reports, User management, Flutter mobile
├── Sprint 11: Beta program (20–50 early adopters)
├── Sprint 12: Bug fix, polish, QA
└── 🚀 PUBLIC LAUNCH

PHASE 3 — Post-MVP Wave 1 (Bulan 7–8)
├── Purchase Order (PO)
├── Kitchen Display System (KDS)
├── Shift Management
└── Stocktake

PHASE 4 — Wave 2–3 (Bulan 9–12)
├── F&B: Recipe, Reservasi, QR Self-Order
└── Retail: Promo Campaign, Batch/Expired, Price List

YEAR 2 — Enterprise + Ecosystem
├── Wave 4: Multi-outlet Dashboard, e-Faktur, API Platform
├── Wave 5: XYN CRM/ERP Integration, Marketplace
└── Wave 6: AI Forecasting, Smart Promo, Conversational AI
```

---

## 💡 Key Decisions Summary

| Keputusan | Pilihan | ADR |
|-----------|---------|-----|
| Backend language | Go 1.22 + Fiber v2 | ADR-001 |
| Mobile framework | Flutter 3 + Dart | ADR-002 |
| Multi-tenancy strategy | Schema-per-tenant (Phase 1) | ADR-003 |
| Repository strategy | Monorepo | ADR-004 |
| Message broker | NATS → Kafka | ADR-005 |
| Object storage | Cloudflare R2 | ADR-006 |
| Auth mechanism | JWT + Refresh Token Rotation | ADR-007 |
| Web framework | Next.js 14 App Router | ADR-008 |
| Business model | Hybrid Freemium + Trial 30 hari | BP-02 |
| Cloud provider | DigitalOcean → AWS | BP-05, BP-09 |
| Payment gateways | Xendit + Midtrans + Stripe | BP-05 |

---

## 📊 Dokumen Stats

| Kategori | Jumlah Blueprint | Coverage |
|----------|-----------------|---------|
| Business & Strategy | 3 (BP-01, 02, 15) | Market, financial, GTM |
| Product | 2 (BP-03, 04) | MVP + post-MVP roadmap |
| Technical Architecture | 4 (BP-05, 06, 07, 08) | Stack, arch, structure, DB |
| Infrastructure | 2 (BP-09, 18) | DevOps, runbook |
| Security & Compliance | 2 (BP-10, 16) | Security, legal |
| API & Integration | 1 (BP-11) | API design |
| Platform-Specific | 1 (BP-12) | Mobile |
| Developer Experience | 6 (BP-13, 19, 20, 21, 22, 23) | CLAUDE.md, onboarding, rules |
| Quality | 1 (BP-14) | Testing strategy |
| Architecture Records | 1 (BP-17) | ADR |
| AI Assistance | 1 (BP-24) | Claude skills |
| **Total** | **24 Blueprint** | **~580KB dokumentasi** |

---

*XynPOS — Extended Synaptic*
*Documentation v2.0 | 24 Blueprints | Generated: 2025*
*Repository: https://github.com/ilramdhan/XynPOS-Docs*
