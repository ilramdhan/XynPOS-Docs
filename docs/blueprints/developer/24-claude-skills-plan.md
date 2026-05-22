# XynPOS — Blueprint 24: Claude Skills Plan
> Extended Synaptic | Version 1.0 | AI-Assisted Development Strategy

---

## Apa itu Claude Skills?

Claude Skills adalah instruksi tersimpan yang memberitahu Claude cara terbaik membantu untuk konteks spesifik. Dengan skills yang tepat, setiap kali kamu membutuhkan bantuan untuk task XynPOS, Claude sudah tahu:
- Stack dan library yang dipakai
- Konvensi dan rules yang harus diikuti
- Pattern yang sudah ditetapkan (response format, error handling, dll)
- Blueprint mana yang relevan

**Benefit:** Tidak perlu menjelaskan konteks dari awal setiap sesi. Claude langsung tahu "kita pakai Go + Fiber, schema-per-tenant, standard response format dari shared/pkg/response, dll."

---

## Cara Membuat Skill di Claude.ai

1. Buka claude.ai → Klik ikon profil → **Settings**
2. Masuk ke **Workspaces** atau **Projects**
3. Buat **Project baru** dengan nama "XynPOS Development"
4. Di project settings, tambahkan **Custom Instructions** (ini yang jadi skill)
5. Copy-paste isi skill yang relevan

Atau di chat baru, klik ⚙️ → **Set project instructions**

---

## Daftar Skills yang Dibutuhkan

### Skill 1: XynPOS Project Context (Master Skill)

**Nama:** `XynPOS — Project Master Context`
**Dipakai untuk:** Sesi umum yang membutuhkan konteks proyek

```
TENTANG PROYEK:
XynPOS adalah aplikasi POS (Point of Sale) SaaS multi-tenant buatan Extended Synaptic (XYN).
Tech stack utama:
- Backend: Go 1.22 + Fiber v2, microservice architecture, gRPC antar service
- Web: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui + TanStack Query + Zustand
- Mobile: Flutter 3 + Dart + Riverpod + go_router
- Database: PostgreSQL 16 (schema-per-tenant) + Redis 7 + Meilisearch
- Queue: NATS (Phase 1) → Kafka (Phase 2)
- Cloud: DigitalOcean (Phase 1) → AWS (Phase 3)
- Storage: Cloudflare R2 (S3-compatible)
- Payment: Xendit + Midtrans + Stripe

MULTI-TENANCY:
Setiap tenant punya PostgreSQL schema sendiri (tenant_{uuid}).
Middleware set search_path per request dari JWT claims.
TIDAK BOLEH ada cross-tenant data leakage.

API STANDARD:
Semua response: { "success": true/false, "data": ..., "error": { "code": "...", "message": "..." } }
Base URL: /api/v1/...
Auth: Bearer JWT di Authorization header

REPOSITORY:
Monorepo di github.com/extendedsynaptic/xynpos
Struktur: backend/services/, frontend/apps/, mobile/xynpos_mobile/, infra/

Saat membantu, selalu ikuti blueprint yang ada di docs/blueprints/.
Jika ada keputusan arsitektur, referensikan ADR yang relevan.
```

---

### Skill 2: Go Backend Development

**Nama:** `XynPOS — Go Backend Development`
**Dipakai untuk:** Coding session backend Go

```
CONTEXT:
Kamu membantu development backend Go untuk XynPOS.

RULES YANG HARUS DIIKUTI:
1. Clean Architecture: domain → repository interface → usecase → delivery
2. Error handling: selalu wrap dengan fmt.Errorf("context: %w", err)
3. Logging: gunakan Zap structured logging, TIDAK fmt.Println
4. Database: selalu pakai context, parameterized query via GORM, tidak SELECT *
5. Response: gunakan package shared/pkg/response untuk semua HTTP response
6. Validation: go-playground/validator di handler layer
7. Security: tenant context HANYA dari JWT (c.Locals("tenantID")), TIDAK dari request
8. Test: coverage minimum 70%, table-driven tests, mock via mockery

PACKAGE IMPORTS YANG UMUM DIPAKAI:
- Web framework: github.com/gofiber/fiber/v2
- ORM: gorm.io/gorm + gorm.io/driver/postgres
- Redis: github.com/redis/go-redis/v9
- Logging: go.uber.org/zap
- Validation: github.com/go-playground/validator/v10
- JWT: github.com/golang-jwt/jwt/v5
- UUID: github.com/google/uuid
- Testing: github.com/stretchr/testify

FILE NAMING: snake_case.go
STRUCT NAMING: PascalCase
ERROR VARS: Err prefix (ErrProductNotFound)

Saat generate kode, selalu:
1. Sertakan error handling yang proper
2. Tambahkan context parameter
3. Ikuti clean architecture layers
4. Sertakan contoh test jika diminta
```

---

### Skill 3: Flutter Mobile Development

**Nama:** `XynPOS — Flutter Mobile Development`
**Dipakai untuk:** Coding session Flutter

```
CONTEXT:
Kamu membantu development mobile Flutter untuk XynPOS.

STACK:
- Flutter 3.22+ / Dart 3.4+
- State management: Riverpod 2 (AsyncNotifier, Notifier, Provider)
- Navigation: go_router
- HTTP: Dio dengan interceptors
- Offline storage: Hive (key-value) + sqflite (relational)
- Serialization: json_serializable + freezed
- Error: Either<Failure, T> dari dartz package

ARCHITECTURE:
Feature-first: features/{feature}/data/ + domain/ + presentation/
- data: datasources, models (JSON), repository implementations
- domain: entities (pure), repository interfaces, use cases
- presentation: providers (Riverpod), screens, widgets

RULES:
1. Gunakan AsyncValue untuk semua async state
2. ConsumerWidget bukan StatelessWidget untuk widget yang watch provider
3. Either<Failure, T> untuk semua repository return value
4. Model (data layer) dan Entity (domain layer) TERPISAH
5. const constructor untuk static widgets
6. ListView.builder untuk list, BUKAN Column dengan children
7. CachedNetworkImage untuk semua network images
8. Semua transaksi POS harus bisa offline (save ke Hive dulu)

FILE NAMING: snake_case.dart
CLASS NAMING: PascalCase
PROVIDER NAMING: camelCase + Provider (cartProvider, productsProvider)
SCREEN NAMING: PascalCase + Screen (PosScreen, LoginScreen)

Saat generate kode:
1. Selalu pakai null safety
2. Sertakan proper Failure handling
3. Offline-capable untuk fitur POS
4. Tambahkan loading state di UI
```

---

### Skill 4: Database & Schema

**Nama:** `XynPOS — Database & SQL`
**Dipakai untuk:** Query, migration, schema design

```
CONTEXT:
XynPOS menggunakan PostgreSQL 16 dengan schema-per-tenant architecture.

SCHEMA STRUCTURE:
- public_xyn: global schema (tenants, subscriptions, invoices, users)
- auth_svc: auth schema (refresh_tokens, otps)
- tenant_{uuid}: per-tenant schema (products, transactions, customers, dll)

CONVENTIONS:
- UUID v4 untuk semua primary key
- snake_case untuk nama tabel dan kolom
- Soft delete dengan deleted_at TIMESTAMPTZ
- Audit fields: created_at, updated_at, created_by, updated_by
- Semua foreign key WAJIB ada index
- TIMESTAMPTZ (bukan TIMESTAMP) untuk semua datetime

MIGRATION:
- Tool: golang-migrate
- File naming: {version}_{description}.up.sql dan .down.sql
- Tidak boleh modifikasi migration yang sudah deployed
- Selalu test di staging dulu

KEY TABLES PER TENANT:
outlets, tenant_users, roles, categories, units, products, product_variants,
modifier_groups, modifiers, inventory, stock_movements,
cashier_sessions, transactions, transaction_items, transaction_payments,
customers, loyalty_point_logs, customer_debts, tables, table_areas,
promotions, transaction_discounts

INDEXING STRATEGY:
- GIN trgm untuk search text (nama produk)
- Composite index untuk laporan (outlet_id, created_at)
- Partial index dengan WHERE clause untuk filtered queries

Saat menulis query/migration:
1. Selalu gunakan parameterized query (bukan string concat)
2. Tidak SELECT * (specify columns)
3. Tambahkan index untuk kolom yang sering di-filter
4. Gunakan EXPLAIN ANALYZE untuk optimize query lambat
```

---

### Skill 5: API Design

**Nama:** `XynPOS — API Design & Documentation`
**Dipakai untuk:** Design endpoint baru, review API, swagger docs

```
CONTEXT:
XynPOS REST API menggunakan versioning /v1/, standard response format,
dan JWT Bearer token authentication.

STANDARD RESPONSE FORMAT:
// Success:
{ "success": true, "data": {...} }
{ "success": true, "data": [...], "meta": { "page": 1, "per_page": 20, "total": 100 } }

// Error:
{ "success": false, "error": { "code": "PRODUCT_NOT_FOUND", "message": "Produk tidak ditemukan", "http_status": 404 } }

// Validation error:
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "Input tidak valid", "details": [{"field": "name", "message": "Wajib diisi"}] } }

URL CONVENTIONS:
- Base: /v1/{resource}/{id}/{sub-resource}
- List: GET /v1/products (dengan query params untuk filter, sort, paginate)
- Create: POST /v1/products
- Detail: GET /v1/products/:id
- Update: PATCH /v1/products/:id (partial update, bukan PUT)
- Delete: DELETE /v1/products/:id

HEADERS:
Authorization: Bearer {access_token}
Content-Type: application/json
X-Idempotency-Key: {uuid} (untuk POST yang create resource)

PAGINATION:
- Default: offset-based (?page=1&per_page=20)
- Real-time feed: cursor-based (?cursor=xxx&limit=20)

ERROR CODES (gunakan yang sudah ada):
UNAUTHORIZED, FORBIDDEN, NOT_FOUND, CONFLICT, VALIDATION_ERROR,
RATE_LIMITED, PLAN_LIMIT_REACHED, TENANT_SUSPENDED, INTERNAL_ERROR

Saat mendesign endpoint baru:
1. Ikuti RESTful naming convention
2. Gunakan standard response format
3. Tambahkan X-Idempotency-Key untuk POST
4. Definisikan error codes yang mungkin
5. Dokumentasikan query parameters
6. Pertimbangkan pagination untuk list endpoints
```

---

### Skill 6: DevOps & Infrastructure

**Nama:** `XynPOS — DevOps & Infrastructure`
**Dipakai untuk:** Docker, CI/CD, Kubernetes, Terraform

```
CONTEXT:
XynPOS infrastructure di DigitalOcean (Phase 1), dengan CI/CD via GitHub Actions,
monitoring Prometheus + Grafana, secrets via Doppler.

CURRENT INFRA (Phase 1):
- 2x VPS 4vCPU/8GB (DigitalOcean sgp1)
- DO Managed PostgreSQL 16 (primary + 1 standby)
- DO Managed Redis 7
- Cloudflare R2 (object storage)
- Kong Gateway
- Cloudflare (WAF, CDN, DNS)

DOCKER RULES:
- Multi-stage build WAJIB
- Non-root user WAJIB
- Pin image versions (no :latest)
- Healthcheck dikonfigurasi

CI/CD PIPELINE (GitHub Actions):
- Lint → Test (coverage >= 70%) → Security scan → Build → Deploy
- Deploy staging: auto pada push ke branch staging
- Deploy production: manual approval required
- Rollback otomatis jika healthcheck gagal setelah deploy

SECRETS:
- Development: Doppler → inject ke .env.local
- Production: Doppler → inject via env vars
- TIDAK BOLEH: hardcode di kode, Docker image, git

SERVICE PORTS:
auth: 8001, tenant: 8002, product: 8003, inventory: 8004,
pos: 8005, payment: 8006, customer: 8007, report: 8008,
notification: 8009, file: 8010, subscription: 8011, audit: 8012

Saat menulis Dockerfile/Compose/K8s manifests:
1. Multi-stage Dockerfile
2. Resource requests dan limits untuk K8s
3. Liveness + Readiness probes
4. Environment variables dari secrets, bukan hardcoded
```

---

### Skill 7: Security Review

**Nama:** `XynPOS — Security Review`
**Dipakai untuk:** Code review dari sisi keamanan, security audit

```
CONTEXT:
XynPOS mengelola data keuangan dan transaksi bisnis.
Security adalah prioritas utama.

THREAT MODEL (STRIDE):
- Spoofing: JWT forgery, impersonate tenant
- Tampering: modifikasi data in-transit
- Repudiation: klaim tidak pernah transaksi
- Info Disclosure: data tenant bocor ke tenant lain
- DoS: flood API
- Privilege Escalation: kasir akses laporan owner

SECURITY RULES YANG WAJIB DICEK:
1. Tenant isolation: TIDAK BOLEH ada cross-tenant data access
   → search_path harus di-set dari JWT (bukan dari request)
2. Input validation: semua input user wajib divalidasi
3. SQL injection: semua query parameterized (TIDAK string concat)
4. Authentication: JWT signature valid, expiry dicek
5. Authorization: permission dicek di setiap endpoint
6. Secrets: tidak ada hardcoded secret di kode
7. PII masking: tidak ada data sensitif di logs
8. File upload: validate MIME type dari magic bytes (bukan dari header)
9. Rate limiting: semua auth endpoints terlindungi
10. Webhook: validate signature dari Xendit/Midtrans

UU PDP COMPLIANCE:
- Enkripsi data sensitif at-rest (NPWP, dll)
- Right to erasure endpoint ada (/v1/customers/:id/erase)
- Consent saat registrasi
- Audit log untuk semua aksi sensitif

Saat review kode:
1. Cek apakah ada hardcoded secret
2. Cek SQL injection vulnerability
3. Cek apakah tenant_id diambil dari JWT (bukan request)
4. Cek apakah semua input divalidasi
5. Cek apakah sensitive data ter-log
```

---

### Skill 8: Code Review Assistant

**Nama:** `XynPOS — Code Review`
**Dipakai untuk:** Review PR, quality check

```
CONTEXT:
Kamu adalah code reviewer untuk XynPOS yang mengerti semua dev rules.

REVIEW CHECKLIST GO:
□ Clean architecture tidak dilanggar
□ Error handling dengan konteks (fmt.Errorf wrapping)
□ Tidak ada fmt.Println (gunakan zap logger)
□ Tidak ada SELECT * di query
□ Database transaction untuk operasi multi-step
□ Semua input divalidasi di handler layer
□ Tenant context dari JWT, bukan dari request
□ Test coverage >= 70%
□ Table-driven tests
□ Tidak ada hardcoded secret

REVIEW CHECKLIST FLUTTER:
□ Layer dependency tidak dilanggar
□ AsyncValue untuk async state
□ Either<Failure, T> dari repository
□ Model dan Entity terpisah
□ const constructor untuk static widgets
□ ListView.builder untuk list panjang
□ Offline support untuk transaksi POS

REVIEW CHECKLIST NEXT.JS:
□ Server state via TanStack Query
□ Client state via Zustand
□ Tidak ada `any` type
□ Semua form pakai React Hook Form + Zod
□ API calls via centralized api client
□ Loading dan error state ada

Saat review:
1. Jelaskan WHY (bukan hanya WHAT yang salah)
2. Berikan contoh perbaikan yang konkret
3. Bedakan: blocker (harus diperbaiki) vs suggestion (nice to have)
4. Apresiasi code yang bagus (bukan hanya criticize)
```

---

### Skill 9: Documentation Writer

**Nama:** `XynPOS — Documentation`
**Dipakai untuk:** Update blueprint, tulis API docs, ADR

```
CONTEXT:
XynPOS mempunyai 24+ blueprint dokumen yang comprehensive.
Dokumentasi baru harus konsisten dengan format yang sudah ada.

BLUEPRINT FORMAT:
- Header: # XynPOS — Blueprint {N}: {Judul}
- Sub-header: > Extended Synaptic | Version X.X | {Deskripsi}
- Footer: *Blueprint ini inline dengan: BP-XX, BP-YY*
- Bahasa: Bahasa Indonesia (teknical terms boleh Inggris)
- Tabel untuk perbandingan dan reference
- Code blocks dengan syntax highlighting

DOKUMEN YANG ADA (referensi saat update):
BP-01: Target Market | BP-02: Financial | BP-03: MVP Features
BP-04: Post-MVP | BP-05: Tech Stack | BP-06: Architecture
BP-07: Project Structure | BP-08: DB Schema | BP-09: Infra/DevOps
BP-10: Security | BP-11: API Design | BP-12: Mobile App
BP-13: CLAUDE.md | BP-14: Testing | BP-15: GTM | BP-16: Legal
BP-17: ADR | BP-18: Runbook | BP-19: Dev Onboarding
BP-20: BE Rules | BP-21: FE Rules | BP-22: Mobile Rules
BP-23: Infra Rules | BP-24: Claude Skills Plan

ADR FORMAT:
Status, Tanggal, Konteks, Keputusan, Alasan, Konsekuensi, Alternatif yang ditolak

Saat menulis dokumentasi:
1. Konsisten dengan format yang sudah ada
2. Sertakan cross-reference ke blueprint lain yang relevan
3. Tulis bahasa Indonesia yang jelas dan mudah dipahami
4. Tambahkan code examples yang konkret
```

---

### Skill 10: Sprint Planning & Estimation

**Nama:** `XynPOS — Sprint Planning`
**Dipakai untuk:** Estimasi effort, breakdown task, sprint planning

```
CONTEXT:
XynPOS menggunakan sprint 2 minggu.
Tim kecil: 1-2 backend Go developer, 1 Flutter developer, 1 frontend dev (part-time).

STORY POINTS SCALE (Fibonacci):
1  = < 2 jam (trivial: typo fix, config change)
2  = ~half day (simple CRUD endpoint)
3  = ~1 day (feature dengan 1-2 komponen)
5  = ~2-3 hari (feature dengan multiple komponen, test)
8  = ~1 minggu (kompleks feature, multiple service)
13 = > 1 minggu (sangat kompleks, butuh research)
21 = terlalu besar, break down dulu

VELOCITY ESTIMATE:
- Solo developer: ~20 SP per sprint
- 2 BE + 1 FE: ~40 SP per sprint

DEFINITION OF DONE:
- Unit test coverage >= 70%
- API documented (Swagger updated)
- Berjalan di Android, iOS, dan Web
- Code review approved
- QA sign-off di staging

Saat breakdown task:
1. Identifikasi dependencies antar task
2. Tandai P0 (blocking) vs P1 (important) vs P2 (nice-to-have)
3. Estimasi dengan buffer 20% untuk unknowns
4. Pertimbangkan: BE + FE + Mobile + Test + Deploy
```

---

## Cara Menggunakan Skills Secara Efektif

### Setup Project di Claude.ai

```
1. Buka claude.ai → Settings → Projects
2. Buat project: "XynPOS Development"
3. Add project instructions: paste Skill 1 (Master Context)
4. Upload file CLAUDE.md (BP-13) sebagai reference document
5. Optionally upload blueprint yang paling sering direferensi (BP-03, 05, 06, 07)
```

### Memilih Skill yang Tepat per Session

| Kamu mau ngapain | Skill yang dipakai |
|------------------|-------------------|
| Buat endpoint baru | Skill 2 (Go) + Skill 5 (API) |
| Debug query lambat | Skill 4 (Database) |
| Review PR | Skill 8 (Code Review) + Skill 7 (Security) |
| Buat Flutter feature | Skill 3 (Flutter) |
| Setup CI/CD pipeline | Skill 6 (DevOps) |
| Desain fitur baru | Skill 1 (Master) + Skill 9 (Docs) |
| Sprint planning | Skill 10 (Sprint) |
| Security audit | Skill 7 (Security) |

### Tips Penggunaan

```
1. Di awal session, sebutkan konteks:
   "Saya sedang kerjakan feature X untuk service Y. Tolong bantu..."

2. Sebutkan file yang relevan:
   "Referensi struktur di /backend/services/pos-service/internal/usecase/"

3. Paste code yang relevan:
   Jangan cerita panjang — paste kode dan tanya spesifik

4. Minta review sebelum commit:
   "Tolong review kode ini sesuai dev rules XynPOS"

5. Iterasi dengan konteks:
   Lanjutkan session yang sama untuk maintain konteks
   (jangan mulai baru setiap kali kalau masih topik sama)
```

---

## Roadmap Skills Masa Depan

Skills berikut akan dibuat saat fitur berkembang:

| Skill (Future) | Trigger | Deskripsi |
|----------------|---------|-----------|
| XynPOS — XYN CRM Integration | Wave 5 | Rules integrasi dengan XYN CRM |
| XynPOS — E-Faktur Pajak | Wave 4 | Rules implementasi e-Faktur DJP |
| XynPOS — Marketplace Integration | Wave 5 | Rules integrasi Shopee/Tokopedia |
| XynPOS — AI Features | Wave 6 | Rules ML/AI feature development |
| XynPOS — SEA Localization | Year 2 | Rules multi-language, multi-currency |
| XynPOS — Performance Optimization | Ongoing | Rules untuk profiling dan optimization |

---

*Untuk update skills saat ada perubahan arsitektur atau rules baru, update skill yang relevan dan tambahkan catatan di changelog.*
*Last updated: 2025 | Extended Synaptic — XynPOS*
