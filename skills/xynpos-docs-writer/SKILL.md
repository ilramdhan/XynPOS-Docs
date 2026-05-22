---
name: xynpos-docs-writer
description: XynPOS documentation writer — use when creating or updating blueprints, writing Architecture Decision Records (ADRs), documenting APIs with Swagger, maintaining the operational runbook, updating CLAUDE.md, writing changelog entries, or creating developer guides for the XynPOS project. Triggers when someone needs to document a new feature or architectural decision, update existing blueprints, write an ADR for a tech decision, add Swagger annotations, update the onboarding guide, or maintain any documentation in the XynPOS-Docs repository.
license: See LICENSE.txt
---

# XynPOS Documentation Writer

Maintain the XynPOS documentation repository at github.com/ilramdhan/XynPOS-Docs.

## Reference Files
- All 24 blueprint inventory → `references/blueprint-inventory.md`
- ADR template and existing ADRs → `references/adr-guide.md`
- Changelog format → `references/changelog-guide.md`

## Documentation Structure

```
XynPOS-Docs/
├── README.md                    Repo homepage
├── CHANGELOG.md                 Version history
├── docs/
│   ├── blueprints/
│   │   ├── business/            BP-01, 02, 15
│   │   ├── product/             BP-03, 04
│   │   ├── technical/           BP-05, 06, 07, 08, 11, 12
│   │   ├── infrastructure/      BP-09
│   │   ├── developer/           BP-13, 14, 19, 20, 21, 22, 23, 24
│   │   └── compliance/          BP-10, 16
│   ├── adr/                     17-adr-architecture-decision-records.md
│   └── runbooks/                18-operational-runbook.md
└── skills/                      10 Claude skills
    ├── xynpos-context/
    ├── xynpos-go-backend/
    └── ... (8 more skills)
```

## Blueprint Format (use this template)

```markdown
# XynPOS — Blueprint {N}: {Title}
> Extended Synaptic | Version X.X | {Brief description}

---

## 1. {First Section}

Content...

## N. {Last Section}

Content...

---
*Blueprint ini inline dengan: BP-XX ({Name}), BP-YY ({Name})*
*Last updated: YYYY | Extended Synaptic — XynPOS*
```

## ADR Format

```markdown
## ADR-{N}: {Decision Title}

- **Status:** Accepted
- **Tanggal:** YYYY-MM-DD
- **Decider:** {Role}

**Konteks:** {What forced this decision}
**Keputusan:** {What was decided, specifically}
**Alasan:** {Why this was chosen — technical + team factors}
**Konsekuensi:** {Trade-offs accepted}
**Alternatif yang ditolak:**
- **{Option A}:** {Why rejected}
**Review Trigger:** {Condition for re-evaluation}
```

## Changelog Format

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature description (BP-XX reference)

### Changed  
- What changed and why

### Fixed
- Bug or correction description
```

## Writing Rules

- Language: Bahasa Indonesia for prose, English for technical terms
- Use tables for comparisons and reference data
- Code blocks with appropriate syntax highlighting
- Every blueprint ends with cross-reference footer
- ADR titles start with verb: "Pilih X", "Gunakan Y", "Migrasi ke Z"

## Scripts

`scripts/validate_docs.py` — checks all blueprints for format compliance.
`scripts/gen_blueprint.py <number> <title> <category>` — scaffolds new blueprint.
