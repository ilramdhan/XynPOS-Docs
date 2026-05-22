---
skill_id: SKILL-10
name: XynPOS Sprint Planning & Estimation
category: shared
description: Skill untuk estimasi effort, task breakdown, sprint planning, dan roadmap management
version: 1.0.0
applies_to: [planning, estimation, sprint, roadmap]
depends_on: [SKILL-00]
---

# SKILL-10: Sprint Planning & Estimation

## Team Capacity

```
Solo founder/lead dev:  ~20 SP / sprint (2 minggu)
2 BE + 1 FE:           ~40 SP / sprint
2 BE + 2 FE + 1 Mobile: ~60 SP / sprint

Buffer: selalu estimasi dengan 20% overhead untuk unknowns
```

## Story Points Scale (Fibonacci)

```
1  SP = < 2 jam      (trivial: typo fix, config tweak, simple CRUD field)
2  SP = ~4 jam       (simple endpoint, basic component)
3  SP = ~1 hari      (feature dengan 1-2 komponen, basic test)
5  SP = ~2-3 hari    (feature dengan multiple components, unit tests)
8  SP = ~1 minggu    (kompleks feature, multi-service, integration test)
13 SP = > 1 minggu   (sangat kompleks, butuh research atau design)
21 SP = terlalu besar → HARUS dipecah jadi beberapa tiket
```

## Definition of Done (DoD)

```
Sebuah task dianggap DONE hanya jika semua ini terpenuhi:
✓ Unit test coverage >= 70% untuk kode baru
✓ API endpoint terdokumentasi di Swagger (jika ada endpoint baru)
✓ Berjalan di Android, iOS, dan Web (jika ada UI)
✓ Offline mode tested (jika ada POS feature)
✓ Code review approved (minimal 1 reviewer)
✓ QA sign-off di staging environment
✓ Tidak ada P0/P1 bug open
✓ Documentation diupdate jika ada perubahan arsitektur
```

## MVP Sprint Breakdown (Referensi)

```
PHASE 1: MVP Development (12 minggu = 6 sprint)

Sprint 1-2 (Bulan 1):     FOUNDATION
  Auth service (register, login, JWT, refresh, OTP)       8 SP
  Tenant service (create, schema provisioning)             5 SP
  Docker local dev environment                             3 SP
  CI/CD pipeline basic (lint, test, build)                 3 SP
  Total: 19 SP

Sprint 3-4 (Bulan 2):     PRODUCT MANAGEMENT  
  Product CRUD + kategori + variant                        8 SP
  Modifier groups + modifiers                              5 SP
  Barcode scan support                                     3 SP
  Stock management basic                                   5 SP
  Total: 21 SP

Sprint 5-6 (Bulan 2-3):   POS CORE
  POS screen (web + mobile)                               13 SP
  Cart management + checkout flow                          8 SP
  Hold order + table management (F&B)                      5 SP
  Offline mode (Hive + sync)                               8 SP
  Total: 34 SP (butuh 2 sprint)

Sprint 7-8 (Bulan 3):     PAYMENT + INVENTORY
  Cash payment + kembalian                                  3 SP
  QRIS dynamic (Xendit integration)                        8 SP
  Thermal printer (BT + USB)                               5 SP
  Inventory tracking + stock alert                         5 SP
  Total: 21 SP

Sprint 9-10 (Bulan 3-4):  REPORTS + USER MGMT
  Dashboard + sales reports                                8 SP
  Inventory report + laporan kasir                         5 SP
  User management + RBAC basic                             5 SP
  Customer management + loyalty points basic               5 SP
  Total: 23 SP

Sprint 11-12 (Bulan 4):   POLISH + BETA
  Bug fix + QA cycle                                       8 SP
  Performance optimization                                  5 SP
  Beta testing dengan 20-50 users                         ongoing
  Onboarding flow + welcome email                          3 SP
  Total: 16+ SP
```

## Post-MVP Wave Estimates

```
Wave 1 (Bulan 7-8 post-launch):   ~35 SP total
  Purchase Order (PO)              13 SP
  Kitchen Display System (KDS)     13 SP
  Shift Management                  5 SP
  Stocktake                         8 SP

Wave 2 (Bulan 9-10):              ~45 SP
  Recipe & Ingredient tracking     13 SP
  Reservasi & Waitlist             13 SP
  QR Self-Order                    13 SP
  Happy Hour pricing                5 SP

Wave 3 (Bulan 11-12):             ~40 SP
  Promo & Campaign management      13 SP
  Batch & Expired tracking         13 SP
  Price List per customer           8 SP
  Consignment                       8 SP

Wave 4 (Year 2 Q1):               ~60 SP
  Multi-outlet Dashboard           13 SP
  e-Faktur integration             21 SP (sangat kompleks)
  RBAC Advanced                    13 SP
  API & Webhook Platform           13 SP

Wave 5 (Year 2 Q2-Q3):           ~80+ SP
  XYN CRM Integration              21 SP
  Marketplace Integration          34 SP (per marketplace)
  WhatsApp Business API            13 SP
```

## Task Breakdown Template

```markdown
## [FEAT-XXX] {Judul Fitur}

**User Story:**
Sebagai {role}, saya ingin {action} agar {benefit}

**Acceptance Criteria:**
- [ ] AC 1: {specific, testable condition}
- [ ] AC 2: ...
- [ ] AC 3: ...

**Technical Tasks:**
Backend:
  - [ ] Database schema / migration (X SP)
  - [ ] Repository + usecase (X SP)
  - [ ] HTTP endpoint (X SP)
  - [ ] Unit tests (included dalam SP atas)

Frontend (Web):
  - [ ] UI component (X SP)
  - [ ] API integration (X SP)

Mobile:
  - [ ] Flutter screen (X SP)
  - [ ] Offline support (X SP)

**Total Estimate:** X SP
**Dependencies:** Butuh FEAT-YYY selesai dulu
**Plan:** Sprint N (tanggal mulai - selesai)
```

## Priority Framework (MoSCoW)

```
MUST (P0)   = Blocker — tanpa ini product tidak bisa dipakai
SHOULD (P1) = Important — harus ada tapi ada workaround
COULD (P2)  = Nice to have — tambahkan jika masih ada kapasitas
WON'T (P3)  = Tidak di sprint ini — backlog untuk nanti
```

## Velocity Tracking

```
Catat setiap sprint:
- Committed SP: X
- Completed SP: Y
- Velocity: Y/X%
- Blockers: {list}
- Learnings: {what to improve}

Target velocity setelah 3 sprint: 80%+ completion rate
```
