# XynPOS — Blueprint 04: Post-MVP & Advanced Features Roadmap
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Filosofi Post-MVP

Post-MVP bukan berarti "fitur tambahan yang tidak penting" — ini adalah **diferensiasi kompetitif** XynPOS. Setelah core POS stabil, fitur-fitur ini adalah alasan mengapa bisnis **tidak mau pindah** ke kompetitor (lock-in value) dan alasan enterprise mau bayar premium.

**Roadmap diorganisir berdasarkan:**
- **Sprint Wave** — urutan pengerjaan
- **Segment value** — siapa yang paling diuntungkan
- **Revenue impact** — apakah fitur ini menaikkan ARPU

---

## 2. Post-MVP Roadmap Overview

| Wave | Timeline (Post-Launch) | Theme | Segment Utama |
|------|------------------------|-------|---------------|
| **Wave 1** | Bulan 1–2 | Operational Excellence | T2–T3 |
| **Wave 2** | Bulan 3–4 | F&B Deep Dive | T2 F&B |
| **Wave 3** | Bulan 5–6 | Retail Intelligence | T2–T3 Retail |
| **Wave 4** | Bulan 7–9 | Enterprise & Compliance | T3–T4 |
| **Wave 5** | Bulan 10–12 | Ecosystem & Platform | T4 + Developer |
| **Wave 6** | Tahun 2 | AI & Automation | Semua |

---

## 3. Wave 1 — Operational Excellence

### 3.1 Purchase Order (PO) Management

**Deskripsi:** Alur lengkap pemesanan ke supplier, penerimaan barang, dan update stok otomatis.

**Fitur Detail:**
- Manajemen data supplier (nama, kontak, alamat, payment term)
- Buat Purchase Order dengan item dan quantity
- Status PO: Draft → Sent → Partial Received → Completed → Cancelled
- Penerimaan barang (GRN — Goods Receipt Note):
  - Input quantity yang diterima (bisa partial)
  - Auto-update stok saat GRN dikonfirmasi
  - Catatan discrepancy (quantity tidak sesuai PO)
- Riwayat PO per supplier
- Alert PO yang sudah jatuh tempo
- Export PO ke PDF untuk dikirim ke supplier via WhatsApp/email

**Plan:** Pro+
**Segment:** Semua vertikal
**Effort:** Medium (2 sprint)

---

### 3.2 Kitchen Display System (KDS)

**Deskripsi:** Layar di dapur yang menampilkan order masuk secara real-time, menggantikan tiket kertas.

**Fitur Detail:**
- Tampilan order yang masuk dari kasir ke layar dapur
- Kategorisasi per station (grill, minuman, cold food)
- Timer per item (berapa lama sudah antri)
- Status item: New → In Progress → Ready → Served
- Bump order saat selesai
- Alert jika order belum diproses > X menit
- KDS bisa berjalan di tablet Android/iPad atau monitor web
- Mendukung multiple KDS (satu per station)
- Notifikasi bunyi saat order baru masuk

**Plan:** Pro+
**Segment:** F&B
**Effort:** High (3 sprint)

---

### 3.3 Shift Management

**Deskripsi:** Manajemen shift kasir yang terstruktur dengan rekap per shift.

**Fitur Detail:**
- Buka shift: Input uang awal di laci kasir (opening balance)
- Rekap shift saat tutup: Total penjualan, total cash, total non-cash
- Hitung selisih (expected cash vs actual cash)
- Notifikasi selisih ke manager/owner
- Multiple shift per hari (pagi/sore/malam)
- Riwayat shift dan rekap per kasir

**Plan:** Starter+
**Segment:** Semua
**Effort:** Low (1 sprint)

---

### 3.4 Stock Opname (Stocktake)

**Deskripsi:** Fitur hitung stok fisik dan sinkronisasi dengan data sistem.

**Fitur Detail:**
- Buat sesi stocktake (bisa partial — per kategori)
- Input jumlah fisik per produk (bisa via scan barcode)
- Sistem tampilkan selisih (sistem vs fisik)
- Konfirmasi adjustment dengan alasan
- Lock stok saat stocktake berlangsung (opsi)
- Laporan hasil stocktake (selisih nilai HPP)

**Plan:** Pro+
**Segment:** Retail, Apotek
**Effort:** Medium (2 sprint)

---

## 4. Wave 2 — F&B Deep Dive

### 4.1 Recipe & Ingredient Management (Cost of Goods)

**Deskripsi:** Lacak komposisi bahan baku per menu dan hitung HPP secara otomatis.

**Fitur Detail:**
- Buat resep: 1 produk terdiri dari beberapa bahan baku
- Bahan baku sebagai inventory item tersendiri
- Saat produk terjual → auto-decrement bahan baku
- Kalkulasi HPP per produk berdasarkan harga beli bahan
- Alert bahan baku hampir habis
- Laporan food cost per periode
- Waste tracking (bahan terbuang)

**Plan:** Pro+
**Segment:** F&B
**Effort:** High (3 sprint)

---

### 4.2 Reservasi & Waitlist

**Deskripsi:** Sistem booking meja dan waiting list untuk restoran.

**Fitur Detail:**
- Booking via link publik (web + WhatsApp integration)
- Konfirmasi booking via email/WA otomatis
- Reminder H-1 dan H-3 jam
- Status booking: Pending → Confirmed → Seated → Completed → No-show → Cancelled
- Waitlist saat semua meja penuh
- Notifikasi ke pelanggan saat meja tersedia
- Tampilan kalender dan timeline meja
- Kapasitas per meja

**Plan:** Pro+
**Segment:** F&B (Restoran, Café)
**Effort:** High (3 sprint)

---

### 4.3 Online Ordering (QR Menu + Self-Order)

**Deskripsi:** Pelanggan scan QR di meja → pesan sendiri → langsung masuk ke kasir/KDS.

**Fitur Detail:**
- Generate QR code per meja
- Mobile-optimized menu page (PWA)
- Pelanggan tambah item ke cart sendiri
- Submit order → langsung muncul di KDS dan kasir
- Status order di HP pelanggan (real-time)
- Opsional: bayar langsung via QRIS/e-wallet di menu

**Plan:** Business+
**Segment:** F&B (Café, Restoran casual)
**Effort:** Very High (4 sprint)

---

### 4.4 Happy Hour & Time-Based Pricing

**Deskripsi:** Harga produk berubah otomatis berdasarkan waktu.

**Fitur Detail:**
- Set jam dan hari untuk harga khusus
- Diskon otomatis saat happy hour aktif
- Visual indicator "Happy Hour" di kasir
- History penggunaan happy hour pricing

**Plan:** Pro+
**Segment:** F&B
**Effort:** Low (1 sprint)

---

## 5. Wave 3 — Retail Intelligence

### 5.1 Supplier & Price Management

**Deskripsi:** Manajemen multi-supplier per produk dengan tracking harga pembelian.

**Fitur Detail:**
- Multiple supplier per produk
- Riwayat harga beli per supplier
- Alert jika harga supplier naik signifikan
- Preferred supplier per produk
- Perbandingan harga antar supplier

**Plan:** Pro+
**Segment:** Retail, Groceries
**Effort:** Medium (2 sprint)

---

### 5.2 Promosi & Campaign Management

**Deskripsi:** Buat dan kelola berbagai jenis promosi secara terjadwal.

**Fitur Detail:**
- Tipe promosi:
  - Buy X Get Y (beli 2 gratis 1)
  - Bundle deal (beli A+B harga khusus)
  - Minimum purchase discount (belanja min 100K diskon 15%)
  - Member-only price
  - Flash sale (limited waktu)
  - Birthday promo (otomatis ke pelanggan ulang tahun)
- Jadwal kampanye (start-end date)
- Limit penggunaan per promosi
- Laporan efektivitas promo

**Plan:** Pro+
**Segment:** Semua
**Effort:** High (3 sprint)

---

### 5.3 Expired Date & Batch Tracking

**Deskripsi:** Tracking batch produk dengan tanggal kadaluarsa — kritikal untuk apotek dan F&B.

**Fitur Detail:**
- Input nomor batch dan expired date saat receive stock
- FIFO/FEFO otomatis (First Expired First Out)
- Alert produk mendekati expired (configurable: 7/14/30 hari sebelum)
- Laporan produk akan expired
- Riwayat pergerakan per batch
- Retur ke supplier untuk produk expired

**Plan:** Business+
**Segment:** Apotek, F&B, Groceries
**Effort:** High (3 sprint)

---

### 5.4 Price List & Customer-Based Pricing

**Deskripsi:** Harga berbeda per segmen pelanggan atau grup.

**Fitur Detail:**
- Buat beberapa price list (Retail, Grosir, Member VIP)
- Assign price list ke pelanggan atau tag pelanggan
- Kasir otomatis menggunakan harga sesuai pelanggan
- Laporan per price list

**Plan:** Business+
**Segment:** Retail Grosir, FMCG
**Effort:** Medium (2 sprint)

---

### 5.5 Consignment (Produk Titipan)

**Deskripsi:** Kelola produk yang dititipkan oleh supplier/vendor pihak ketiga.

**Fitur Detail:**
- Data produk konsinyasi per vendor
- Tracking penjualan produk konsinyasi
- Auto-kalkulasi komisi vendor
- Laporan konsinyasi per periode
- Rekonsiliasi pembayaran ke vendor

**Plan:** Business+
**Segment:** Retail fashion, accessories, crafts
**Effort:** Medium (2 sprint)

---

## 6. Wave 4 — Enterprise & Compliance

### 6.1 Multi-Outlet Consolidated Dashboard

**Deskripsi:** Dashboard terpusat untuk memantau semua outlet sekaligus.

**Fitur Detail:**
- Aggregasi revenue semua outlet real-time
- Comparison performa antar outlet
- Heat map penjualan per waktu per outlet
- Drill-down dari konsolidat ke outlet spesifik
- Custom date range comparison (minggu ini vs minggu lalu)
- Export laporan konsolidat

**Plan:** Business+
**Segment:** Enterprise T4
**Effort:** Medium (2 sprint)

---

### 6.2 e-Faktur Integration (Pajak Indonesia)

**Deskripsi:** Integrasi langsung dengan sistem e-Faktur DJP untuk PKP (Pengusaha Kena Pajak).

**Fitur Detail:**
- Generate e-Faktur otomatis per transaksi (B2B)
- Upload ke DJP Online otomatis
- Manajemen nomor seri faktur pajak
- Laporan pajak bulanan (SPT Masa PPN)
- Validasi NPWP pembeli
- Support PPN 11% dan PPN 0% (ekspor)

**Plan:** Business+
**Segment:** Enterprise, PKP
**Effort:** Very High (5 sprint — regulasi kompleks)

---

### 6.3 Role-Based Access Control (RBAC) Advanced

**Deskripsi:** Kontrol akses granular untuk enterprise dengan custom role.

**Fitur Detail:**
- Custom role creation (nama + permission set)
- Permission granular per modul (view, create, edit, delete, export)
- Scope role: Global (semua outlet) atau per outlet tertentu
- Delegated admin (manager outlet bisa manage user di outletnya)
- Approval workflow (contoh: void transaksi butuh approval manager)
- Role inheritance

**Plan:** Business+
**Segment:** Enterprise
**Effort:** High (3 sprint)

---

### 6.4 API & Webhook Platform

**Deskripsi:** Platform API terbuka untuk integrasi pihak ketiga.

**Fitur Detail:**
- REST API dengan dokumentasi lengkap (OpenAPI/Swagger)
- Webhook untuk event: transaction.created, stock.updated, dll
- API key management (create, revoke, rotate)
- Rate limiting per API key
- Sandbox environment untuk testing
- SDK (JavaScript, Python — Wave 5)
- API usage analytics

**Plan:** Pro (read-only), Business+ (full)
**Segment:** Developer, Enterprise
**Effort:** High (3 sprint)

---

### 6.5 Approval Workflow

**Deskripsi:** Sistem persetujuan multi-level untuk aksi sensitif.

**Fitur Detail:**
- Definisikan aksi yang butuh approval (void, diskon > X%, hapus produk)
- Approval chain (kasir → manager → owner)
- Approval via HP (push notification)
- Audit trail approval
- Eskalasi jika tidak diapprove dalam waktu tertentu

**Plan:** Business+
**Segment:** Enterprise
**Effort:** Medium (2 sprint)

---

## 7. Wave 5 — Ecosystem & Platform

### 7.1 XynPOS ↔ XYN CRM Integration

**Deskripsi:** Sync data pelanggan dan transaksi ke XYN CRM untuk sales dan marketing.

**Fitur Detail:**
- Auto-sync customer data setelah transaksi
- Trigger CRM workflow dari event POS (contoh: pelanggan belanja > 500K → tag VIP)
- Lihat history CRM di profil pelanggan POS
- Campaign dari CRM bisa apply promo di POS

**Plan:** Pro+
**Segment:** Semua yang punya XYN CRM
**Effort:** High (bergantung XYN CRM development)

---

### 7.2 XynPOS ↔ XYN ERP Integration

**Deskripsi:** Sinkronisasi data keuangan dan inventori ke XYN ERP.

**Fitur Detail:**
- Auto-posting journal entry ke ERP setelah transaksi
- Sync produk dan harga dari ERP ke POS
- Sync stok real-time dua arah
- Laporan keuangan ERP mencakup data POS

**Plan:** Business+
**Segment:** Enterprise
**Effort:** Very High

---

### 7.3 Marketplace Integration

**Deskripsi:** Sinkronisasi produk dan stok dengan marketplace online.

**Fitur Detail:**
- Integrasi: Tokopedia, Shopee, TikTok Shop, Lazada
- Sync stok: Jika stok habis di POS → otomatis update marketplace
- Sync produk (nama, harga, foto)
- Order dari marketplace masuk sebagai transaksi POS
- Laporan penjualan gabungan (offline + online)

**Plan:** Business+
**Segment:** Retail omnichannel
**Effort:** Very High (4 sprint per marketplace)

---

### 7.4 WhatsApp Business Integration

**Deskripsi:** Kirim struk, notifikasi, dan kampanye via WhatsApp Business API.

**Fitur Detail:**
- Struk digital via WA setelah transaksi
- Notifikasi stok ke owner via WA
- Broadcast promo ke pelanggan via WA blast
- WA bot untuk customer service dasar
- Template pesan yang bisa dikustomisasi

**Plan:** Pro+
**Segment:** Semua
**Effort:** Medium (2 sprint)

---

### 7.5 Hardware Management

**Deskripsi:** Manajemen perangkat keras POS yang terhubung.

**Fitur Detail:**
- Registrasi perangkat (printer, scanner, cash drawer, tablet)
- Status perangkat online/offline
- Remote config printer
- Paper low alert (untuk printer yang mendukung)
- Troubleshooting guide per perangkat

**Plan:** Starter+
**Segment:** Semua
**Effort:** Medium

---

## 8. Wave 6 — AI & Automation (Tahun 2)

### 8.1 AI Sales Forecasting

**Deskripsi:** Prediksi penjualan menggunakan machine learning berdasarkan historical data.

**Fitur Detail:**
- Prediksi penjualan 7/14/30 hari ke depan per produk
- Rekomendasi quantity restock otomatis
- Anomaly detection (penjualan drop/spike tidak wajar)
- Faktor musiman (hari libur, cuaca — integrasi BMKG)
- Accuracy score per prediksi

---

### 8.2 AI-Powered Smart Promotion

**Deskripsi:** Rekomendasi promosi yang paling efektif berdasarkan data pelanggan.

**Fitur Detail:**
- Analisis produk yang sering dibeli bersamaan (market basket analysis)
- Rekomendasi bundle deal otomatis
- Segmentasi pelanggan otomatis berdasarkan behavior
- A/B testing promosi
- Prediksi churn pelanggan (pelanggan yang sudah lama tidak datang)

---

### 8.3 Conversational AI Assistant

**Deskripsi:** AI assistant dalam aplikasi untuk pertanyaan bisnis natural language.

**Fitur Detail:**
- Tanya laporan dalam bahasa Indonesia: *"Produk apa yang paling laku minggu ini?"*
- Analisis bisnis on-demand
- Alert bisnis otomatis: *"Revenue turun 20% dibanding minggu lalu"*
- Rekomendasi tindakan
- Menggunakan XYN AI engine (produk Extended Synaptic berikutnya)

---

### 8.4 Automated Accounting

**Deskripsi:** Otomasi jurnal akuntansi dasar tanpa perlu input manual.

**Fitur Detail:**
- Chart of Accounts sederhana
- Auto-posting: Setiap transaksi POS → journal entry otomatis
- Laporan: Neraca sederhana, Laporan Laba Rugi, Arus Kas
- Export untuk akuntan
- Integrasi ke Accurate Online / Jurnal.id

---

### 8.5 Loyalty 2.0 — Gamification

**Deskripsi:** Program loyalitas tingkat lanjut dengan elemen gamifikasi.

**Fitur Detail:**
- Tier loyalty (Bronze → Silver → Gold → Platinum)
- Benefit berbeda per tier (diskon, priority service, free item)
- Badge dan achievement
- Referral program (ajak teman → bonus poin)
- Leaderboard pelanggan (opsional, gamifikasi)
- Digital membership card (wallet pass Apple/Google)

---

## 9. Feature Prioritization Matrix

```
                    HIGH VALUE
                        │
   Wave 4-5 ●  ●Wave 3  │  ● Wave 1–2
  (e-Faktur)  (Promo)   │  (PO, KDS, Shift)
                        │
HIGH EFFORT ────────────┼──────────────── LOW EFFORT
                        │
   Wave 6 ●             │   ● Quick Wins
  (AI Features)         │   (Happy Hour, 
                        │    Batch Expiry)
                    LOW VALUE
```

---

## 10. Feature Dependency Map

```
MVP Core (BP-03)
    ├── Wave 1: Purchase Order → butuh: Product ✓, Inventory ✓
    ├── Wave 1: KDS → butuh: POS Core ✓, Table Management ✓
    ├── Wave 1: Shift Management → butuh: User Management ✓
    ├── Wave 2: Recipe → butuh: Product ✓, PO ✓
    ├── Wave 2: Reservasi → butuh: Table Management ✓
    ├── Wave 2: QR Menu → butuh: POS Core ✓, KDS ✓
    ├── Wave 3: Promo Campaign → butuh: Customer ✓, Product ✓
    ├── Wave 3: Batch Tracking → butuh: Inventory ✓, PO ✓
    ├── Wave 4: e-Faktur → butuh: Payment ✓, Customer ✓
    ├── Wave 4: API Platform → butuh: Auth ✓, Core stable
    ├── Wave 5: CRM Integration → butuh: Customer ✓, API ✓
    ├── Wave 5: Marketplace → butuh: Product ✓, Inventory ✓, API ✓
    └── Wave 6: AI → butuh: 12+ bulan data historis
```

---

## 11. Estimasi Resource Post-MVP

| Wave | Sprint (2 minggu) | Dev Needed | Estimasi Timeline |
|------|-------------------|-----------|-------------------|
| Wave 1 | 4–5 sprint | 2 BE + 1 FE | Bulan 1–2 post-launch |
| Wave 2 | 6–7 sprint | 2 BE + 2 FE | Bulan 3–4 post-launch |
| Wave 3 | 5–6 sprint | 2 BE + 1 FE | Bulan 5–6 post-launch |
| Wave 4 | 8–10 sprint | 3 BE + 2 FE | Bulan 7–9 post-launch |
| Wave 5 | 10–12 sprint | 3 BE + 2 FE + 1 Mobile | Bulan 10–12 post-launch |
| Wave 6 | 12+ sprint | + ML Engineer | Tahun 2 |

---

*Blueprint ini inline dengan: BP-03 (MVP), BP-05 (Tech Stack), BP-02 (Pricing per plan)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
