# CLAUDE.md — XynPOS Project Instructions
> Extended Synaptic | For Claude Code & AI Assistants

---

## 🔎 Proyek ini apa?

XynPOS adalah aplikasi Point of Sale (POS) SaaS multi-tenant buatan **Extended Synaptic (XYN)**. Ini adalah produk pertama dari ekosistem XYN yang akan mencakup XYN CRM, XYN ERP, dan lainnya.

- **Backend:** Go 1.22 + Fiber v2, microservice architecture
- **Web:** Next.js 14 + TypeScript + Tailwind + shadcn/ui
- **Mobile:** Flutter 3 + Dart + Riverpod
- **Database:** PostgreSQL 16 (schema-per-tenant) + Redis + Meilisearch
- **Queue:** NATS (Phase 1) → Kafka (Phase 2)

---

## 📂 Struktur Repository

```
xynpos/
├── backend/services/{service-name}/    ← Go microservices
├── backend/shared/                     ← Shared Go packages
├── frontend/apps/web-pos/              ← Web kasir (Next.js)
├── frontend/apps/web-dashboard/        ← Web dashboard (Next.js)
├── mobile/xynpos_mobile/               ← Flutter app
├── infra/                              ← Terraform, K8s, Docker
└── docs/blueprints/                    ← Blueprint dokumen ini
```

Untuk detail lengkap → lihat `docs/blueprints/07-project-structure-blueprint.md`

---

## ⚡ Perintah Umum

### Backend (Go)

```bash
# Run service lokal
make be-auth       # Auth service
make be-pos        # POS service
make be-product    # Product service

# Test
make be-test                          # Semua service
cd backend/services/pos-service && go test ./... -v

# Lint
make be-lint
cd backend/services/pos-service && golangci-lint run ./...

# Generate Swagger docs
make be-swagger SVC=pos-service

# Generate mocks
make mock-gen

# Database migration
make migrate-up TENANT=tenant_abc123
make migrate-down TENANT=tenant_abc123

# Generate protobuf
make proto-gen
```

### Frontend (Next.js)

```bash
cd frontend/apps/web-dashboard
pnpm dev                              # Dev server port 3000

cd frontend/apps/web-pos
pnpm dev                              # Dev server port 3001

# Build
pnpm build

# Lint + type check
pnpm lint
pnpm type-check
```

### Mobile (Flutter)

```bash
cd mobile/xynpos_mobile

flutter pub get
flutter run                           # Run di connected device/emulator
flutter run --flavor staging          # Staging flavor
flutter analyze
flutter test

# Build
flutter build apk --release
flutter build appbundle --release
flutter build ipa --release
```

### Docker

```bash
make docker-up                        # Jalankan semua infra lokal
make docker-down                      # Stop semua
make docker-logs SVC=pos-service      # Lihat log service
```

---

## 🏗️ Konvensi Kode

### Go

**File naming:** `snake_case.go` — contoh: `transaction_repository.go`

**Package structure wajib per service:**
```
internal/
├── domain/       ← Entity + business rules (tidak boleh import infra)
├── repository/   ← Interface data access
├── usecase/      ← Business logic (hanya depend ke domain + repository interface)
├── delivery/     ← HTTP handlers, gRPC (depend ke usecase)
└── event/        ← NATS publisher/subscriber
```

**Wajib:**
- Semua repository dibalik interface (untuk testability)
- Error pakai custom errors dari `shared/pkg/errors`
- Logging pakai `shared/pkg/logger` (Zap), bukan `fmt.Println`
- Response pakai format standard dari `shared/pkg/response`
- Validasi input di handler layer pakai `shared/pkg/validator`
- Semua query PostgreSQL via GORM (tidak boleh string concatenation)

**Contoh error handling yang benar:**
```go
// ✅ BENAR
if err != nil {
    return nil, errors.Wrap(err, "failed to get product by id")
}

// ❌ SALAH
if err != nil {
    return nil, err  // Tidak ada konteks
}

// ❌ SALAH
if err != nil {
    fmt.Println("error:", err)  // Pakai logger!
}
```

**Test coverage minimum: 70%** untuk setiap service. Test file harus ada untuk:
- Semua usecase
- Semua handler (happy path + error cases)
- Utility functions

### TypeScript (Next.js)

**File naming:** `PascalCase.tsx` untuk komponen, `camelCase.ts` untuk utility

**State management:**
- Server state → TanStack Query (`useQuery`, `useMutation`)
- Client-only state → Zustand store
- Form state → React Hook Form + Zod

**Wajib:**
- Semua API call via fungsi di `lib/api.ts` (tidak boleh langsung fetch di komponen)
- Types untuk semua API response dari `packages/types`
- Error boundary di setiap route level

### Dart (Flutter)

**File naming:** `snake_case.dart`

**Wajib:**
- Semua state via Riverpod provider (tidak boleh setState untuk business logic)
- Repository pattern: setiap feature punya `data/repositories/`
- Freezed untuk immutable domain models
- `AsyncValue` untuk state async (loading/error/data)
- Semua network request melalui `core/network/dio_client.dart`

---

## 🔒 Security Rules — WAJIB DIIKUTI

1. **TIDAK BOLEH** hardcode secret, API key, atau password di kode
2. **TIDAK BOLEH** log data sensitif: password, pin, nomor kartu, NPWP
3. **WAJIB** parameterized query — tidak ada string concatenation untuk SQL
4. **WAJIB** validasi semua input user sebelum diproses
5. **WAJIB** cek tenant isolation — setiap query harus dalam tenant context
6. **TIDAK BOLEH** return stack trace di response production
7. **WAJIB** validate webhook signature dari payment gateway
8. **WAJIB** sanitize filename saat file upload

Detail → lihat `docs/blueprints/10-security-blueprint.md`

---

## 🗄️ Database Rules

### Schema per Tenant

Setiap tenant punya schema PostgreSQL sendiri: `tenant_{uuid}`

**Wajib set search_path** sebelum query:
```go
// Middleware sudah handle ini — jangan bypass!
// Jika butuh raw query, pastikan schema name di-sanitize dulu
schemaName := "tenant_" + sanitizeTenantID(tenantID)
db.Exec("SET search_path = ?", schemaName)
```

### Migration

- Semua migration ada di `backend/services/{service}/migrations/`
- Naming: `{version}_{description}.up.sql` dan `.down.sql`
- **Tidak boleh** modifikasi migration yang sudah di-deploy
- Migration harus idempotent (bisa dijalankan ulang safely)

### Query

- Pakai GORM untuk semua query
- Read-heavy query → gunakan read replica
- Tidak boleh `SELECT *` — selalu specify field yang dibutuhkan
- Pagination wajib untuk semua list endpoint

---

## 📡 API Design

Semua endpoint mengikuti format:
```
Base: /api/v1/{resource}

Standard response:
✅ Success: { "success": true, "data": {...} }
❌ Error:   { "success": false, "error": { "code": "...", "message": "..." } }
```

Error codes yang digunakan → lihat `shared/pkg/errors/errors.go`

Detail lengkap → `docs/blueprints/11-api-design-blueprint.md`

---

## 🧪 Testing Strategy

### Go

```go
// Setiap usecase wajib punya test
func TestTransactionUsecase_CreateTransaction(t *testing.T) {
    // Arrange
    mockRepo := mocks.NewTransactionRepository(t)  // mockery generated
    mockRepo.On("Create", mock.Anything, mock.Anything).Return(nil)
    
    uc := usecase.NewTransactionUsecase(mockRepo, ...)
    
    // Act
    result, err := uc.Create(ctx, validRequest)
    
    // Assert
    assert.NoError(t, err)
    assert.NotNil(t, result)
    mockRepo.AssertExpectations(t)
}
```

### Flutter

```dart
// Widget test
testWidgets('ProductCard menampilkan nama dan harga', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      child: MaterialApp(home: ProductCard(product: mockProduct)),
    ),
  );
  
  expect(find.text('Kopi Susu'), findsOneWidget);
  expect(find.text('Rp 25.000'), findsOneWidget);
});
```

---

## 🚀 Deployment

### Environment

| Env | Branch | URL |
|-----|--------|-----|
| Development | local | localhost |
| Staging | `staging` | api-staging.xynpos.com |
| Production | `main` | api.xynpos.com |

**TIDAK BOLEH** push langsung ke `main`. Semua harus via PR dengan review.

### CI/CD

CI/CD via GitHub Actions. Setiap push ke branch akan:
1. Run linter + tests
2. Check coverage (minimum 70%)
3. Build Docker image
4. Deploy ke staging (untuk branch `staging`)
5. Deploy ke production (untuk branch `main`, setelah approval)

---

## 📦 Dependency Management

### Go

```bash
# Tambah dependency
go get github.com/some/package@v1.2.3

# Update semua
go get -u ./...

# Security audit
govulncheck ./...
```

### Flutter

```bash
# Tambah dependency di pubspec.yaml, lalu:
flutter pub get

# Upgrade
flutter pub upgrade

# Audit
flutter pub audit
```

### Node.js

```bash
# Selalu pakai pnpm (bukan npm atau yarn)
pnpm add package-name
pnpm audit
```

---

## 🔑 Local Development Setup

```bash
# 1. Clone repo
git clone https://github.com/extendedsynaptic/xynpos.git
cd xynpos

# 2. Copy env templates
cp .env.example .env.local
cp backend/services/pos-service/.env.example backend/services/pos-service/.env.local

# 3. Jalankan infrastruktur lokal
make docker-up

# 4. Tunggu semua service healthy, lalu jalankan migration
make migrate-up

# 5. Jalankan service yang mau di-develop
make be-pos

# 6. Jalankan frontend
cd frontend/apps/web-dashboard && pnpm dev
```

---

## 📚 Referensi Blueprint

| Blueprint | File |
|-----------|------|
| Target Market | `01-target-market-competitive-analysis.md` |
| Financial & Pricing | `02-financial-subscription-mechanism.md` |
| MVP Features | `03-mvp-features-blueprint.md` |
| Post-MVP Roadmap | `04-post-mvp-advanced-features.md` |
| Tech Stack | `05-tech-stack-blueprint.md` |
| System Architecture | `06-system-architecture-blueprint.md` |
| Project Structure | `07-project-structure-blueprint.md` |
| Database Schema | `08-database-schema-blueprint.md` |
| Infrastructure/DevOps | `09-infrastructure-devops-blueprint.md` |
| Security | `10-security-blueprint.md` |
| API Design | `11-api-design-blueprint.md` |
| Mobile App | `12-mobile-app-blueprint.md` |
| Testing Strategy | `14-testing-strategy-blueprint.md` |
| GTM & Launch | `15-gtm-launch-blueprint.md` |
| Legal & Compliance | `16-legal-compliance-blueprint.md` |

---

## ❓ FAQ

**Q: Di mana saya bisa lihat semua API endpoint?**
A: Swagger UI di `http://localhost:8000/docs` (saat dev), atau lihat BP-11.

**Q: Bagaimana cara tambah service baru?**
A: Copy structure dari service yang sudah ada, update `docker-compose.yml` dan Kong config.

**Q: Bagaimana cara debug offline sync?**
A: Di Flutter, cek Hive box `pending_transactions`. Di web, cek IndexedDB di DevTools.

**Q: Apa yang harus diperhatikan saat bikin query database?**
A: (1) Selalu via GORM. (2) Pastikan search_path sudah di-set via middleware. (3) Pakai read replica untuk report. (4) Jangan SELECT *.

**Q: Bagaimana cara test webhook payment gateway?**
A: Gunakan Xendit/Midtrans sandbox + ngrok untuk expose localhost ke internet.

---

*XynPOS — Extended Synaptic | CLAUDE.md v1.0*
