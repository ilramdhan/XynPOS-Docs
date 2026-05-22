# XynPOS — Blueprint 17: Architecture Decision Records (ADR)
> Extended Synaptic | Version 1.0 | Living Document

---

## Apa itu ADR?

Architecture Decision Record adalah dokumen singkat yang mencatat **keputusan arsitektur penting** beserta konteks, alasan, dan konsekuensinya. Tujuannya: developer baru (atau diri sendiri 6 bulan kemudian) bisa paham *mengapa* sistem dibangun seperti ini, bukan hanya *apa* yang dibangun.

**Format tiap ADR:**
- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Konteks:** Situasi yang memaksa keputusan ini
- **Keputusan:** Apa yang diputuskan
- **Alasan:** Mengapa ini yang dipilih
- **Konsekuensi:** Trade-off yang diterima
- **Alternatif yang ditolak:** Opsi lain yang dipertimbangkan

**Cara membuat ADR baru:**
```bash
# Naming: ADR-{nomor}-{judul-singkat}.md
# Contoh: ADR-005-use-nats-instead-of-rabbitmq.md
# Simpan di: docs/adr/
```

---

## ADR-001: Pilih Go sebagai Backend Language

- **Status:** Accepted
- **Tanggal:** 2025

**Konteks:**
XynPOS membutuhkan backend yang bisa handle ribuan transaksi concurrent dari banyak tenant, dengan latency rendah. Tim kecil (1-3 developer), jadi produktivitas juga penting.

**Keputusan:** Menggunakan Go (Golang) 1.22+ untuk semua backend microservice.

**Alasan:**
- Concurrency built-in dengan goroutine — ideal untuk POS multi-tenant
- Binary tunggal, deploy sederhana, tidak butuh runtime (beda dari Node/Python)
- Memory footprint rendah dibanding Java/Node.js
- Performance sangat dekat C++ untuk workload I/O bound
- Standard library kuat (net/http, testing, crypto)
- Compile time error catching — lebih aman dari Python/JS
- Fiber v2 benchmark: salah satu framework HTTP tercepat

**Konsekuensi:**
- Learning curve lebih tinggi dari Node.js untuk developer yang belum kenal Go
- Ekosistem library lebih kecil dari NPM
- Generics baru tersedia di Go 1.18+ (bisa dipakai sekarang)

**Alternatif yang ditolak:**
- **Node.js/TypeScript:** Familiar, tapi event loop single-threaded kurang ideal untuk CPU-bound tasks. Memory usage lebih tinggi.
- **Python/FastAPI:** Bagus untuk prototyping, tapi GIL membatasi concurrency sejati.
- **Java/Spring:** Enterprise-grade tapi terlalu verbose dan heavy untuk tim kecil.
- **Rust:** Terlalu steep learning curve untuk tim kecil, produktivitas lebih rendah.

---

## ADR-002: Pilih Flutter untuk Mobile

- **Status:** Accepted
- **Tanggal:** 2025

**Konteks:**
XynPOS Mobile perlu berjalan di iOS dan Android dengan performa native, terutama untuk kasir yang transaksinya harus cepat. Tim kecil tidak bisa maintain dua codebase native terpisah.

**Keputusan:** Flutter 3 + Dart untuk semua mobile development.

**Alasan:**
- 1 codebase → iOS + Android, menghemat 50% development time
- Kompilasi ke native code (bukan interpreted) — 60fps konsisten
- Hot reload mempercepat development cycle
- Widget system sangat fleksibel untuk custom POS UI
- Dart null safety mencegah NPE yang umum di mobile
- Riverpod untuk state management yang type-safe dan testable
- Komunitas Indonesia untuk Flutter cukup besar

**Konsekuensi:**
- Dart bukan bahasa mainstream — lebih sulit cari developer
- Ukuran APK sedikit lebih besar dari native (tapi bisa dioptimasi)
- Akses fitur platform-specific (NFC, bluetooth) butuh plugin pihak ketiga

**Alternatif yang ditolak:**
- **React Native:** JavaScript bridge overhead, performa lebih rendah untuk animasi kompleks
- **Native iOS (Swift) + Android (Kotlin):** 2x development time, 2x bug surface
- **Ionic/Capacitor:** Web-based, performa tidak memadai untuk POS real-time

---

## ADR-003: Pilih Schema-per-Tenant untuk Multi-tenancy

- **Status:** Accepted (Phase 1), Review pada Phase 2
- **Tanggal:** 2025

**Konteks:**
XynPOS menyimpan data bisnis sensitif ribuan tenant. Isolasi data antar tenant adalah requirement kritis — kebocoran data tenant A ke tenant B adalah bencana bisnis dan legal.

**Keputusan:** Phase 1 menggunakan schema-per-tenant di PostgreSQL. Setiap tenant mendapat PostgreSQL schema sendiri (`tenant_{uuid}`).

**Alasan:**
- Isolasi data terkuat — tidak mungkin ada row-level bug menyebabkan data bocor antar tenant
- Backup per tenant mudah (`pg_dump -n tenant_abc123`)
- Migration per tenant terkontrol
- Tidak perlu Row Level Security yang kompleks
- `SET search_path = tenant_xyz` di connection → query otomatis terisolasi

**Konsekuensi:**
- Banyak schema saat tenant bertambah (manageable hingga ~10K schema per PostgreSQL)
- Migration harus dijalankan ke semua schema saat ada perubahan DDL
- Connection pool lebih kompleks (berbeda search_path per tenant)

**Alternatif yang ditolak:**
- **Row-level isolation (shared table + tenant_id):** Lebih scalable tapi risiko bug menyebabkan data bocor; butuh RLS yang ketat dan susah di-audit.
- **Database-per-tenant:** Isolasi paling kuat tapi operasional sangat kompleks (ribuan database).

**Review Trigger:** Akan direview dan mungkin migrasi ke row-level saat tenant aktif > 5.000 atau ada performance degradation signifikan.

---

## ADR-004: Pilih Monorepo untuk Repository Strategy

- **Status:** Accepted
- **Tanggal:** 2025

**Konteks:**
XynPOS terdiri dari backend Go (12 service), frontend Next.js (2 app), mobile Flutter, dan infrastruktur. Pertanyaan: satu repo atau multi-repo?

**Keputusan:** Monorepo — semua kode dalam satu repository GitHub.

**Alasan:**
- Tim kecil (2-5 orang) — overhead manajemen multi-repo tidak worth it
- Shared types dan contracts mudah di-share tanpa versioning overhead
- Atomic commit untuk perubahan yang span multiple service
- Single CI/CD pipeline lebih mudah di-maintain
- Refactoring cross-service lebih mudah
- Code review lebih mudah karena satu tempat

**Konsekuensi:**
- Clone repo lebih lama seiring bertambahnya kode
- Perlu disiplin dalam CI/CD — tidak semua service perlu deploy tiap ada perubahan
- Perlu path filtering di GitHub Actions agar tidak trigger build semua service

**Alternatif yang ditolak:**
- **Multi-repo (polyrepo):** Lebih independen per service tapi overhead versioning dependency antar service tinggi untuk tim kecil.
- **Nx/Turborepo:** Bisa dipakai tapi overkill untuk fase awal — tambahkan nanti jika monorepo sudah besar.

---

## ADR-005: Pilih NATS sebagai Message Broker (Phase 1)

- **Status:** Accepted
- **Tanggal:** 2025

**Konteks:**
Microservice XynPOS butuh komunikasi async antar service (contoh: POS service selesai transaksi → notify inventory, report, notification service). Butuh message broker yang ringan dan mudah di-setup untuk tim kecil.

**Keputusan:** NATS 2.x untuk Phase 1 (0-500 tenant). Akan dievaluasi Kafka untuk Phase 2.

**Alasan:**
- NATS sangat ringan — binary single ~20MB, tidak butuh ZooKeeper
- Latensi sangat rendah (sub-millisecond)
- Built-in persistence dengan JetStream
- Mudah di-setup via Docker satu command
- Go client library official dan mature
- Cukup untuk throughput Phase 1

**Konsekuensi:**
- NATS tidak se-battle-tested Kafka untuk high-throughput
- Ekosistem tools monitoring lebih kecil dari Kafka
- Perlu migration ke Kafka saat scale besar

**Review Trigger:** Evaluasi Kafka saat throughput message > 100K message/hari atau tenant > 5.000.

---

## ADR-006: Pilih Cloudflare R2 untuk Object Storage

- **Status:** Accepted
- **Tanggal:** 2025

**Konteks:**
XynPOS perlu menyimpan foto produk, logo bisnis, export PDF/Excel, dan backup. Butuh storage yang murah, reliabel, dan bisa diakses via CDN.

**Keputusan:** Cloudflare R2 sebagai primary object storage.

**Alasan:**
- **Zero egress fee** — tidak ada biaya bandwidth keluar (berbeda dengan AWS S3 yang charge $0.09/GB egress)
- S3-compatible API — bisa pakai AWS SDK yang sudah familiar
- Integrated dengan Cloudflare CDN — asset langsung terserve dari edge
- Harga storage kompetitif ($0.015/GB/bulan)
- Cloudflare sudah dipakai untuk WAF/CDN — one vendor untuk edge

**Konsekuensi:**
- Tidak se-mature AWS S3 dari sisi SLA dan fitur
- Region terbatas (tidak ada Jakarta-specific region, tapi Cloudflare edge dekat Indonesia)
- Tidak ada S3 event notifications (butuh polling atau webhook alternatif)

**Alternatif yang ditolak:**
- **AWS S3:** Lebih mature tapi egress fee sangat mahal untuk startup
- **DigitalOcean Spaces:** Lebih murah dari S3 tapi tidak ada zero-egress dan CDN terintegrasi lebih lemah
- **MinIO self-hosted:** Kontrol penuh tapi operasional burden tinggi

---

## ADR-007: Pilih JWT dengan Refresh Token Rotation

- **Status:** Accepted
- **Tanggal:** 2025

**Konteks:**
XynPOS butuh mekanisme autentikasi yang stateless (bisa scale horizontal) tapi tetap aman. Session-based auth butuh sticky session atau Redis session store yang lebih kompleks.

**Keputusan:** JWT access token (15 menit) + refresh token dengan rotation (30 hari), disimpan hash di Redis.

**Alasan:**
- Stateless access token — API Gateway bisa validate tanpa roundtrip ke auth service
- Short-lived access token (15 menit) — minimize window jika token dicuri
- Refresh token rotation — jika refresh token dicuri dan dipakai, original holder akan detect (reuse detection via token_family)
- Redis untuk revocation list — logout immediate tanpa tunggu expiry

**Konsekuensi:**
- Kompleksitas lebih tinggi dari session-based auth
- Butuh Redis sebagai dependency untuk refresh token storage
- Client harus implement refresh logic

**Alternatif yang ditolak:**
- **Long-lived JWT (24 jam):** Lebih simple tapi tidak bisa revoke — jika dicuri, attacker punya akses 24 jam
- **Session-based:** Simpler tapi butuh sticky session untuk scale horizontal
- **Opaque token:** Setiap API request harus roundtrip ke auth service untuk validasi

---

## ADR-008: Pilih Next.js App Router untuk Web Frontend

- **Status:** Accepted
- **Tanggal:** 2025

**Konteks:**
XynPOS Web terdiri dari 2 aplikasi: Web POS (kasir, full-screen, touch-optimized) dan Web Dashboard (laporan, manajemen). Butuh framework yang bisa SSR untuk SEO halaman marketing dan CSR untuk aplikasi dinamis.

**Keputusan:** Next.js 14 dengan App Router.

**Alasan:**
- Hybrid rendering — SSR untuk landing/auth pages, CSR untuk app
- App Router lebih modern dan performant dari Pages Router
- Server Components mengurangi JavaScript bundle ke client
- Built-in code splitting per route
- TypeScript support first-class
- shadcn/ui + Tailwind — design system yang produktif

**Konsekuensi:**
- App Router masih relatif baru — beberapa library belum fully compatible
- Learning curve dari Pages Router ke App Router
- Server Components model baru butuh adaptasi pola development

**Alternatif yang ditolak:**
- **React + Vite (SPA):** Lebih simple tapi tidak ada SSR untuk SEO dan initial load lebih lambat
- **Remix:** Bagus tapi ekosistem lebih kecil, shadcn/ui lebih erat dengan Next.js
- **SvelteKit:** Sangat bagus tapi komunitas lebih kecil, harder to hire

---

## Template ADR untuk Keputusan Baru

Saat membuat keputusan arsitektur baru, gunakan template ini:

```markdown
## ADR-XXX: [Judul Keputusan]

- **Status:** Proposed | Accepted | Deprecated | Superseded by ADR-YYY
- **Tanggal:** YYYY-MM-DD
- **Decider:** [Nama/Role]

**Konteks:**
[Situasi, masalah, atau kebutuhan yang memaksa keputusan ini]

**Keputusan:**
[Keputusan yang diambil, spesifik]

**Alasan:**
[Mengapa ini yang dipilih — faktor teknis, bisnis, tim]

**Konsekuensi:**
[Trade-off yang diterima, risiko, hal yang perlu diperhatikan]

**Alternatif yang ditolak:**
- **[Opsi A]:** [Mengapa ditolak]
- **[Opsi B]:** [Mengapa ditolak]

**Review Trigger (opsional):**
[Kondisi yang akan membuat keputusan ini direview ulang]
```

---

## Daftar Keputusan yang Perlu ADR (Backlog)

Keputusan berikut perlu ADR saat diambil nanti:

- [ ] ADR-009: Strategi caching produk (Redis vs in-memory vs Meilisearch)
- [ ] ADR-010: PDF generation library (chromium headless vs wkhtmltopdf vs Go PDF lib)
- [ ] ADR-011: Background job scheduler (Asynq vs cron vs Temporal)
- [ ] ADR-012: Feature flag system (Firebase Remote Config vs custom vs LaunchDarkly)
- [ ] ADR-013: Error tracking (Sentry vs self-hosted Glitchtip)
- [ ] ADR-014: Migrasi dari NATS ke Kafka (kapan dan bagaimana)
- [ ] ADR-015: Row-level security migration (kapan berpindah dari schema-per-tenant)

---

*Blueprint ini adalah living document — tambahkan ADR baru setiap ada keputusan arsitektur penting.*
*Last updated: 2025 | Extended Synaptic — XynPOS*
