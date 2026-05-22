# XynPOS Claude Skills — Usage Guide
> Extended Synaptic | For All Developers

---

## Apa itu Skills?

Skills adalah **instruksi kontekstual** yang membuat Claude memahami XynPOS secara mendalam tanpa perlu penjelasan ulang setiap sesi. Dengan skill yang tepat:

- Claude langsung tahu stack, pattern, dan rules yang dipakai
- Tidak perlu jelaskan "kita pakai Go + Fiber + schema-per-tenant" berulang kali
- Response lebih relevan dan langsung applicable
- Code yang dihasilkan sudah sesuai dengan konvensi XynPOS

---

## Daftar Skills

| ID | Nama | Kategori | Dipakai Untuk |
|----|------|----------|---------------|
| [SKILL-00](../shared/SKILL-00-project-context.md) | Project Context | Shared | **Master skill — load pertama selalu** |
| [SKILL-01](../backend/SKILL-01-go-backend.md) | Go Backend | Backend | Coding session backend Go |
| [SKILL-02](../backend/SKILL-02-database-sql.md) | Database & SQL | Backend | Query, schema, migration |
| [SKILL-03](../frontend/SKILL-03-nextjs-frontend.md) | Next.js Frontend | Frontend | Web dashboard & POS |
| [SKILL-04](../mobile/SKILL-04-flutter-mobile.md) | Flutter Mobile | Mobile | Mobile app development |
| [SKILL-05](../infrastructure/SKILL-05-devops-infra.md) | DevOps & Infra | Infra | Docker, CI/CD, K8s, Terraform |
| [SKILL-06](../shared/SKILL-06-api-design.md) | API Design | Shared | Design endpoint, review API |
| [SKILL-07](../shared/SKILL-07-security-review.md) | Security Review | Shared | Code security audit, UU PDP |
| [SKILL-08](../shared/SKILL-08-code-review.md) | Code Review | Shared | Review PR semua stack |
| [SKILL-09](../shared/SKILL-09-documentation.md) | Documentation | Shared | Update blueprint, ADR, docs |
| [SKILL-10](../shared/SKILL-10-sprint-planning.md) | Sprint Planning | Shared | Estimasi, task breakdown |

---

## Cara Setup di Claude.ai

### Step 1: Buat Project

1. Buka **claude.ai**
2. Klik **Projects** di sidebar kiri
3. Klik **+ New Project**
4. Nama: `XynPOS Development`
5. Klik **Create**

### Step 2: Tambahkan Project Instructions

Di halaman project:
1. Klik **Project Settings** (atau icon gear ⚙️)
2. Scroll ke **Custom Instructions** atau **Project Instructions**
3. Copy-paste isi SKILL-00 (wajib) + skill lain yang relevan untuk role kamu

### Step 3: Upload Reference Files (Opsional tapi Sangat Membantu)

Upload file-file ini sebagai **project knowledge**:
- `docs/blueprints/developer/13-CLAUDE-ai-instructions.md` ← **Paling penting**
- `docs/blueprints/technical/05-tech-stack-blueprint.md`
- `docs/blueprints/technical/06-system-architecture-blueprint.md`
- `docs/blueprints/developer/20-dev-rules-backend.md` (untuk BE dev)
- `docs/blueprints/developer/21-dev-rules-frontend.md` (untuk FE dev)
- `docs/blueprints/developer/22-dev-rules-mobile.md` (untuk Mobile dev)

---

## Kombinasi Skills per Role

### 👨‍💻 Backend Developer (Go)

```
Project Instructions:
  [SKILL-00] Project Context   ← Always first
  [SKILL-01] Go Backend        ← Primary skill
  [SKILL-02] Database & SQL    ← For DB work
  [SKILL-06] API Design        ← When designing endpoints
  [SKILL-07] Security Review   ← For security checks
```

### 🖥️ Frontend Developer (Next.js)

```
Project Instructions:
  [SKILL-00] Project Context   ← Always first
  [SKILL-03] Next.js Frontend  ← Primary skill
  [SKILL-06] API Design        ← For API consumption
```

### 📱 Mobile Developer (Flutter)

```
Project Instructions:
  [SKILL-00] Project Context   ← Always first
  [SKILL-04] Flutter Mobile    ← Primary skill
  [SKILL-06] API Design        ← For API reference
```

### 🔧 DevOps / SRE

```
Project Instructions:
  [SKILL-00] Project Context   ← Always first
  [SKILL-05] DevOps & Infra    ← Primary skill
  [SKILL-07] Security Review   ← For security checks
```

### 👔 Tech Lead / Full-stack

```
Project Instructions:
  [SKILL-00] + [SKILL-01] + [SKILL-03] + [SKILL-04]
  + [SKILL-06] + [SKILL-07] + [SKILL-08] + [SKILL-10]
```

---

## Cara Menggunakan Skills Secara Efektif

### ✅ DO: Sertakan Konteks Spesifik

```
"Saya sedang kerjakan endpoint POST /v1/transactions untuk pos-service.
 Berikut existing domain entity Transaction dan repository interface-nya:
 [paste kode]
 Tolong generate usecase CreateTransactionUsecase dengan handle offline sync."
```

### ✅ DO: Paste Kode yang Relevan

```
"Tolong review kode ini sesuai dev rules XynPOS:
 [paste kode]"
```

### ✅ DO: Minta Task Spesifik

```
"Generate unit test table-driven untuk TransactionUsecase.Create()
 dengan test cases: success, insufficient stock, invalid payment amount."
```

### ❌ DON'T: Pertanyaan Terlalu Umum

```
"Buat fitur POS"  ← Terlalu luas, tidak actionable
"Cek kode ini"    ← Tidak jelas apa yang mau di-cek
```

### ✅ DO: Iterasi dalam Session yang Sama

```
Jangan mulai session baru untuk topik yang sama.
Lanjutkan conversation yang sama untuk maintain konteks.
```

---

## Tips Penggunaan

### Untuk Coding Session

```
1. Sebutkan service atau feature yang dikerjakan
2. Paste relevant existing code (entity, interface, dll)
3. Minta generate specific layer (usecase? handler? test?)
4. Iterasi dari output Claude — minta refinement jika perlu
```

### Untuk Code Review

```
1. Paste kode yang mau di-review
2. Tanya: "Tolong review sesuai SKILL-08 XynPOS code review checklist"
3. Claude akan berikan feedback kategorized (BLOCKER vs SUGGESTION)
```

### Untuk Architecture Decision

```
1. Jelaskan problem yang dihadapi
2. Tanya: "Apa pilihan yang ada? Tolong buat ADR-nya sesuai format XynPOS"
3. Claude akan generate ADR dengan context, options, consequences
```

### Untuk Debug

```
1. Paste error message lengkap
2. Paste relevant code (handler, usecase, atau query)
3. Sebutkan environment (development? staging?)
4. Claude akan diagnose dan suggest fix sesuai XynPOS patterns
```

---

## Cara Update Skills

Saat ada perubahan arsitektur, rules baru, atau lessons learned:

1. Edit skill file yang relevan di `skills/` directory
2. Update versi di frontmatter: `version: 1.0.1`
3. Commit dengan message: `docs(skills): update SKILL-01 Go backend — tambah rule X`
4. Update semua Project Instructions di claude.ai

**Trigger untuk update skills:**
- Ada dev rule baru yang disepakati tim
- Ada library baru yang ditambahkan ke stack
- Ada architectural pattern baru
- Ada common mistake yang ditemukan via code review
- Post-sprint retrospective menghasilkan learnings

---

## Membuat Skill Baru

Untuk kebutuhan yang belum ada skill-nya:

1. Copy template dari skill yang mirip
2. Isi frontmatter dengan benar (skill_id, name, category, applies_to, depends_on)
3. Fokus pada: stack, patterns, rules, dan checklist yang actionable
4. Tambahkan ke daftar di dokumen ini
5. PR ke repo ini untuk review tim

**Template minimal:**

```markdown
---
skill_id: SKILL-{N}
name: XynPOS {Nama Skill}
category: {backend|frontend|mobile|infrastructure|shared}
description: {Deskripsi singkat}
version: 1.0.0
applies_to: [{tag1}, {tag2}]
depends_on: [SKILL-00]
---

# SKILL-{N}: {Nama Skill}

## Stack/Context
...

## Key Patterns
...

## Rules
...

## Checklist
...
```

---

## Skills Roadmap (Future)

| Skill (Future) | Trigger | Estimasi |
|----------------|---------|---------|
| SKILL-11: XYN CRM Integration | Wave 5 start | Q4 Year 1 |
| SKILL-12: e-Faktur Integration | Wave 4 start | Q3 Year 1 |
| SKILL-13: Marketplace Integration | Wave 5 | Q1 Year 2 |
| SKILL-14: Performance Optimization | Post-launch | When needed |
| SKILL-15: AI Features Development | Wave 6 | Year 2 |
| SKILL-16: SEA Localization | Year 2 expansion | Year 2 |

---

*Skills Guide ini adalah living document — update saat ada skills baru atau cara penggunaan yang lebih baik.*
*Extended Synaptic — XynPOS | skills/guides/SKILLS-GUIDE.md*
