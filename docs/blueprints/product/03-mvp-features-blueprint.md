# XynPOS — Blueprint 03: MVP Features Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Filosofi MVP XynPOS

MVP XynPOS harus menjawab satu pertanyaan utama:
> *"Bisakah seorang pemilik bisnis menjalankan operasi kasir sehari-hari sepenuhnya dengan XynPOS, tanpa perlu sistem lain?"*

Jika ya → MVP sukses.

**Prinsip MVP:**
- 🎯 **Core-first** — Selesaikan kasir, produk, laporan dasar dahulu
- 📱 **Mobile-first** — 80% user akan akses dari HP
- 🔌 **Offline-capable** — Internet tidak stabil di Indonesia
- 🌊 **Vertically launchable** — Bisa launch untuk F&B atau Retail saja lebih dulu
- 🏃 **Ship in 90 days** — MVP harus bisa di-launch dalam 3 bulan

---

## 2. Domain & Modul MVP

MVP terdiri dari **8 domain utama** dengan total **47 fitur inti**:

| # | Domain | Fitur | Prioritas |
|---|--------|-------|-----------|
| 1 | Authentication & Tenant | 5 | P0 |
| 2 | Product & Inventory | 8 | P0 |
| 3 | Point of Sale (Kasir) | 10 | P0 |
| 4 | Payment Processing | 6 | P0 |
| 5 | Customer Management | 4 | P1 |
| 6 | Reporting & Analytics | 7 | P1 |
| 7 | User & Role Management | 4 | P0 |
| 8 | Settings & Configuration | 3 | P1 |

> **P0** = Wajib ada sebelum launch | **P1** = Harus ada di launch | **P2** = Nice to have

---

## 3. Detail Fitur Per Domain

### 3.1 Domain: Authentication & Tenant Management

**Tujuan:** User bisa mendaftar, login, dan memiliki workspace terisolasi.

#### F-AUTH-01: Registrasi Tenant Baru
- Input: Nama bisnis, email, password, nomor HP
- Proses: Verifikasi email OTP, auto-create tenant workspace
- Output: Akun aktif + trial Pro 30 hari otomatis
- Edge case: Email sudah terdaftar → tampilkan pesan + link login
- **Platform:** Web, Mobile

#### F-AUTH-02: Login Multi-Platform
- Support: Email + password, Google OAuth (opsional)
- Session management: JWT access token (15 menit) + refresh token (30 hari)
- Remember device: Optional "Ingat perangkat ini"
- **Platform:** Web, Mobile

#### F-AUTH-03: Lupa Password / Reset Password
- Flow: Email → link reset → halaman reset → konfirmasi
- Expiry: Link valid 1 jam
- **Platform:** Web, Mobile

#### F-AUTH-04: Multi-Outlet Selection
- Setelah login, user memilih outlet mana yang akan dioperasikan
- Bisa switch outlet tanpa logout
- **Platform:** Web, Mobile

#### F-AUTH-05: Tenant Isolation
- Setiap tenant punya schema/namespace database terpisah
- Tidak ada data leakage antar tenant
- **Platform:** BE only

---

### 3.2 Domain: Product & Inventory Management

**Tujuan:** Pemilik bisnis bisa mengelola seluruh katalog produk dan stok.

#### F-PROD-01: CRUD Produk
- Field: Nama, SKU (auto-generate), harga jual, harga modal, satuan, kategori, foto (max 2MB), deskripsi, status (aktif/nonaktif)
- Bulk import via CSV/Excel
- **Platform:** Web, Mobile

#### F-PROD-02: Manajemen Kategori Produk
- Hierarki 2 level (Kategori → Sub-kategori)
- Icon/warna kategori untuk UX kasir
- Urutan drag-and-drop
- **Platform:** Web, Mobile

#### F-PROD-03: Variant Produk
- Contoh: Kopi Susu → Size (S/M/L), Suhu (Hot/Cold/Ice Blend)
- Harga berbeda per variant
- Stok per variant
- **Platform:** Web, Mobile

#### F-PROD-04: Modifier / Add-on Produk (F&B)
- Contoh: "Tambah Shot Espresso +5.000", "Kurangi Gula"
- Satu produk bisa punya multiple modifier group
- Modifier wajib vs opsional
- **Platform:** Web, Mobile

#### F-PROD-05: Manajemen Stok Dasar
- Input stok awal
- Auto-decrement saat transaksi
- Alert stok minimum (notifikasi push + email)
- **Platform:** Web, Mobile

#### F-PROD-06: Stock Adjustment
- Penyesuaian stok manual (rusak, hilang, opname)
- Log alasan penyesuaian
- Riwayat adjustment
- **Platform:** Web

#### F-PROD-07: Barcode / QR Code
- Generate barcode otomatis per produk
- Scan barcode saat transaksi (kamera HP atau scanner USB)
- Print label barcode
- **Platform:** Web, Mobile

#### F-PROD-08: Multi-Outlet Stock (per outlet)
- Stok independen per outlet
- Transfer stok antar outlet
- Riwayat transfer
- **Platform:** Web

---

### 3.3 Domain: Point of Sale (Kasir)

**Tujuan:** Kasir bisa melakukan transaksi penjualan dengan cepat dan akurat.

#### F-POS-01: Tampilan Kasir (POS Screen)
- Grid produk dengan foto, nama, harga
- Search produk by nama atau scan barcode
- Filter by kategori
- Shortcut keyboard untuk Web POS
- Desain: Big touch target untuk mobile
- **Platform:** Web, Mobile

#### F-POS-02: Keranjang Belanja (Cart)
- Tambah/kurangi item
- Edit quantity langsung
- Hapus item dari cart
- Subtotal real-time
- Notes per item
- **Platform:** Web, Mobile

#### F-POS-03: Diskon & Promo
- Diskon per item (nominal atau persentase)
- Diskon keseluruhan order
- Kode promo / voucher
- Diskon member loyalty
- **Platform:** Web, Mobile

#### F-POS-04: Pajak (PPN)
- Auto-calculate PPN 11%
- Pilihan harga sudah include tax atau exclude tax
- Tampilkan detail pajak di struk
- **Platform:** Web, Mobile

#### F-POS-05: Split Bill
- Bagi tagihan ke beberapa orang
- Bayar dengan metode berbeda per bagian
- **Platform:** Web, Mobile

#### F-POS-06: Hold Order
- Simpan transaksi sementara (parking)
- Buka kembali dari hold
- Multiple hold order
- **Platform:** Web, Mobile

#### F-POS-07: Order Notes
- Catatan spesial dari pelanggan
- Tampil di kitchen ticket dan struk
- **Platform:** Web, Mobile

#### F-POS-08: Table Management (F&B)
- Denah meja visual (drag-and-drop setup)
- Status meja: Available, Occupied, Reserved, Cleaning
- Pindah meja aktif
- **Platform:** Web, Mobile

#### F-POS-09: Offline Mode
- Transaksi tetap berjalan tanpa internet
- Data tersimpan lokal (SQLite/Hive)
- Auto-sync saat online kembali
- Conflict resolution otomatis
- **Platform:** Mobile

#### F-POS-10: Cetak Struk
- Bluetooth thermal printer (mobile)
- USB thermal printer (web/desktop)
- Struk digital via WhatsApp / email
- Custom header/footer struk
- **Platform:** Web, Mobile

---

### 3.4 Domain: Payment Processing

**Tujuan:** Menerima berbagai metode pembayaran dengan akurat.

#### F-PAY-01: Pembayaran Tunai
- Input nominal diterima
- Auto-calculate kembalian
- **Platform:** Web, Mobile

#### F-PAY-02: QRIS (Static & Dynamic)
- Static QR per outlet (sudah ada)
- Dynamic QR per transaksi (real-time amount)
- Status pembayaran real-time via webhook
- **Platform:** Web, Mobile

#### F-PAY-03: Transfer Bank / Virtual Account
- Generate VA per transaksi
- Ekspirasi VA 1–24 jam (configurable)
- Notifikasi payment confirmed
- **Platform:** Web, Mobile

#### F-PAY-04: e-Wallet (GoPay, OVO, Dana, ShopeePay)
- Deeplink ke app e-wallet
- Konfirmasi via callback
- **Platform:** Mobile-first

#### F-PAY-05: Split Payment
- Satu transaksi dibayar dengan kombinasi metode
- Contoh: Sebagian tunai + sebagian QRIS
- **Platform:** Web, Mobile

#### F-PAY-06: Pembayaran Hutang (Kredit Pelanggan)
- Tandai transaksi sebagai "hutang"
- Catat pelanggan yang berhutang
- Bayar hutang di kemudian hari
- Laporan piutang outstanding
- **Platform:** Web, Mobile

---

### 3.5 Domain: Customer Management

**Tujuan:** Mengelola data pelanggan dan loyalitas dasar.

#### F-CUST-01: CRUD Data Pelanggan
- Field: Nama, HP, email, alamat, tanggal lahir, catatan
- Auto-create dari transaksi (opsional)
- **Platform:** Web, Mobile

#### F-CUST-02: Riwayat Transaksi Pelanggan
- Timeline pembelian
- Total spending
- Produk favorit
- **Platform:** Web

#### F-CUST-03: Program Poin Loyalitas
- Konfigurasi: X rupiah = Y poin
- Redeem poin sebagai diskon
- Lihat saldo poin di kasir
- **Platform:** Web, Mobile

#### F-CUST-04: Segmentasi Pelanggan Dasar
- Label/tag pelanggan (VIP, Regular, Wholesale)
- Filter pelanggan berdasarkan tag
- **Platform:** Web

---

### 3.6 Domain: Reporting & Analytics

**Tujuan:** Pemilik bisnis bisa memahami performa bisnis dari data real-time.

#### F-RPT-01: Dashboard Utama
- Ringkasan hari ini: Total penjualan, transaksi, item terjual
- Grafik penjualan 7/30 hari
- Top 5 produk terlaris
- **Platform:** Web, Mobile

#### F-RPT-02: Laporan Penjualan
- Filter: Tanggal, outlet, kasir, kategori produk
- Detail per transaksi
- Export ke PDF dan Excel
- **Platform:** Web

#### F-RPT-03: Laporan Inventori
- Stok saat ini per produk per outlet
- Riwayat pergerakan stok
- Produk hampir habis
- **Platform:** Web

#### F-RPT-04: Laporan Laba Rugi Sederhana
- Pendapatan vs HPP
- Gross profit per periode
- **Platform:** Web

#### F-RPT-05: Laporan Kasir
- Rekap penjualan per kasir
- Shift report (buka tutup kasir)
- **Platform:** Web, Mobile

#### F-RPT-06: Laporan Metode Pembayaran
- Breakdown per payment method
- Rekap cash vs non-cash
- **Platform:** Web

#### F-RPT-07: Laporan Pelanggan
- Pelanggan terbanyak belanja
- Hutang pelanggan outstanding
- **Platform:** Web

---

### 3.7 Domain: User & Role Management

**Tujuan:** Kontrol akses yang aman antar pengguna dalam satu bisnis.

#### F-USER-01: Manajemen User
- Undang user via email
- Assign ke outlet tertentu
- Nonaktifkan user
- **Platform:** Web

#### F-USER-02: Role Bawaan
- **Owner:** Full access semua
- **Manager:** Akses laporan, produk, inventori; tidak bisa hapus data
- **Cashier:** Hanya bisa kasir + lihat transaksi sendiri
- **Inventory Staff:** Hanya stok dan produk
- **Platform:** Web

#### F-USER-03: PIN Kasir
- Kasir login dengan PIN 4–6 digit
- Ganti shift kasir tanpa logout akun owner
- **Platform:** Mobile, Web

#### F-USER-04: Audit Log
- Rekam semua aksi penting (hapus produk, ubah harga, void transaksi)
- Filter by user dan waktu
- **Platform:** Web

---

### 3.8 Domain: Settings & Configuration

#### F-SET-01: Pengaturan Bisnis
- Nama bisnis, logo, alamat, nomor HP, NPWP
- Timezone dan mata uang
- Format struk
- **Platform:** Web

#### F-SET-02: Pengaturan Outlet
- Nama outlet, alamat, jam operasional
- Printer default
- **Platform:** Web

#### F-SET-03: Notifikasi
- Email notifikasi: Transaksi besar, stok habis, pembayaran subscription
- Push notification: Alert stok
- **Platform:** Web, Mobile

---

## 4. User Stories Prioritas Tinggi

### US-001: Transaksi Kasir Dasar (Happy Path)
```
Sebagai kasir,
Saya ingin memilih produk, menerima pembayaran, dan mencetak struk
Agar transaksi selesai dalam waktu < 30 detik
```
**Acceptance Criteria:**
- [ ] Kasir bisa search produk by nama dalam < 1 detik
- [ ] Scan barcode menambah produk ke cart dalam < 0.5 detik
- [ ] Hitung kembalian tunai otomatis
- [ ] Struk tercetak dalam < 3 detik setelah konfirmasi
- [ ] Transaksi tersimpan meski internet terputus

### US-002: Monitoring Stok Real-time
```
Sebagai pemilik bisnis,
Saya ingin mendapat notifikasi saat stok produk hampir habis
Agar saya bisa restock sebelum kehabisan
```
**Acceptance Criteria:**
- [ ] Setting batas minimum stok per produk
- [ ] Push notification + email saat stok ≤ minimum
- [ ] Dashboard menampilkan produk dengan stok kritis

### US-003: Laporan Harian dari HP
```
Sebagai pemilik bisnis,
Saya ingin melihat total penjualan hari ini dari HP
Agar saya bisa monitor bisnis saat tidak di lokasi
```
**Acceptance Criteria:**
- [ ] Dashboard mobile load < 3 detik
- [ ] Data akurat real-time (delay maks 5 menit)
- [ ] Bisa drill-down ke transaksi detail

---

## 5. Non-Functional Requirements MVP

| Aspek | Requirement |
|-------|------------|
| **Performance** | API response < 300ms (p95), Kasir screen load < 2 detik |
| **Availability** | 99.5% uptime (Starter), 99.9% (Pro+) |
| **Offline** | Kasir tetap berfungsi 100% tanpa internet |
| **Sync** | Data ter-sync ke server dalam 30 detik setelah online |
| **Security** | JWT + HTTPS + enkripsi data sensitif at-rest |
| **Mobile Support** | Android 8.0+, iOS 14+ |
| **Browser Support** | Chrome, Firefox, Safari, Edge (2 versi terakhir) |
| **Concurrent Users** | 100 transaksi/detik per tenant besar |
| **Data Retention** | Data tersimpan minimal 2 tahun (Pro+) |

---

## 6. MVP Exclusions (Sengaja TIDAK Ada di MVP)

Fitur berikut **tidak** termasuk MVP untuk menjaga scope dan timeline:

| Fitur Dikecualikan | Alasan | Target Post-MVP |
|-------------------|--------|-----------------|
| Kitchen Display System (KDS) | Kompleks hardware | Post-MVP Sprint 2 |
| Purchase Order (PO) ke supplier | Butuh module terpisah | Post-MVP Sprint 1 |
| e-Faktur / integrasi pajak | Butuh integrasi DJP | Post-MVP Sprint 3 |
| Marketplace integration (Shopee, Tokopedia) | Kompleks API | Post-MVP Sprint 4 |
| Payroll karyawan | Beda domain, scope besar | XYN ERP |
| Akuntansi lengkap (neraca, dll) | Beda domain | XYN ERP |
| Delivery / kurir integration | Butuh 3rd party API | Post-MVP Sprint 3 |
| Loyalty advanced (tier, cashback) | Cukup poin dasar dulu | Post-MVP Sprint 2 |
| White label | Enterprise only | Post-MVP Sprint 5 |
| Multi-currency | Butuh setup pajak kompleks | Post-MVP Sprint 4 |

---

## 7. MVP Sprint Plan (12 Minggu)

| Sprint | Minggu | Fokus | Output |
|--------|--------|-------|--------|
| S1 | 1–2 | Setup infra, Auth, Tenant | Login, Register, Tenant isolation |
| S2 | 3–4 | Product Management | CRUD produk, kategori, variant |
| S3 | 5–6 | POS Core | Kasir screen, cart, checkout |
| S4 | 7–8 | Payment + Receipt | Cash, QRIS, cetak struk |
| S5 | 9–10 | Inventory + Reporting | Stok, dashboard, laporan dasar |
| S6 | 11–12 | User management, Polish, Testing | Role, audit log, bug fix, beta |

---

## 8. Definition of Done (DoD) per Fitur

Sebuah fitur dianggap SELESAI jika:
- [ ] Unit test coverage ≥ 70%
- [ ] API endpoint terdokumentasi di Swagger
- [ ] Berjalan di Android, iOS, dan Web
- [ ] Offline mode tested (jika applicable)
- [ ] Code review approved
- [ ] QA sign-off di staging environment
- [ ] Tidak ada P0/P1 bug open

---

*Blueprint ini inline dengan: BP-02 (Financial/Plan features), BP-04 (Post-MVP), BP-05 (Tech Stack), BP-08 (DB Schema)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
