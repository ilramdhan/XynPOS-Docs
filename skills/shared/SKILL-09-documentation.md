---
skill_id: SKILL-09
name: XynPOS Documentation Writer
category: shared
description: Skill untuk update blueprint, tulis ADR, API docs, dan semua dokumentasi XynPOS
version: 1.0.0
applies_to: [documentation, blueprint, adr, api-docs]
depends_on: [SKILL-00]
---

# SKILL-09: Documentation Writer

## Blueprint Format

```markdown
# XynPOS — Blueprint {N}: {Judul}
> Extended Synaptic | Version X.X | {Deskripsi Singkat}

---

## 1. Section Pertama
...

## N. Section Terakhir
...

---
*Blueprint ini inline dengan: BP-XX (Nama), BP-YY (Nama)*
*Last updated: YYYY | Extended Synaptic — XynPOS*
```

**Ketentuan:**
- Bahasa Indonesia untuk narasi, English untuk technical terms
- Gunakan tabel untuk perbandingan dan reference
- Code blocks dengan syntax highlighting yang tepat
- Setiap blueprint harus ada cross-reference di footer

## Blueprint Inventory (24 dokumen)

```
docs/blueprints/business/
  01-target-market-competitive-analysis.md  ← T1-T4 segments, competitors, GTM summary
  02-financial-subscription-mechanism.md    ← Business model, pricing, BEP, ARR projection
  15-gtm-launch-blueprint.md               ← Launch phases, acquisition, retention

docs/blueprints/product/
  03-mvp-features-blueprint.md             ← 47 features, sprint plan 12 weeks
  04-post-mvp-advanced-features.md         ← 6 waves: Wave 1-6 features

docs/blueprints/technical/
  05-tech-stack-blueprint.md               ← Full stack decisions with rationale
  06-system-architecture-blueprint.md      ← System design, data flows, security layers
  07-project-structure-blueprint.md        ← Monorepo structure, naming conventions
  08-database-schema-blueprint.md          ← Full SQL schema + ERD + migration strategy
  11-api-design-blueprint.md               ← All endpoints, request/response format
  12-mobile-app-blueprint.md               ← Flutter architecture, offline mode

docs/blueprints/infrastructure/
  09-infrastructure-devops-blueprint.md    ← Cloud resources, Docker, CI/CD, K8s

docs/blueprints/developer/
  13-CLAUDE-ai-instructions.md             ← CLAUDE.md for Claude Code (daily reference)
  14-testing-strategy-blueprint.md         ← Test pyramid, coverage, k6 load test
  19-developer-onboarding-guide.md         ← Setup guide for new developers
  20-dev-rules-backend.md                  ← Go dev rules (law, not guidelines)
  21-dev-rules-frontend.md                 ← Next.js dev rules
  22-dev-rules-mobile.md                   ← Flutter dev rules
  23-dev-rules-infrastructure.md           ← Infrastructure dev rules
  24-claude-skills-plan.md                 ← Skills roadmap and usage guide

docs/blueprints/compliance/
  10-security-blueprint.md                 ← STRIDE, RBAC, UU PDP compliance
  16-legal-compliance-blueprint.md         ← PT setup, ToS, Privacy Policy, HKI

docs/adr/
  17-adr-architecture-decision-records.md  ← 8 ADRs with template

docs/runbooks/
  18-operational-runbook.md                ← Step-by-step incident procedures
```

## ADR Format

```markdown
## ADR-{N}: {Judul Keputusan}

- **Status:** Proposed | Accepted | Deprecated | Superseded by ADR-{N}
- **Tanggal:** YYYY-MM-DD
- **Decider:** {Nama/Role}

**Konteks:**
{Situasi yang memaksa keputusan ini}

**Keputusan:**
{Keputusan spesifik yang diambil}

**Alasan:**
{Mengapa ini yang dipilih — faktor teknis, bisnis, tim}

**Konsekuensi:**
{Trade-off yang diterima}

**Alternatif yang ditolak:**
- **{Opsi A}:** {Mengapa ditolak}

**Review Trigger:** (opsional)
{Kondisi yang akan memicu review ulang keputusan ini}
```

## Swagger/OpenAPI Doc (Go)

```go
// Setiap handler WAJIB punya Swagger annotation

// @Summary      Buat transaksi baru
// @Description  Membuat transaksi penjualan. Mendukung multi-payment dan offline sync.
// @Tags         transactions
// @Accept       json
// @Produce      json
// @Param        X-Idempotency-Key header string  true "Idempotency key (UUID)"
// @Param        request body CreateTransactionRequest true "Transaction data"
// @Success      201  {object}  response.SuccessResponse{data=TransactionResponse}
// @Failure      400  {object}  response.ErrorResponse
// @Failure      422  {object}  response.ValidationErrorResponse
// @Security     BearerAuth
// @Router       /v1/transactions [post]
func (h *Handler) Create(c *fiber.Ctx) error { ... }

// Generate: make be-swagger SVC=pos-service
```

## Changelog Format

```markdown
# Changelog

## [Unreleased]
### Added
- Feature X (BP-03 Sprint 5)

## [1.2.0] - 2025-03-01
### Added
- Purchase Order management (Wave 1)
### Changed  
- Product list endpoint now supports cursor pagination
### Fixed
- Stock tidak ter-update saat offline sync conflict

## [1.1.0] - 2025-02-01
...
```

## Documentation Update Triggers

```
Kapan WAJIB update dokumentasi:

Blueprint update → Saat ada perubahan arsitektur, tech stack, atau fitur scope
ADR baru         → Setiap keputusan arsitektur penting
Runbook update   → Saat ada prosedur baru atau perubahan infra
API docs update  → Setiap endpoint baru atau perubahan signature
CLAUDE.md update → Saat ada konvensi atau rules baru
Changelog update → Setiap sprint release
```
