# XynPOS — Blueprint 19: Developer Onboarding Guide
> Extended Synaptic | Version 1.0 | New Developer Reference

---

## Selamat Datang di Tim XynPOS! 👋

Dokumen ini adalah panduan lengkap untuk developer baru yang bergabung ke tim Extended Synaptic. Setelah selesai membaca dan mengikuti langkah di sini, kamu akan:

- Paham visi dan arsitektur XynPOS
- Bisa menjalankan seluruh environment lokal
- Tahu konvensi kode yang dipakai tim
- Siap mengerjakan task pertama

**Estimasi waktu:** 4–8 jam untuk setup lengkap (tergantung kecepatan internet dan spesifikasi laptop)

---

## 1. Baca Dulu Sebelum Mulai

Sebelum setup environment, luangkan waktu membaca blueprint berikut **secara berurutan**. Ini investasi waktu yang akan menghemat banyak pertanyaan nantinya:

| Urutan | Dokumen | Fokus Utama |
|--------|---------|-------------|
| 1 | `00-MASTER-INDEX.md` | Gambaran besar semua blueprint |
| 2 | `03-mvp-features-blueprint.md` | Apa yang sedang dibangun |
| 3 | `05-tech-stack-blueprint.md` | Tools dan library yang dipakai |
| 4 | `06-system-architecture-blueprint.md` | Bagaimana sistem bekerja |
| 5 | `07-project-structure-blueprint.md` | Struktur folder dan file |
| 6 | `08-database-schema-blueprint.md` | Skema database |
| 7 | `13-CLAUDE-ai-instructions.md` | Dev rules dan konvensi harian |

---

## 2. Prerequisites

### Wajib Diinstal

```bash
# Cek versi minimum yang dibutuhkan:

go version          # >= 1.22
node --version      # >= 20.x
pnpm --version      # >= 8.x
flutter --version   # >= 3.22
dart --version      # >= 3.4
docker --version    # >= 25.x
docker compose version # >= 2.x
git --version       # >= 2.40

# Tools tambahan
make --version
curl --version
```

### Install jika belum ada

```bash
# Go
# https://go.dev/doc/install
wget https://go.dev/dl/go1.22.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.22.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin  # tambahkan ke ~/.bashrc atau ~/.zshrc

# Node.js via nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install 20
nvm use 20

# pnpm
npm install -g pnpm

# Flutter
# https://docs.flutter.dev/get-started/install
# Ikuti instruksi sesuai OS kamu

# golangci-lint
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | \
  sh -s -- -b $(go env GOPATH)/bin v1.58.0

# golang-migrate
go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest

# mockery (Go mock generator)
go install github.com/vektra/mockery/v2@latest

# swag (Swagger doc generator)
go install github.com/swaggo/swag/cmd/swag@latest
```

### IDE Setup (Rekomendasi: VS Code atau GoLand)

```bash
# VS Code Extensions yang wajib:
# - Go (golang.go)
# - Flutter (Dart-Code.flutter)
# - ESLint (dbaeumer.vscode-eslint)
# - Tailwind CSS IntelliSense
# - Prettier
# - GitLens
# - REST Client (untuk test API)
# - Docker
# - Error Lens

# VS Code Settings (tambahkan ke settings.json):
{
  "go.useLanguageServer": true,
  "go.lintTool": "golangci-lint",
  "go.lintOnSave": "workspace",
  "go.formatTool": "goimports",
  "editor.formatOnSave": true,
  "[go]": {
    "editor.defaultFormatter": "golang.go"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[dart]": {
    "editor.formatOnSave": true,
    "editor.selectionHighlight": false,
    "editor.suggest.snippetsPreventQuickSuggestions": false,
    "editor.suggestSelection": "first",
    "editor.tabCompletion": "onlySnippets",
    "editor.wordBasedSuggestions": "off"
  }
}
```

---

## 3. Akses yang Dibutuhkan

Minta ke founder/lead developer untuk akses berikut:

```
Checklist akses baru:
[ ] GitHub — invite ke org extendedsynaptic, repo XynPOS
[ ] Doppler — invite ke project xynpos-development
[ ] DigitalOcean — read-only access (atau staging access)
[ ] Sentry — invite ke project xynpos
[ ] Grafana — read-only dashboard access
[ ] Notion/Linear — project management
[ ] Slack/Discord — channel #engineering #general #incidents
[ ] Google Workspace — email @extendedsynaptic.com
```

---

## 4. Clone & Setup Repository

```bash
# 1. Clone monorepo
git clone https://github.com/extendedsynaptic/xynpos.git
cd xynpos

# 2. Setup Git hooks (husky untuk pre-commit lint)
# Sudah otomatis saat npm install di root

# 3. Copy environment files
cp .env.example .env.local

# Untuk setiap service backend:
for service in backend/services/*/; do
  if [ -f "$service/.env.example" ]; then
    cp "$service/.env.example" "$service/.env.local"
    echo "Copied .env for $service"
  fi
done

# 4. Isi .env.local dengan nilai dari Doppler
# Cara dapat nilai: tanya ke lead developer atau:
doppler setup --project xynpos --config dev
doppler secrets download --no-file --format env > .env.local
```

---

## 5. Setup Local Development Environment

### 5.1 Start Infrastructure

```bash
# Start semua infrastruktur lokal (postgres, redis, nats, meilisearch)
make docker-up

# Tunggu sampai semua healthy (30-60 detik)
docker ps --format "table {{.Names}}\t{{.Status}}"

# Output yang diharapkan:
# xynpos-postgres     Up (healthy)
# xynpos-redis        Up (healthy)
# xynpos-nats         Up
# xynpos-meilisearch  Up
```

### 5.2 Setup Database

```bash
# Create global schema dan seed data
make db-setup

# Atau manual:
# 1. Connect ke postgres
docker exec -it xynpos-postgres psql -U xynpos -d xynpos

# 2. Create global schema
\i backend/scripts/init-global-schema.sql

# 3. Create development tenant
\i backend/scripts/seed-dev-tenant.sql

# 4. Exit
\q

# 5. Jalankan migration untuk dev tenant
make migrate-up TENANT=tenant_dev001
```

### 5.3 Verify Setup

```bash
# Test koneksi database
docker exec xynpos-postgres psql -U xynpos -d xynpos -c \
  "SELECT name FROM public_xyn.tenants;"

# Test Redis
docker exec xynpos-redis redis-cli -a devpassword ping
# Output: PONG

# Test NATS
curl http://localhost:8222/varz | python3 -c "import sys,json; d=json.load(sys.stdin); print('NATS OK:', d['version'])"
```

### 5.4 Start Backend Services

```bash
# Option A: Jalankan semua via Docker Compose
make docker-up-all

# Option B: Jalankan service spesifik (untuk development aktif)
# Terminal 1: Auth service
make be-auth

# Terminal 2: POS service
make be-pos

# Terminal 3: Product service
make be-product

# Verify semua service berjalan
curl http://localhost:8001/health  # Auth
curl http://localhost:8005/health  # POS
curl http://localhost:8003/health  # Product
```

### 5.5 Start Frontend

```bash
# Install dependencies
cd frontend
pnpm install

# Start web dashboard
cd apps/web-dashboard
pnpm dev
# Buka: http://localhost:3000

# Start web POS (terminal lain)
cd apps/web-pos
pnpm dev
# Buka: http://localhost:3001
```

### 5.6 Setup Mobile (Opsional untuk backend dev)

```bash
cd mobile/xynpos_mobile

# Install dependencies
flutter pub get

# Check setup
flutter doctor

# Run di emulator/device
flutter run

# Jika belum ada emulator:
# Android: Android Studio → AVD Manager → Create Virtual Device
# iOS: Xcode → Open Simulator (macOS only)
```

---

## 6. First-Time Verification: End-to-End Test

Setelah semua berjalan, lakukan test manual sederhana:

```bash
# 1. Register tenant baru
curl -X POST http://localhost:8001/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@mybusiness.com",
    "password": "Test1234!",
    "name": "Test User",
    "business_name": "My Test Café"
  }'

# Simpan token dari response

# 2. Login
curl -X POST http://localhost:8001/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@mybusiness.com", "password": "Test1234!"}'

# Simpan access_token

# 3. Buat produk
curl -X POST http://localhost:8000/v1/products \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kopi Susu",
    "selling_price": 25000,
    "category_id": "<category_id>"
  }'

# Jika semua berhasil → setup lokal berjalan dengan baik ✅
```

---

## 7. Development Workflow

### 7.1 Git Branching Strategy

```
main          ← Production, always deployable
staging       ← Pre-production, auto-deploy ke staging server
dev           ← Integration branch (opsional)
feature/*     ← Feature branch dari main atau staging
bugfix/*      ← Bug fix branch
hotfix/*      ← Critical fix untuk production
```

```bash
# Cara buat feature branch
git checkout staging
git pull origin staging
git checkout -b feature/pos-hold-order

# Setelah selesai
git push origin feature/pos-hold-order
# Buat Pull Request ke staging di GitHub
```

### 7.2 Commit Message Convention

Format: `type(scope): description`

```
type:
  feat     = Fitur baru
  fix      = Bug fix
  refactor = Refactoring tanpa perubahan fungsional
  test     = Tambah atau update test
  docs     = Update dokumentasi
  chore    = Maintenance, dependency update
  perf     = Performance improvement

scope: (opsional) nama service atau module
  auth, pos, product, inventory, payment, mobile, web, infra

Contoh:
  feat(pos): add hold order functionality
  fix(auth): refresh token not rotating on reuse
  test(product): add unit tests for variant usecase
  docs: update API design blueprint
  chore(deps): upgrade fiber to v2.52.4
```

### 7.3 Code Review Process

```
PR Requirements sebelum merge ke staging:
✓ CI/CD pass (lint + test + coverage)
✓ Self-review checklist (lihat PR template)
✓ Minimal 1 reviewer approve
✓ Semua comment resolved
✓ Tidak ada TODO yang belum di-address

PR Template akan otomatis muncul saat buat PR di GitHub.
Isi semua bagian — jangan dikosongkan.
```

### 7.4 Daily Development Loop

```
1. Morning:
   - Pull latest dari staging
   - Cek Jira/Linear board — ambil task
   - Buat branch dari staging

2. During work:
   - Commit sering (small commits, easier to review)
   - Jalankan test lokal sebelum push
   - Gunakan `make be-test` atau `go test ./...`

3. Sebelum PR:
   - `make be-lint` — pastikan tidak ada lint error
   - `go test ./... -cover` — cek coverage
   - Update swagger jika ada perubahan API: `make be-swagger SVC=pos-service`
   - Self-review diff di GitHub sebelum request review
```

---

## 8. Tools & Debugging

### 8.1 Database GUI

```bash
# TablePlus (rekomendasi, ada trial gratis)
# Connection string:
Host: localhost
Port: 5432
Database: xynpos
Username: xynpos
Password: (dari .env.local)

# Untuk lihat tenant schema, ubah search_path:
# Di TablePlus: klik nama koneksi → Edit → Initial SQL:
SET search_path = tenant_dev001;
```

### 8.2 API Testing

```bash
# Bruno (rekomendasi, free & open source):
# Install: https://www.usebruno.com/

# Import collection dari:
docs/api/bruno-collection/

# Atau gunakan REST Client di VS Code:
# File: docs/api/requests.http
```

### 8.3 Melihat Logs

```bash
# Docker logs (local)
docker logs xynpos-pos-service -f --tail 100

# Semua service sekaligus
docker-compose logs -f 2>&1 | grep -v "health check"

# Filter error saja
docker-compose logs -f 2>&1 | grep -i "error\|fatal\|panic"
```

### 8.4 Debugging Go Service

```bash
# Jalankan dengan debug output
LOG_LEVEL=debug go run ./cmd/main.go

# Delve debugger (attach ke running process)
dlv attach $(pgrep pos-service)

# VS Code: sudah ada launch.json di .vscode/
# F5 → pilih "Debug pos-service"
```

### 8.5 Database Debugging

```bash
# Connect ke tenant schema
docker exec -it xynpos-postgres psql -U xynpos -d xynpos \
  -c "SET search_path = tenant_dev001;" \
  -c "\dt"  # list semua tabel

# EXPLAIN ANALYZE untuk debug query lambat
docker exec -it xynpos-postgres psql -U xynpos -d xynpos <<EOF
SET search_path = tenant_dev001;
EXPLAIN ANALYZE SELECT * FROM transactions 
WHERE outlet_id = 'uuid' 
AND created_at > NOW() - INTERVAL '30 days';
EOF
```

---

## 9. FAQ Developer

**Q: Import path Go yang benar itu apa?**
A: `github.com/extendedsynaptic/xynpos/{service-name}/internal/...`

**Q: Kenapa ada 2 database connection di setiap service?**
A: Primary (read-write) dan read replica (read-only untuk query laporan). Selalu pakai primary untuk write, replica untuk read-heavy queries.

**Q: Saya ubah schema tapi tidak terreflect?**
A: Jalankan `make migrate-up TENANT=tenant_dev001`. Jika sudah ada migration version yang sama, perlu buat migration baru.

**Q: Flutter app tidak bisa hit API lokal?**
A: Untuk emulator Android, gunakan `10.0.2.2` bukan `localhost`. Sudah ada di `core/constants/api_constants.dart` untuk flavor `dev`.

**Q: Test saya pass lokal tapi fail di CI?**
A: Kemungkinan besar race condition atau test tidak cleanup state. Gunakan `t.Parallel()` hanya jika test benar-benar independen. Cek juga bahwa test DB di-reset antar test.

**Q: Bagaimana cara test webhook payment gateway?**
A: Gunakan `ngrok http 8006` untuk expose port lokal, lalu daftarkan URL ngrok ke Xendit/Midtrans sandbox dashboard sebagai webhook URL.

**Q: Saya perlu fitur yang belum ada di blueprint, bagaimana?**
A: Diskusikan dulu di Slack #engineering. Jika disetujui, buat tiket di Linear dan update blueprint yang relevan sebelum mulai coding.

---

## 10. Escalation & Help

| Butuh Bantuan | Tanya Siapa | Channel |
|---------------|------------|---------|
| Code review, PR feedback | Lead Backend | GitHub PR atau Slack |
| Architecture decision | Founder/CTO | Slack #engineering |
| Access issue | Founder | WhatsApp/Slack |
| Infra/DevOps | Lead DevOps | Slack #infra |
| Product clarity | Product Owner | Slack #product |
| Emergency/Production | On-call dev | Slack #incidents + WA |

---

## 11. Checklist Onboarding Selesai

Tandai saat selesai:

```
Week 1:
[ ] Semua blueprint sudah dibaca (minimal BP-03, 05, 06, 07, 13)
[ ] Environment lokal berjalan (docker up + semua service healthy)
[ ] End-to-end test berhasil (register → login → buat produk → transaksi)
[ ] Paham git branching strategy
[ ] Akses semua tools (GitHub, Doppler, Sentry, dll) sudah ada
[ ] PR pertama dibuat (walau kecil — fix typo, improve docs, dll)

Week 2:
[ ] Mengerjakan task pertama (dari backlog sprint)
[ ] Code review pertama dari lead developer
[ ] Paham cara debug (log, delve, DB client)
[ ] Paham konvensi commit message
[ ] Join stand-up harian

Week 3-4:
[ ] Selesaikan 1 fitur lengkap (dari tiket sampai merge ke staging)
[ ] Ikut sprint planning dan retrospective
[ ] Berikan feedback tertulis untuk onboarding ini (kirim ke founder)
```

---

*Dokumen ini adalah living document — kalau ada yang kurang jelas atau langkah yang tidak work, update sekarang juga. Jangan tunggu orang lain yang update.*
*Last updated: 2025 | Extended Synaptic — XynPOS*
