# XynPOS — Blueprint 02: Financial & Subscription Mechanism
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Perbandingan Model Bisnis Subscription

Sebelum menetapkan model, berikut adalah analisis mendalam tiga model yang paling relevan untuk XynPOS:

### 1.1 Model A — Freemium + Paid Tiers

**Konsep:** Ada plan gratis permanen dengan fitur terbatas. User upgrade ke paid untuk fitur lebih.

| Aspek | Detail |
|-------|--------|
| **Struktur** | Free → Starter → Pro → Business → Enterprise |
| **Revenue trigger** | Fitur premium, limit transaksi, jumlah outlet/user |
| **Contoh produk** | Kasir Pintar, Moka (dulu), Notion, Trello |

**✅ Pros:**
- Barrier masuk nol → akuisisi user massal, terutama UMKM
- Word-of-mouth tinggi karena bisa dicoba gratis
- Data pengguna gratis bisa dianalisis untuk product improvement
- Konversi alami saat bisnis berkembang (product-led growth)
- Cocok untuk pasar Indonesia yang price-sensitive

**❌ Cons:**
- Free users makan biaya server tanpa revenue
- Risiko "stuck di free forever" — konversi bisa rendah (industri: 2–5%)
- Support beban tinggi dari free users
- Investor sering tanya "kapan monetize?"
- Butuh skala besar sebelum profitable

**📊 Estimasi Konversi:** 2–5% free → paid (industri SaaS)

---

### 1.2 Model B — Trial Period + Paid Tiers

**Konsep:** Semua fitur bisa dicoba gratis selama 14–30 hari, setelah itu harus bayar.

| Aspek | Detail |
|-------|--------|
| **Struktur** | Trial 14/30 hari (full akses) → Pilih plan berbayar |
| **Revenue trigger** | Habisnya masa trial |
| **Contoh produk** | Shopify, Xero, Lightspeed, iSeller |

**✅ Pros:**
- User mencoba full experience → konversi lebih tinggi (15–25%)
- Tidak ada beban free tier permanen
- Revenue predictable sejak awal
- Memaksa user untuk evaluasi dan commit
- Lebih mudah untuk unit economics

**❌ Cons:**
- Barrier lebih tinggi — user harus input data lalu takut hilang setelah trial
- Kehilangan "viral free" user yang recommend ke orang lain
- Di Indonesia, banyak yang akan buat akun baru terus (trial abuse)
- Perlu anti-abuse mechanism (KTP/NPWP verification)
- Kurang cocok untuk segmen T1 (UMKM mikro)

**📊 Estimasi Konversi:** 15–25% trial → paid

---

### 1.3 Model C — Pay-as-You-Go (Usage-Based)

**Konsep:** Bayar berdasarkan apa yang digunakan — per transaksi, per outlet aktif, per fitur.

| Aspek | Detail |
|-------|--------|
| **Struktur** | Base fee kecil + charge per transaksi / per outlet / per fitur |
| **Revenue trigger** | Volume aktivitas bisnis |
| **Contoh produk** | Stripe, Twilio, AWS, Toast POS (partial) |

**✅ Pros:**
- Sangat adil — bayar sesuai pakai
- Cocok untuk bisnis musiman (misal: event organizer)
- Revenue naik otomatis seiring pertumbuhan pelanggan
- Low barrier masuk

**❌ Cons:**
- Revenue tidak predictable → sulit untuk financial planning
- User bisa "shock" dengan tagihan tiba-tiba
- Kompleks untuk billing system
- UMKM Indonesia tidak suka model ini (prefer fixed cost)
- Sulit menjelaskan ke investor early stage

**📊 Best for:** SaaS B2B dengan volume tinggi dan well-educated market

---

### 1.4 Rekomendasi: Model Hybrid (A + B)

**Untuk XynPOS, rekomendasi adalah model Hybrid:**

> **Freemium terbatas + Trial Pro + Paid Tiers**

**Mekanisme:**
1. **Free Plan permanen** — sangat terbatas (1 outlet, max 100 transaksi/bulan, 1 user kasir)
2. **Trial Pro 30 hari** — saat signup, semua user otomatis trial plan Pro (full akses)
3. **Setelah 30 hari** — auto-downgrade ke Free kecuali upgrade
4. **Paid Tiers** — Starter, Pro, Business, Enterprise

**Alasan hybrid ini terbaik untuk XynPOS:**
- UMKM Indonesia bisa mulai gratis → akuisisi massal
- Trial Pro 30 hari membuat mereka "addicted" ke fitur premium
- Setelah trial habis dan downgrade, mereka akan merasa "kehilangan" → konversi meningkat
- Anti-abuse: free plan sangat terbatas (100 transaksi saja)

---

## 2. Pricing Tiers XynPOS

### 2.1 Struktur Plan

| Plan | Harga/Bulan | Target Segmen | Outlets | Users | Transaksi/Bulan |
|------|-------------|---------------|---------|-------|-----------------|
| **Free** | Rp 0 | T1 Mikro / Coba-coba | 1 | 1 kasir | 100 |
| **Starter** | Rp 149.000 | T1–T2 UMKM | 1 | 3 | Unlimited |
| **Pro** | Rp 349.000 | T2 Kecil-Menengah | 3 | 10 | Unlimited |
| **Business** | Rp 749.000 | T3 Menengah | 10 | 30 | Unlimited |
| **Enterprise** | Custom (min Rp 2.000.000) | T4 Besar/Chain | Unlimited | Unlimited | Unlimited |

### 2.2 Diskon Tahunan

| Plan | Bulanan | Tahunan (diskon 20%) | Saving |
|------|---------|----------------------|--------|
| Starter | Rp 149.000 | Rp 1.430.400 (Rp 119.200/bln) | Rp 357.600/tahun |
| Pro | Rp 349.000 | Rp 3.350.400 (Rp 279.200/bln) | Rp 837.600/tahun |
| Business | Rp 749.000 | Rp 7.190.400 (Rp 599.200/bln) | Rp 1.797.600/tahun |

### 2.3 Feature Matrix per Plan

| Fitur | Free | Starter | Pro | Business | Enterprise |
|-------|------|---------|-----|----------|------------|
| Transaksi penjualan | 100/bln | Unlimited | Unlimited | Unlimited | Unlimited |
| Outlet / lokasi | 1 | 1 | 3 | 10 | Unlimited |
| Akun kasir | 1 | 3 | 10 | 30 | Unlimited |
| Manajemen produk | 50 item | 500 item | Unlimited | Unlimited | Unlimited |
| Laporan dasar | ✅ | ✅ | ✅ | ✅ | ✅ |
| Laporan advanced & custom | ❌ | ❌ | ✅ | ✅ | ✅ |
| Manajemen inventori | Basic | Basic | Advanced | Advanced | Advanced |
| Purchase Order | ❌ | ❌ | ✅ | ✅ | ✅ |
| Kitchen Display System | ❌ | ❌ | ✅ | ✅ | ✅ |
| Customer loyalty & poin | ❌ | Basic | Advanced | Advanced | Custom |
| Hutang pelanggan (piutang) | ❌ | ✅ | ✅ | ✅ | ✅ |
| Multi-payment method | ❌ | ✅ | ✅ | ✅ | ✅ |
| QRIS terintegrasi | ❌ | ✅ | ✅ | ✅ | ✅ |
| Cetak struk thermal | ✅ | ✅ | ✅ | ✅ | ✅ |
| Offline mode | ✅ | ✅ | ✅ | ✅ | ✅ |
| API access | ❌ | ❌ | Read-only | Full | Full + Webhook |
| White label | ❌ | ❌ | ❌ | ❌ | ✅ |
| Dedicated support | ❌ | Email | Email+Chat | Priority | Dedicated CSM |
| SLA uptime | Best effort | 99.5% | 99.9% | 99.9% | 99.99% |
| Integrasi XYN CRM | ❌ | ❌ | ✅ | ✅ | ✅ |
| Integrasi XYN ERP | ❌ | ❌ | ❌ | ✅ | ✅ |

### 2.4 Add-On (Opsional, semua plan kecuali Free)

| Add-On | Harga | Deskripsi |
|--------|-------|-----------|
| Outlet tambahan | Rp 99.000/outlet/bln | Melebihi limit plan |
| User kasir tambahan | Rp 29.000/user/bln | Melebihi limit plan |
| SMS Notifikasi | Rp 49.000/bln (1000 SMS) | Blast promo ke pelanggan |
| Advanced Analytics | Rp 149.000/bln | Prediksi stok, tren penjualan |
| e-Faktur Integration | Rp 99.000/bln | Integrasi e-Faktur pajak |
| Hardware Bundle | Harga terpisah | Printer, scanner, cash drawer |

---

## 3. Struktur Biaya (HPP — Harga Pokok Produk)

### 3.1 Biaya Infrastruktur Cloud (Monthly, per Skala)

#### Fase 1: 0–500 tenant (Bulan 1–6)

| Komponen | Provider | Spesifikasi | Biaya/Bulan (est.) |
|----------|----------|-------------|---------------------|
| **App Server** | DigitalOcean / Vultr | 2x VPS 4vCPU 8GB RAM | Rp 600.000 |
| **Database Primary** | DigitalOcean Managed PostgreSQL | 2vCPU 4GB, 50GB SSD | Rp 450.000 |
| **Database Replica** | DigitalOcean | Read replica | Rp 300.000 |
| **Redis Cache** | DigitalOcean Managed Redis | 1GB | Rp 150.000 |
| **Object Storage (S3)** | Cloudflare R2 / DO Spaces | 50GB + bandwidth | Rp 75.000 |
| **Load Balancer** | DigitalOcean | 1 LB | Rp 150.000 |
| **CDN** | Cloudflare Free/Pro | — | Rp 0–300.000 |
| **Mail Server** | Resend / Mailgun | 10.000 email/bln | Rp 150.000 |
| **Firebase** | Google Firebase | Auth + FCM push notif | Rp 0–200.000 |
| **Monitoring** | Grafana Cloud Free | — | Rp 0 |
| **SSL/Domain** | Cloudflare | wildcard SSL | Rp 50.000 |
| **Backup** | DigitalOcean Snapshots | Daily backup | Rp 100.000 |
| **TOTAL FASE 1** | | | **~Rp 2.325.000/bln** |

#### Fase 2: 500–5.000 tenant (Bulan 7–18)

| Komponen | Spesifikasi | Biaya/Bulan (est.) |
|----------|-------------|---------------------|
| App Server (K8s cluster) | 3 node × 8vCPU 16GB | Rp 4.500.000 |
| Database (HA cluster) | Primary + 2 Replica | Rp 2.000.000 |
| Redis Cluster | 3 node | Rp 600.000 |
| Object Storage | 500GB | Rp 300.000 |
| Message Queue (RabbitMQ/NATS) | Managed | Rp 500.000 |
| Mail Server (volume lebih) | 100.000 email/bln | Rp 600.000 |
| Monitoring (Grafana + Loki) | Self-hosted | Rp 300.000 |
| CDN + DDoS protection | Cloudflare Pro | Rp 300.000 |
| **TOTAL FASE 2** | | **~Rp 9.100.000/bln** |

#### Fase 3: 5.000–50.000 tenant (Tahun 2–3)

| Komponen | Biaya/Bulan (est.) |
|----------|--------------------|
| Multi-region Kubernetes | Rp 25.000.000 |
| Managed DB cluster (multi-region) | Rp 12.000.000 |
| CDN + Edge | Rp 3.000.000 |
| Storage + Backup | Rp 5.000.000 |
| Mail + SMS | Rp 4.000.000 |
| Security (WAF, pentest) | Rp 5.000.000 |
| **TOTAL FASE 3** | **~Rp 54.000.000/bln** |

### 3.2 Biaya Tim (Human Cost)

#### Setup Awal (Tahun 1 — Tim Kecil 2–4 orang)

| Peran | Status | Biaya/Bulan |
|-------|--------|-------------|
| Founder/Lead Backend (Go) | Founder (equity) | — |
| Frontend/Flutter Developer | Freelance/Part-time | Rp 5.000.000 |
| UI/UX Designer | Freelance/Project | Rp 3.000.000 |
| QA Tester | Part-time | Rp 2.000.000 |
| Customer Support | Part-time | Rp 2.500.000 |
| **Total Tim** | | **~Rp 12.500.000/bln** |

#### Scale-up (Tahun 2 — Tim 6–8 orang)

| Peran | Biaya/Bulan |
|-------|-------------|
| 2x Backend Go Developer | Rp 20.000.000 |
| 2x Flutter Developer | Rp 18.000.000 |
| 1x DevOps/SRE | Rp 12.000.000 |
| 1x Product Manager | Rp 10.000.000 |
| 2x Customer Success | Rp 10.000.000 |
| 1x Marketing | Rp 7.000.000 |
| **Total Tim** | **~Rp 77.000.000/bln** |

### 3.3 Biaya Lain-lain

| Item | Biaya/Bulan |
|------|-------------|
| Domain & SSL | Rp 50.000 |
| Tools (GitHub, Figma, Jira, Notion) | Rp 1.500.000 |
| Legal & Compliance | Rp 500.000 |
| Marketing & Iklan | Rp 3.000.000–10.000.000 |
| Pajak & Admin perusahaan | Rp 500.000 |

---

## 4. HPP per Plan (Cost of Revenue)

### Asumsi Biaya Infrastruktur per Tenant Aktif

| Skala | Total Infra/Bln | Tenant Aktif | Biaya Infra/Tenant/Bln |
|-------|----------------|--------------|------------------------|
| Fase 1 (500 tenant) | Rp 2.325.000 | 500 | **Rp 4.650** |
| Fase 2 (3.000 tenant) | Rp 9.100.000 | 3.000 | **Rp 3.033** |
| Fase 3 (30.000 tenant) | Rp 54.000.000 | 30.000 | **Rp 1.800** |

### HPP per Plan (Include Support Cost)

| Plan | Harga Jual | Biaya Infra | Biaya Support | Total HPP | Gross Margin |
|------|-----------|-------------|---------------|-----------|--------------|
| Free | Rp 0 | Rp 4.650 | Rp 2.000 | Rp 6.650 | **-Rp 6.650** |
| Starter | Rp 149.000 | Rp 8.000 | Rp 5.000 | Rp 13.000 | **91,3%** |
| Pro | Rp 349.000 | Rp 15.000 | Rp 10.000 | Rp 25.000 | **92,8%** |
| Business | Rp 749.000 | Rp 30.000 | Rp 20.000 | Rp 50.000 | **93,3%** |
| Enterprise | Rp 2.000.000+ | Custom | Rp 100.000+ | Custom | **~90%** |

> **Catatan:** Gross margin SaaS yang baik adalah >70%. XynPOS memiliki margin sangat sehat di atas 90% untuk paid plans. Biaya terbesar justru di SDM (tim), bukan infrastruktur.

---

## 5. Break-Even Point (BEP) Analysis

### 5.1 Asumsi BEP

- **Modal awal:** Rp 150.000.000 (tengah range 50–200 juta)
- **Fixed cost/bulan (Fase 1):** Rp 15.000.000 (infra + tim minimal + overhead)
- **Average Revenue per User (ARPU):** diasumsikan dari mix plan

### 5.2 Distribusi User Mix (Proyeksi Konservatif)

| Plan | % dari Paid Users | ARPU Kontribusi |
|------|-------------------|-----------------|
| Free | 70% (tidak bayar) | Rp 0 |
| Starter | 15% | Rp 22.350 (15% × Rp 149K) |
| Pro | 10% | Rp 34.900 (10% × Rp 349K) |
| Business | 4% | Rp 29.960 (4% × Rp 749K) |
| Enterprise | 1% | Rp 20.000 (1% × Rp 2.000K) |
| **Blended ARPU** | 100% | **~Rp 107.210/user aktif** |

*Atau jika hanya dari paid user (30%):*
- **Paid ARPU:** Rp 357.367/paid user

### 5.3 BEP Calculation

| Metrik | Nilai |
|--------|-------|
| Fixed Cost / Bulan | Rp 15.000.000 |
| Variable Cost / Paid User | Rp 13.000 (HPP Starter) |
| Contribution Margin / Paid User | Rp 149.000 – Rp 13.000 = Rp 136.000 |
| **BEP Paid Users (Starter semua)** | 15.000.000 ÷ 136.000 = **~111 paid users** |
| **BEP dengan blended plan mix** | ~70 paid users |

**BEP Paid Users: ~70–111 paid subscribers = sangat achievable!**

### 5.4 Proyeksi Revenue & BEP Timeline

| Bulan | Total Tenant | Paid Tenant (30%) | MRR (est.) | Total Cost | Net |
|-------|-------------|-------------------|------------|-----------|-----|
| M1 | 50 | 15 | Rp 2.625.000 | Rp 15.000.000 | -Rp 12.375.000 |
| M3 | 200 | 60 | Rp 10.500.000 | Rp 16.000.000 | -Rp 5.500.000 |
| M6 | 500 | 150 | Rp 26.250.000 | Rp 17.325.000 | **+Rp 8.925.000** ✅ |
| M9 | 1.000 | 300 | Rp 52.500.000 | Rp 22.000.000 | +Rp 30.500.000 |
| M12 | 2.000 | 600 | Rp 105.000.000 | Rp 35.000.000 | +Rp 70.000.000 |
| M18 | 5.000 | 1.500 | Rp 262.500.000 | Rp 60.000.000 | +Rp 202.500.000 |

> **Estimasi BEP: Bulan ke 5–6** dengan ~150 paid users. Modal awal Rp 150 juta cukup untuk cover 5–6 bulan burn rate.

### 5.5 ARR (Annual Recurring Revenue) Proyeksi

| Tahun | Paid Tenant | MRR | ARR |
|-------|------------|-----|-----|
| Y1 End | 600 | Rp 105.000.000 | Rp 1.260.000.000 |
| Y2 End | 3.000 | Rp 525.000.000 | Rp 6.300.000.000 |
| Y3 End | 10.000 | Rp 1.750.000.000 | Rp 21.000.000.000 |

---

## 6. Modal Awal — Kebutuhan & Alokasi

### 6.1 Rincian Kebutuhan Modal (Fase Pre-Launch hingga Month 6)

| Kategori | Item | Biaya (Rp) |
|----------|------|-----------|
| **Infrastruktur Setup** | Server + domain + SSL setup | 5.000.000 |
| **Infrastruktur Operasional** | Cloud server 6 bulan (Fase 1) | 13.950.000 |
| **Development** | Flutter dev freelance 6 bulan | 30.000.000 |
| **Development** | UI/UX designer 3 bulan | 9.000.000 |
| **Development** | QA tester 3 bulan | 6.000.000 |
| **Legal** | Pendirian PT/CV, NPWP, TDP | 8.000.000 |
| **Marketing** | Iklan digital 6 bulan | 18.000.000 |
| **Marketing** | Konten, desain, website | 5.000.000 |
| **Tools & Lisensi** | GitHub, Figma, dsb 6 bulan | 9.000.000 |
| **Hardware Demo** | 1 set demo hardware POS | 5.000.000 |
| **Operasional** | Listrik, internet, co-working | 6.000.000 |
| **Buffer Darurat** | 20% contingency | 23.990.000 |
| **TOTAL MODAL MINIMUM** | | **~Rp 143.940.000** |
| **TOTAL MODAL IDEAL** | | **Rp 175.000.000–200.000.000** |

### 6.2 Breakdown per Kategori

```
Modal Awal Rp 150.000.000 Alokasi:
├── Infrastruktur (13%)       : Rp 18.950.000
├── Development/SDM (30%)     : Rp 45.000.000
├── Marketing (15%)           : Rp 23.000.000
├── Legal & Admin (5%)        : Rp 8.000.000
├── Tools & Software (6%)     : Rp 9.000.000
├── Hardware Demo (3%)        : Rp 5.000.000
├── Operasional (4%)          : Rp 6.000.000
└── Buffer/Contingency (20%)  : Rp 35.050.000
```

---

## 7. Payment Gateway & Billing System

### 7.1 Payment Method untuk Subscription

| Method | Provider | Fee per Transaksi | Keterangan |
|--------|----------|-------------------|-----------|
| Transfer Bank / VA | Xendit | Rp 4.000–5.000 | Paling umum di Indonesia |
| Kartu Kredit/Debit | Midtrans | 2–3% | Untuk segmen menengah ke atas |
| QRIS | Xendit / Midtrans | 0.7% | Scan QR untuk bayar langganan |
| GoPay / OVO / Dana | Xendit | 1.5–2% | e-Wallet |
| Kartu Kredit Global | Stripe | 2.9% + $0.30 | Untuk Enterprise customer global |

### 7.2 Subscription Billing Flow

```
User memilih plan
       ↓
Xendit/Midtrans membuat recurring charge
       ↓
Auto-debit setiap tanggal billing
       ↓
Jika sukses → perpanjang subscription
       ↓
Jika gagal → grace period 3 hari → reminder email/WA
       ↓
Setelah 3 hari gagal → downgrade ke Free
       ↓
Jika bayar dalam 7 hari → reaktivasi + tidak kehilangan data
       ↓
Setelah 30 hari non-payment → data retention policy berlaku
```

### 7.3 Kebijakan Refund & Upgrade/Downgrade

| Skenario | Kebijakan |
|----------|-----------|
| Upgrade mid-cycle | Pro-rate sisa hari, langsung aktif |
| Downgrade mid-cycle | Berlaku di awal periode berikutnya |
| Cancel | Data tersimpan 30 hari, bisa reaktivasi |
| Refund | Tidak ada refund kecuali technical issue >24 jam |
| Garansi uang kembali | 7 hari untuk plan baru pertama kali |

---

## 8. Metrik Keuangan Kunci yang Dipantau

| Metrik | Target Y1 | Target Y2 | Formula |
|--------|-----------|-----------|---------|
| **MRR** | Rp 100 juta | Rp 500 juta | Sum monthly recurring |
| **ARR** | Rp 1,2 miliar | Rp 6 miliar | MRR × 12 |
| **ARPU** | Rp 175.000 | Rp 200.000 | MRR ÷ paid users |
| **Churn Rate** | <5%/bln | <3%/bln | Churned ÷ total user |
| **LTV** | Rp 3,5 juta | Rp 6 juta | ARPU ÷ churn rate |
| **CAC** | <Rp 500.000 | <Rp 300.000 | Marketing spend ÷ new users |
| **LTV:CAC Ratio** | >7:1 | >20:1 | LTV ÷ CAC |
| **Gross Margin** | >85% | >90% | (Revenue - COGS) ÷ Revenue |
| **Payback Period** | <6 bulan | <3 bulan | CAC ÷ ARPU |
| **Free-to-Paid Conv.** | >5% | >8% | Paid ÷ Free signups |

---

## 9. Skenario Sensitivitas

### Skenario Optimis (Konversi 10%, Churn 2%)
- BEP: Bulan ke-4
- ARR Y1: Rp 2,1 miliar
- Profit Y1: Rp 800 juta

### Skenario Moderat (Konversi 5%, Churn 5%)
- BEP: Bulan ke-6
- ARR Y1: Rp 1,2 miliar
- Profit Y1: Rp 300 juta

### Skenario Konservatif (Konversi 3%, Churn 8%)
- BEP: Bulan ke-9
- ARR Y1: Rp 600 juta
- Burn rate modal habis: Bulan ke-10 (perlu fundraising atau revenue)

> **Rekomendasi:** Siapkan modal untuk 9–12 bulan burn rate, bukan 6 bulan. Buffer untuk skenario konservatif adalah kunci survival.

---

*Blueprint ini inline dengan: BP-01 (Target Market), BP-03 (MVP), BP-15 (GTM)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
