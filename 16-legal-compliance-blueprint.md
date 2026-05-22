# XynPOS — Blueprint 16: Legal & Compliance Blueprint
> Extended Synaptic | Version 1.0 | Confidential
> ⚠️ Dokumen ini adalah panduan umum, bukan nasihat hukum. Konsultasikan dengan lawyer untuk keputusan legal.

---

## 1. Entitas Hukum

### 1.1 Rekomendasi Bentuk Badan Usaha

**Pilihan: PT (Perseroan Terbatas)**

| Aspek | Detail |
|-------|--------|
| **Bentuk** | PT dengan minimal 2 pemegang saham |
| **Nama** | PT Extended Synaptic Indonesia |
| **Bidang usaha** | KBLI 62010 - Aktivitas Pemrograman Komputer |
| **Modal dasar minimum** | Rp 50.000.000 (bisa di bawah untuk UMK) |
| **Waktu pendirian** | 2–4 minggu via OSS (Online Single Submission) |
| **Biaya pendirian** | Rp 5–10 juta (via notaris) |

**Mengapa PT (bukan CV atau Perorangan)?**
- Diperlukan untuk kontrak enterprise
- Bisa terima investasi lebih mudah
- Pisahkan aset pribadi dan bisnis
- Lebih kredibel untuk kerjasama payment gateway
- Dibutuhkan untuk daftar di Play Store/App Store sebagai organisasi

### 1.2 Dokumen Pendirian

```
Checklist dokumen PT:
[ ] Akta pendirian PT (notaris)
[ ] SK Kemenkumham (persetujuan Menkumham)
[ ] NPWP PT
[ ] NIB (Nomor Induk Berusaha) via OSS
[ ] SIUP jika diperlukan oleh bidang usaha
[ ] BPJS Ketenagakerjaan + Kesehatan (saat ada karyawan)
[ ] Rekening bank atas nama PT
```

---

## 2. Perjanjian & Terms of Service

### 2.1 Dokumen Legal yang Harus Dibuat

| Dokumen | Kepentingan | Kapan Dibutuhkan |
|---------|-------------|-----------------|
| **Terms of Service (ToS)** | Mengatur hubungan dengan tenant | Sebelum launch |
| **Privacy Policy** | Wajib UU PDP + App Store | Sebelum launch |
| **Data Processing Agreement (DPA)** | Untuk enterprise customer | Saat ada enterprise |
| **Refund Policy** | Transparansi ke user | Sebelum launch |
| **Cookie Policy** | Untuk web app | Sebelum launch |
| **SLA Agreement** | Untuk Business+ | Saat ada Business plan |
| **Reseller Agreement** | Untuk channel partner | Saat ada reseller |

### 2.2 Klausul Penting dalam ToS

```
ToS XynPOS harus mencakup minimal:

1. DEFINISI
   - Tenant, User, Outlet, Data Transaksi, dsb.

2. LAYANAN
   - Deskripsi layanan per plan
   - Pembatasan plan (transaksi, outlet, user)
   - Uptime SLA per plan

3. PEMBAYARAN
   - Harga per plan
   - Kebijakan penagihan (billing cycle)
   - Kenaikan harga (minimal 30 hari notice)
   - Refund policy
   - Keterlambatan bayar

4. DATA & PRIVASI
   - Siapa pemilik data transaksi (TENANT, bukan XynPOS)
   - Bagaimana data diproses
   - Retensi data
   - Right to export & erasure (UU PDP)

5. PEMBATASAN TANGGUNG JAWAB
   - XynPOS tidak bertanggung jawab atas:
     - Kehilangan bisnis akibat downtime
     - Kesalahan input user
     - Kesalahan integrasi pihak ketiga
   - Limitation of liability cap: 3x monthly fee

6. LARANGAN
   - Tidak boleh scraping/crawl API
   - Tidak boleh resell tanpa izin
   - Tidak boleh untuk aktivitas ilegal

7. TERMINASI
   - Kapan XynPOS bisa terminate akun
   - Prosedur terminasi
   - Data pasca terminasi

8. HUKUM YANG BERLAKU
   - Hukum Indonesia
   - Yurisdiksi: Pengadilan Negeri [kota]
```

### 2.3 Privacy Policy — Poin Kritis

Berdasarkan UU PDP No. 27/2022 dan standar internasional (GDPR-aligned):

```
Privacy Policy WAJIB mencakup:

A. DATA YANG DIKUMPULKAN:
   - Data pendaftaran (nama, email, HP)
   - Data transaksi bisnis
   - Data pelanggan tenant
   - Log penggunaan aplikasi
   - IP address dan device info

B. TUJUAN PENGGUNAAN:
   - Operasional layanan POS
   - Pengiriman invoice dan notifikasi
   - Analisis untuk peningkatan produk (aggregated, anonymized)
   - TIDAK untuk dijual ke pihak ketiga

C. BERBAGI DATA:
   - Payment gateway (Xendit, Midtrans) — untuk pemrosesan pembayaran
   - Cloud provider (DigitalOcean, Cloudflare) — untuk infrastruktur
   - Email service (Resend) — untuk notifikasi
   → TIDAK ada penjualan data

D. HAK SUBJEK DATA:
   - Hak akses (lihat data sendiri)
   - Hak koreksi
   - Hak penghapusan (right to erasure)
   - Hak portabilitas (export data)
   - Hak keberatan

E. RETENTION:
   - Data tenant aktif: selama aktif + sesuai kebijakan
   - Data tenant non-aktif Free: 30 hari
   - Data tenant non-aktif Paid: 1 tahun

F. KONTAK DPO:
   - Email: privacy@extendedsynaptic.com
```

---

## 3. Kepatuhan Regulasi Indonesia

### 3.1 Pajak

#### PPN (Pajak Pertambahan Nilai)

| Aspek | Detail |
|-------|--------|
| **Threshold PKP** | Omzet > Rp 4,8 miliar/tahun → wajib PKP |
| **Tarif PPN** | 11% (UU HPP 2021) |
| **Kewajiban** | Buat Faktur Pajak untuk setiap transaksi B2B PKP |
| **Laporan** | SPT Masa PPN setiap bulan |
| **e-Faktur** | Wajib pakai aplikasi e-Faktur DJP untuk PKP |

**Untuk XynPOS (sebagai perusahaan):**
- Daftar PKP saat omzet mendekati Rp 4,8 miliar
- Mulai jual ke enterprise → pertimbangkan daftar PKP lebih awal

**Untuk Tenant XynPOS:**
- XynPOS membantu mereka hitung PPN di setiap transaksi
- Tampilkan PPN di struk (sudah built-in di fitur F-POS-04)
- e-Faktur integration di Wave 4 (untuk tenant PKP)

#### PPh (Pajak Penghasilan)

- PPh 25 (badan): 22% dari laba bersih
- PPh 21 (karyawan): dipotong dari gaji
- PPh 23 (jasa): 2% untuk jasa yang dibayar ke pihak lain

### 3.2 Izin Terkait Fintech & Payment

| Regulasi | Otoritas | Relevansi XynPOS |
|----------|----------|-----------------|
| **POJK 77/2016** (P2P Lending) | OJK | Tidak relevan (tidak ada fitur pinjaman) |
| **BI PADG 1/2019** (QRIS) | Bank Indonesia | Wajib support QRIS, partner dengan PJSP |
| **PBI 22/2020** (SP) | Bank Indonesia | Jika ingin jadi Payment Service Provider sendiri |
| **POJK 13/2021** (Inovasi Keuangan Digital) | OJK | Regulatory sandbox jika ada fitur fintech |

**Posisi XynPOS:** Bukan PSP (Payment Service Provider) — hanya aggregator yang menghubungkan merchant ke PSP (Xendit, Midtrans). Tidak butuh izin BI/OJK sendiri. ✅

### 3.3 Perlindungan Data (UU PDP)

Sudah dibahas di BP-10 (Security) dan Privacy Policy di atas.

**Timeline compliance:**
- **Sekarang:** Implementasikan privacy policy, right to erasure, enkripsi data
- **2024:** UU PDP mulai efektif sepenuhnya — pastikan semua compliance berjalan
- **Scale:** Saat > 50 karyawan, tunjuk Data Protection Officer (DPO)

### 3.4 BSSN (Badan Siber dan Sandi Negara)

- Wajib lapor insiden siber yang material ke BSSN dalam 14 hari (berdasarkan PP 71/2019)
- Jika ada breach data PII → lapor ke BSSN dan subjek data dalam 14 hari

---

## 4. Hak Kekayaan Intelektual (HKI)

### 4.1 Merek Dagang

```
Daftarkan merek berikut ke DJKI (Direktorat Jenderal Kekayaan Intelektual):

Merek: XynPOS
Merek: Extended Synaptic
Logo: Extended Synaptic

Kelas:
- Kelas 9: Software, aplikasi komputer
- Kelas 42: Layanan SaaS, software as a service

Biaya: ~Rp 2.500.000 per merek per kelas
Waktu: 6-12 bulan proses
Masa berlaku: 10 tahun (dapat diperpanjang)

Timeline: Daftarkan SEBELUM launch publik untuk mencegah squatting
```

### 4.2 Hak Cipta

- Source code XynPOS otomatis dilindungi hak cipta sejak dibuat (tidak perlu daftar)
- Namun untuk kekuatan hukum lebih baik: daftarkan ke DJKI
- Pastikan semua open source library yang digunakan sesuai lisensinya

### 4.3 Lisensi Open Source — Compliance

```
Audit lisensi dependency sebelum launch:

✅ MIT License — Bebas digunakan untuk komersial
   - Fiber v2, Tailwind CSS, React, sebagian besar Go packages

✅ Apache 2.0 — Bebas untuk komersial, dengan attribution
   - gRPC, Protocol Buffers

⚠️ GPL / LGPL — PERHATIAN: bisa "menulari" kode Anda
   - Cek setiap dependency yang pakai GPL
   - LGPL (dynamic linking): biasanya aman
   - GPL (static linking): bisa bermasalah

❌ AGPL — Hindari di backend (mengharuskan kode dibuka)

Tools: govulncheck, npm audit, flutter pub audit
```

---

## 5. Kontrak Karyawan & Kontraktor

### 5.1 Freelancer / Kontraktor

```
Kontrak freelancer WAJIB mencakup:

1. KEPEMILIKAN KODE
   "Semua kode yang dibuat untuk proyek ini adalah milik PT Extended Synaptic Indonesia.
    Kontraktor tidak menyimpan salinan setelah kontrak berakhir."

2. NON-DISCLOSURE AGREEMENT (NDA)
   "Tidak boleh mengungkapkan informasi rahasia perusahaan selama dan
    setelah masa kontrak."

3. NON-COMPETE (opsional, 1 tahun untuk key developer)
   "Tidak membuat produk serupa/kompetitor langsung selama 1 tahun."

4. DELIVERABLES
   Spesifikasi jelas apa yang harus diselesaikan.

5. PEMBAYARAN
   Jumlah, jadwal, kondisi pembayaran.

6. TERMINASI
   Kondisi terminate kontrak dua arah.
```

### 5.2 Karyawan Tetap

- Ikuti UU Ketenagakerjaan No. 13/2003 dan UU Cipta Kerja No. 11/2020
- PKWT (Karyawan Kontrak): maksimal 2 tahun, dapat diperpanjang sekali
- PKWTT (Karyawan Tetap): setelah masa percobaan 3 bulan
- Wajib daftarkan ke BPJS Ketenagakerjaan dan Kesehatan

---

## 6. Kontrak dengan Pihak Ketiga

### 6.1 Payment Gateway (Xendit/Midtrans)

```
Baca dan pahami:
[ ] Merchant Agreement Xendit/Midtrans
[ ] MDR (Merchant Discount Rate) per payment method
[ ] Settlement schedule (kapan dana masuk ke rekening)
[ ] Chargeback policy
[ ] PCI DSS compliance requirements
[ ] AML/KYC requirements untuk merchant

Penting: Pastikan ToS Xendit/Midtrans mengizinkan 
         penggunaan untuk model SaaS aggregator
```

### 6.2 Cloud Provider (DigitalOcean/AWS)

- Baca Data Processing Agreement (DPA)
- Pastikan sesuai UU PDP (data residency di Indonesia atau negara yang diakui)
- SLA uptime yang dijanjikan
- Kebijakan terminasi dan portabilitas data

### 6.3 Firebase / Google

- Google Cloud DPA — pastikan sesuai UU PDP
- Firebase quota limits dan pricing tier

---

## 7. Compliance Checklist Pre-Launch

```
LEGAL & CORPORATE:
[ ] PT sudah didirikan dan semua dokumen lengkap
[ ] NPWP PT aktif
[ ] NIB (OSS) sudah terbit
[ ] Rekening bank atas nama PT

MEREK & HKI:
[ ] Pendaftaran merek XynPOS ke DJKI (bisa sambil jalan)
[ ] Audit lisensi open source selesai

DOKUMEN LEGAL:
[ ] Terms of Service final (review lawyer)
[ ] Privacy Policy final
[ ] Refund Policy final
[ ] Semua dipublikasikan di website sebelum sign-up

DATA PROTECTION:
[ ] Privacy Policy mencakup semua yang diminta UU PDP
[ ] Mekanisme consent saat sign-up
[ ] Right to erasure endpoint sudah ada
[ ] Data export endpoint sudah ada
[ ] Enkripsi data sensitif sudah implemented

PAYMENT:
[ ] Merchant agreement Xendit/Midtrans sudah ditandatangani
[ ] KYC/verifikasi merchant selesai
[ ] Settlement ke rekening PT (bukan pribadi)
[ ] Sistem invoice untuk subscription sudah siap

KONTRAKTOR:
[ ] Semua kontraktor sudah tandatangani kontrak + NDA
[ ] IP assignment clause sudah ada
```

---

## 8. Risk Register Legal

| Risiko | Kemungkinan | Dampak | Mitigasi |
|--------|------------|--------|---------|
| Merek XynPOS sudah dipakai pihak lain | Rendah | Tinggi | Daftarkan merek segera, cek DJKI |
| Data breach → tuntutan UU PDP | Sedang | Sangat Tinggi | Security-first architecture, incident response plan |
| Pelanggaran lisensi open source | Rendah | Sedang | Audit lisensi sebelum launch |
| Karyawan/kontraktor klaim IP | Rendah | Tinggi | Kontrak yang jelas dengan IP assignment |
| Tenant gunakan XynPOS untuk aktivitas ilegal | Sedang | Tinggi | ToS yang melarang, mekanisme suspend akun |
| Regulasi payment berubah | Sedang | Sedang | Ikuti newsletter BI/OJK, punya tim legal partner |
| Sengketa dengan tenant enterprise | Rendah | Sedang | SLA agreement yang jelas, mediasi sebelum litigasi |

---

## 9. Penasihat Hukum yang Disarankan

Untuk startup di Jawa Tengah/Indonesia:

| Kebutuhan | Rekomendasi Cari |
|-----------|-----------------|
| Pendirian PT | Notaris lokal (cepat, murah) |
| ToS & Privacy Policy | Startup law firm dengan pengalaman SaaS |
| HKI (Merek) | Konsultan HKI terdaftar DJKI |
| HR Law | Konsultan HR/hukum ketenagakerjaan |
| Pajak | Konsultan pajak / Kantor Akuntan Publik |

**Budget awal legal:** Rp 15–25 juta (pendirian + dokumen dasar)

---

*Blueprint ini inline dengan: BP-02 (Financial/Billing), BP-10 (Security/UU PDP), BP-15 (GTM)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
*⚠️ Ini bukan nasihat hukum. Konsultasikan dengan lawyer berlisensi.*
