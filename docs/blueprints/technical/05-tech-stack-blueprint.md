# XynPOS — Blueprint 05: Tech Stack Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Prinsip Pemilihan Tech Stack

| Prinsip | Penjelasan |
|---------|-----------|
| **Performance First** | Golang untuk BE — concurrency tinggi, memory efficient |
| **Cross-Platform Mobile** | Flutter — 1 codebase untuk iOS & Android |
| **Developer Productivity** | Tools dengan DX (Developer Experience) terbaik |
| **Vendor Pragmatism** | Managed services > self-host untuk infrastruktur non-core |
| **Indonesia-First** | Storage di region Asia, payment gateway lokal |
| **Cost-Aware** | Mulai kecil, scale dengan arsitektur yang bisa grow |
| **Security by Default** | JWT, mTLS, encryption di setiap layer |

---

## 2. Backend (BE) — Golang Microservices

### 2.1 Language & Runtime

| Komponen | Pilihan | Versi | Alasan |
|----------|---------|-------|--------|
| **Language** | Go (Golang) | 1.22+ | Performance tinggi, concurrency built-in, binary kecil |
| **Framework HTTP** | Fiber v2 | v2.52+ | Express-like, fastest Go framework (built on fasthttp) |
| **Alternative HTTP** | Chi Router | v5 | Untuk service yang butuh net/http compatibility |
| **gRPC** | google.golang.org/grpc | v1.64+ | Komunikasi antar microservice internal |
| **Protobuf** | Protocol Buffers | v3 | Contract-first API definition |

### 2.2 Microservice Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway (Kong)                    │
└─────────────┬───────────┬───────────┬───────────────────┘
              │           │           │
    ┌─────────▼──┐ ┌──────▼──┐ ┌─────▼──────┐
    │ Auth Svc   │ │ POS Svc │ │ Product Svc│
    │ (Go+Fiber) │ │ (Go)    │ │ (Go)       │
    └─────────┬──┘ └──────┬──┘ └─────┬──────┘
              │           │          │
    ┌─────────▼──┐ ┌──────▼──┐ ┌─────▼──────┐
    │ Payment Svc│ │ Report  │ │ Notify Svc │
    │ (Go)       │ │ Svc(Go) │ │ (Go)       │
    └────────────┘ └─────────┘ └────────────┘
```

### 2.3 Key Libraries per Service

| Library | Tujuan | Package |
|---------|--------|---------|
| **GORM** | ORM untuk PostgreSQL | gorm.io/gorm |
| **golang-migrate** | Database migration | github.com/golang-migrate/migrate |
| **go-redis** | Redis client | github.com/redis/go-redis |
| **viper** | Config management | github.com/spf13/viper |
| **zap** | Structured logging | go.uber.org/zap |
| **validator** | Request validation | github.com/go-playground/validator |
| **jwt-go** | JWT auth | github.com/golang-jwt/jwt |
| **swaggo** | Swagger doc gen | github.com/swaggo/swag |
| **testify** | Testing assertion | github.com/stretchr/testify |
| **mockery** | Mock generation | github.com/vektra/mockery |
| **cobra** | CLI tools | github.com/spf13/cobra |
| **cron** | Scheduled jobs | github.com/robfig/cron |
| **prometheus** | Metrics | github.com/prometheus/client_golang |
| **otelgo** | OpenTelemetry tracing | go.opentelemetry.io/otel |
| **urfave/negroni** | Middleware | (via Fiber middleware) |
| **goose** | DB Migration alt | pressly/goose |

### 2.4 Microservice List & Responsibility

| Service | Port | Fungsi Utama | Database |
|---------|------|--------------|---------|
| `auth-service` | 8001 | Registrasi, login, JWT, refresh token, OAuth | PostgreSQL + Redis |
| `tenant-service` | 8002 | Manajemen tenant, outlet, subscription status | PostgreSQL |
| `product-service` | 8003 | CRUD produk, kategori, variant, modifier | PostgreSQL |
| `inventory-service` | 8004 | Stok, movement, adjustment, PO, stocktake | PostgreSQL |
| `pos-service` | 8005 | Transaksi penjualan, cart, order | PostgreSQL + Redis |
| `payment-service` | 8006 | Payment gateway integrasi, webhook | PostgreSQL |
| `customer-service` | 8007 | CRM dasar, loyalty poin, hutang | PostgreSQL |
| `report-service` | 8008 | Laporan, analytics, export | PostgreSQL (read replica) |
| `notification-service` | 8009 | Push notif, email, WhatsApp | Redis queue |
| `file-service` | 8010 | Upload gambar, S3/R2 management | S3 compatible |
| `subscription-service` | 8011 | Billing, plan management, invoice | PostgreSQL |
| `audit-service` | 8012 | Audit log, activity tracking | PostgreSQL / ClickHouse |

---

## 3. API Gateway

| Komponen | Pilihan | Alasan |
|----------|---------|--------|
| **Primary** | **Kong Gateway** (open source) | Plugin ekosistem kaya, mature, production-proven |
| **Alternative** | Traefik | Lebih ringan, native Kubernetes |
| **Development** | Nginx (simple) | Untuk development environment |

**Plugin Kong yang digunakan:**
- Rate limiting (per tenant, per plan)
- JWT authentication
- Request transformation
- Logging → Grafana
- CORS
- IP whitelisting (untuk admin)
- Circuit breaker

---

## 4. Frontend Web (Web POS & Dashboard)

### 4.1 Framework & Language

| Komponen | Pilihan | Versi | Alasan |
|----------|---------|-------|--------|
| **Framework** | **Next.js** | 14+ (App Router) | SSR/SSG hybrid, React ecosystem, great DX |
| **Language** | TypeScript | 5+ | Type safety, better DX, catch errors early |
| **Styling** | Tailwind CSS | v3 | Utility-first, consistent design system |
| **UI Components** | **shadcn/ui** | Latest | Accessible, customizable, not a lib dependency |
| **Charts** | Recharts + Tremor | Latest | React-native charts, business dashboard ready |
| **State Management** | Zustand | v4 | Lightweight, simple, no boilerplate |
| **Server State** | TanStack Query (React Query) | v5 | Cache, sync, background updates |
| **Forms** | React Hook Form + Zod | Latest | Performance, validation, TypeScript integration |
| **Animation** | Framer Motion | v11 | Smooth UI transitions |
| **Tables** | TanStack Table | v8 | Headless, powerful data tables |
| **Icons** | Lucide React | Latest | Consistent, customizable icons |

### 4.2 Web POS Specific

| Komponen | Library | Kegunaan |
|----------|---------|---------|
| Barcode Scanner | html5-qrcode | Scan via webcam |
| Print | qz-tray | USB printer dari browser |
| Offline Storage | Dexie.js (IndexedDB) | Offline transaction storage |
| PWA | next-pwa | Installable, offline-ready |
| WebSocket | Socket.io-client | Real-time kitchen display |
| Virtual Keyboard | react-simple-keyboard | Touch-optimized numpad |

### 4.3 Build & Tooling

| Tool | Pilihan | Kegunaan |
|------|---------|---------|
| Package Manager | pnpm | Faster, disk efficient |
| Bundler | Turbopack (via Next.js) | Fast builds |
| Linting | ESLint + Prettier | Code quality |
| Testing | Vitest + Testing Library | Unit + integration |
| E2E Testing | Playwright | Cross-browser E2E |
| Storybook | Storybook 8 | Component development |

---

## 5. Mobile App (iOS & Android)

### 5.1 Framework

| Komponen | Pilihan | Alasan |
|----------|---------|--------|
| **Framework** | **Flutter** | Dart, 1 codebase iOS+Android, native performance, kaya widget |
| **Language** | Dart | 3.0+ dengan null safety |
| **State Management** | **Riverpod** (Riverpod 2 + Hooks) | Type-safe, testable, no context hell |
| **Navigation** | go_router | Declarative routing, deep link support |
| **HTTP Client** | Dio | Interceptors, retry, cancellation |
| **Local DB** | **Hive** (offline) + **sqflite** | Hive: fast key-value, sqflite: relational offline |
| **Background Sync** | workmanager | Background tasks sync |
| **Push Notification** | Firebase Cloud Messaging (FCM) | iOS + Android unified |
| **Bluetooth Printer** | flutter_bluetooth_printer | Thermal printer BT |
| **Barcode Scanner** | mobile_scanner | Fast camera barcode scan |
| **Camera** | image_picker | Foto produk |

### 5.2 Flutter Packages Utama

| Package | Kegunaan |
|---------|---------|
| `flutter_riverpod` | State management |
| `go_router` | Navigation |
| `dio` | HTTP client |
| `hive_flutter` | Offline storage (key-value) |
| `sqflite` | Offline SQLite |
| `firebase_core` + `firebase_auth` | Auth |
| `firebase_messaging` | Push notifications |
| `mobile_scanner` | QR & barcode |
| `flutter_bluetooth_printer` | Bluetooth thermal print |
| `image_picker` | Camera/gallery |
| `cached_network_image` | Image caching |
| `flutter_secure_storage` | Simpan token aman |
| `intl` | Format currency, date, localization |
| `freezed` | Immutable data classes |
| `json_serializable` | JSON serialization |
| `retrofit` | Type-safe HTTP (Dio wrapper) |
| `connectivity_plus` | Cek koneksi internet |
| `workmanager` | Background sync job |
| `fl_chart` | Charts di mobile dashboard |
| `flutter_local_notifications` | Local push notifications |
| `permission_handler` | Runtime permissions |
| `share_plus` | Share struk digital |
| `url_launcher` | Buka link external |

---

## 6. Database

### 6.1 Primary Database

| Komponen | Pilihan | Versi | Alasan |
|----------|---------|-------|--------|
| **Relational** | **PostgreSQL** | 16+ | ACID, JSON support, Row Level Security (multi-tenant), mature |
| **Multi-tenant Strategy** | **Schema per tenant** (medium scale) → Row-level (large scale) | Isolasi baik, manageable |
| **Connection Pooling** | **PgBouncer** | Latest | Reduce connection overhead |

### 6.2 Caching & Session

| Komponen | Pilihan | Kegunaan |
|----------|---------|---------|
| **In-memory Cache** | **Redis** 7+ | Session, JWT blacklist, rate limit counter, Pub/Sub |
| **Redis Mode** | Sentinel (HA) → Cluster (large scale) | High availability |

### 6.3 Search Engine

| Komponen | Pilihan | Kegunaan |
|----------|---------|---------|
| **Full-text Search** | **Meilisearch** | Cari produk di kasir (fast, typo-tolerant) |
| **Alternative** | PostgreSQL FTS | Untuk search sederhana di awal |

### 6.4 Analytics Database

| Komponen | Pilihan | Kegunaan |
|----------|---------|---------|
| **OLAP** | **ClickHouse** (Phase 2+) | Analytics query cepat, laporan besar |
| **Alternative Phase 1** | PostgreSQL read replica | Cukup untuk 0–5000 tenant |

### 6.5 Message Queue

| Komponen | Pilihan | Kegunaan |
|----------|---------|---------|
| **Queue** | **NATS** (Phase 1) → **Kafka** (Phase 2+) | Event streaming, async microservice |
| **Task Queue** | **Asynq** (Go + Redis) | Background jobs, scheduled tasks |

---

## 7. Cloud Infrastructure

### 7.1 Cloud Provider Strategy

| Phase | Provider | Alasan |
|-------|----------|--------|
| **Phase 1** (0–500 tenant) | **DigitalOcean** | Cost-effective, simple, great managed services |
| **Phase 2** (500–10K tenant) | **DigitalOcean + Cloudflare** | Scale up DO, CDN Cloudflare |
| **Phase 3** (10K+ tenant) | **AWS (ap-southeast-1 Singapore)** atau **GCP** | Enterprise grade, compliance, global |

### 7.2 Region Strategy

| Region | Tujuan |
|--------|--------|
| **Jakarta (DigitalOcean SGP1/BLR1)** | Primary: Semua user Indonesia |
| **Singapore (backup)** | Disaster recovery, enterprise compliance |
| **Global CDN** | Cloudflare edge: assets, static files |

### 7.3 Compute

| Komponen | Phase 1 | Phase 2 | Phase 3 |
|----------|---------|---------|---------|
| App Servers | 2x VPS 4vCPU/8GB | Kubernetes 3-node | K8s multi-node auto-scale |
| Database | DO Managed PG | DO Managed PG HA | RDS Aurora |
| Cache | DO Managed Redis | DO Managed Redis HA | Elasticache |
| Load Balancer | DO LB | DO LB | AWS ALB |

---

## 8. Object Storage (S3 Compatible)

| Komponen | Pilihan | Alasan |
|----------|---------|--------|
| **Phase 1** | **Cloudflare R2** | S3-compatible, NO egress fee, sangat cost-effective |
| **Phase 2+** | Cloudflare R2 + backup ke DO Spaces | Redundancy |
| **Enterprise** | AWS S3 (jika sudah di AWS) | Native integration |

**Penggunaan:**
- Foto produk (max 2MB per gambar)
- Logo bisnis tenant
- Export PDF/Excel laporan
- Backup database
- Invoice dan struk digital

---

## 9. Email Service

| Komponen | Pilihan | Tier | Alasan |
|----------|---------|------|--------|
| **Primary** | **Resend** | Free: 3K email/bln, Pro: $20/100K | Developer-friendly, React Email, great deliverability |
| **Transactional** | **Mailgun** (backup) | $15/50K | Backup & SMS |
| **Template Engine** | React Email | — | TypeScript email templates, preview in browser |
| **Bulk/Marketing** | (Wave 5) | — | Integrasi XYN CRM marketing |

**Email yang dikirim:**
- Welcome email + verifikasi
- Reset password
- Invoice subscription
- Alert stok habis
- Laporan harian/mingguan (opsional)
- Notifikasi payment sukses/gagal

---

## 10. Firebase

| Firebase Service | Kegunaan | Platform |
|-----------------|---------|---------|
| **Firebase Auth** | Google Sign-In OAuth | Mobile + Web |
| **Firebase Cloud Messaging (FCM)** | Push notification iOS + Android | Mobile |
| **Firebase Analytics** | User behavior analytics | Mobile (optional) |
| **Firebase Crashlytics** | Crash reporting mobile | Mobile |
| **Firebase Remote Config** | Feature flags, A/B test tanpa update app | Mobile |
| **Firebase App Distribution** | Distribute beta builds ke tester | Dev/Staging |

> **Catatan:** Auth utama tetap di backend (JWT + PostgreSQL). Firebase Auth digunakan untuk OAuth flow dan push notification token management.

---

## 11. DevOps & Infrastructure as Code

| Komponen | Pilihan | Kegunaan |
|----------|---------|---------|
| **Containerization** | **Docker** + Docker Compose | Semua service |
| **Orchestration** | **Kubernetes** (K8s) via DOKS | Phase 2+ |
| **CI/CD** | **GitHub Actions** | Build, test, deploy pipeline |
| **IaC** | **Terraform** | Provisioning cloud resources |
| **Container Registry** | **GitHub Container Registry (GHCR)** | Free dengan GitHub |
| **Config Management** | **HashiCorp Vault** (Phase 2) | Secret management |
| **Environment Config** | **Doppler** (Phase 1) | Simple secret management |

---

## 12. Monitoring & Observability

| Komponen | Pilihan | Kegunaan |
|----------|---------|---------|
| **Metrics** | **Prometheus** + **Grafana** | System metrics, custom dashboards |
| **Logging** | **Loki** + Grafana | Log aggregation, structured search |
| **Tracing** | **Jaeger** / **Tempo** | Distributed tracing (microservice) |
| **APM** | **Sentry** | Error tracking, performance |
| **Uptime** | **Better Uptime** / UptimeRobot | External health check, incident alert |
| **Alert** | Grafana Alerting + PagerDuty | On-call incident management |
| **Dashboard** | Grafana | Single pane of glass |

---

## 13. Security Stack

| Komponen | Pilihan | Kegunaan |
|----------|---------|---------|
| **WAF** | Cloudflare WAF | DDoS, bot protection |
| **Secret Scanning** | Doppler / Vault | Prevent leaked secrets |
| **SAST** | SonarQube / golangci-lint | Static analysis |
| **Dependency Scan** | Snyk / govulncheck | CVE scanning |
| **SSL/TLS** | Cloudflare (wildcard) | *.xynpos.com |
| **mTLS** | (Phase 2) | Service-to-service auth |

---

## 14. Development Tools

| Tool | Pilihan | Kegunaan |
|------|---------|---------|
| **Version Control** | GitHub | Repository, PR, CI/CD |
| **Project Management** | Linear / Notion | Sprint planning |
| **API Testing** | **Bruno** (API client) / Postman | Test API lokal |
| **DB Management** | TablePlus / DBeaver | Manage PostgreSQL |
| **API Documentation** | Swagger UI (auto dari swaggo) | Live docs |
| **Design** | Figma | UI/UX design |
| **Communication** | Discord (team) | Dev communication |
| **Code Quality** | golangci-lint + ESLint | Linting |
| **Pre-commit** | Husky + lint-staged | Auto lint sebelum commit |

---

## 15. Tech Stack Summary Table

```
┌─────────────────────────────────────────────────────────────┐
│                    XYNPOS TECH STACK                        │
├─────────────────┬───────────────────────────────────────────┤
│ BACKEND         │ Go 1.22 · Fiber v2 · gRPC · GORM         │
│ API GATEWAY     │ Kong Gateway                              │
│ WEB FRONTEND    │ Next.js 14 · TypeScript · Tailwind · shadcn│
│ MOBILE          │ Flutter 3 · Dart · Riverpod · go_router   │
│ DATABASE        │ PostgreSQL 16 · Redis 7 · Meilisearch     │
│ ANALYTICS DB    │ ClickHouse (Phase 2+)                     │
│ QUEUE           │ NATS → Kafka (Phase 2+) · Asynq           │
│ CLOUD           │ DigitalOcean → AWS (Phase 3)              │
│ STORAGE         │ Cloudflare R2 (S3-compatible)             │
│ CDN             │ Cloudflare                                │
│ EMAIL           │ Resend · React Email                      │
│ PUSH NOTIF      │ Firebase FCM                              │
│ AUTH OAUTH      │ Firebase Auth                             │
│ MONITORING      │ Prometheus · Grafana · Loki · Sentry      │
│ CI/CD           │ GitHub Actions                            │
│ CONTAINER       │ Docker · Kubernetes (Phase 2+)            │
│ IaC             │ Terraform                                 │
│ SECURITY        │ Cloudflare WAF · Doppler/Vault            │
└─────────────────┴───────────────────────────────────────────┘
```

---

*Blueprint ini inline dengan: BP-06 (Architecture), BP-07 (Project Structure), BP-09 (Infrastructure)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
