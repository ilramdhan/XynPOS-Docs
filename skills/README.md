# XynPOS Claude Skills

> 10 production-ready skills for AI-assisted development of XynPOS

---

## What Are These Skills?

Each skill is a **Claude Code skill** — a folder containing a `SKILL.md` (instructions), Python scripts for automation, reference documentation, and eval test cases. When installed in Claude Code, they are invoked with `/xynpos-{name}` commands.

Skills provide:
- **Context** — Claude knows the full XynPOS architecture without re-explanation
- **Automation** — Python scripts for scaffolding, linting, validation, and security scanning
- **Consistency** — Every developer gets the same standards and patterns
- **Evals** — Test cases to verify skill quality

---

## Available Skills

| Skill | Command | Purpose | Scripts Included |
|-------|---------|---------|-----------------|
| [xynpos-context](xynpos-context/) | `/xynpos-context` | Master project context — load first | — |
| [xynpos-go-backend](xynpos-go-backend/) | `/xynpos-go-backend` | Go microservice development | `check_rules.py` · `scaffold_service.py` |
| [xynpos-database](xynpos-database/) | `/xynpos-database` | PostgreSQL, GORM, migrations | `gen_migration.py` |
| [xynpos-frontend](xynpos-frontend/) | `/xynpos-frontend` | Next.js web development | `check_fe_rules.py` |
| [xynpos-mobile](xynpos-mobile/) | `/xynpos-mobile` | Flutter mobile development | `check_flutter_rules.py` |
| [xynpos-devops](xynpos-devops/) | `/xynpos-devops` | Docker, CI/CD, K8s, Terraform | `validate_dockerfile.py` |
| [xynpos-api-design](xynpos-api-design/) | `/xynpos-api-design` | REST API design & documentation | `check_api_consistency.py` |
| [xynpos-security](xynpos-security/) | `/xynpos-security` | Security review & UU PDP | `security_scan.py` |
| [xynpos-code-review](xynpos-code-review/) | `/xynpos-code-review` | PR review all stacks | `review_go.py` · `review_flutter.py` · `review_typescript.py` |
| [xynpos-docs-writer](xynpos-docs-writer/) | `/xynpos-docs-writer` | Blueprint & ADR authoring | `validate_docs.py` · `gen_blueprint.py` |

---

## Installation

### Option A: Install `.skill` File (Recommended)

Download the `.skill` file from `skills/dist/` and install via Claude Code:

```bash
# Install a specific skill
claude skill install skills/dist/xynpos-go-backend.skill

# Or install all at once
for f in skills/dist/*.skill; do claude skill install "$f"; done
```

### Option B: Point Claude Code at the folder directly

In your Claude Code config or settings, add the skills directory:

```json
{
  "skills_path": "/path/to/XynPOS-Docs/skills"
}
```

### Option C: Symlink to Claude Code skills directory

```bash
# Find your Claude Code skills directory (usually ~/.claude/skills/)
ln -s /path/to/XynPOS-Docs/skills/xynpos-go-backend ~/.claude/skills/xynpos-go-backend
```

---

## Using Skills in Claude Code

Once installed, invoke with `/skill-name`:

```
/xynpos-context                    → Load project context
/xynpos-go-backend                 → Start Go coding session
/xynpos-code-review review main.go → Review a specific file
/xynpos-security scan ./backend/   → Run security scan
/xynpos-database                   → Get DB/migration help
/xynpos-mobile                     → Flutter development
/xynpos-devops                     → Infra/DevOps work
/xynpos-api-design                 → Design or review endpoints
/xynpos-docs-writer                → Write/update documentation
```

---

## Using the Python Scripts Directly

All scripts can be run standalone from the repo root:

```bash
# Check Go code for rule violations
python skills/xynpos-go-backend/scripts/check_rules.py backend/services/pos-service/

# Scaffold a new Go microservice
python skills/xynpos-go-backend/scripts/scaffold_service.py kds-service order

# Generate a new migration file
python skills/xynpos-database/scripts/gen_migration.py add_batch_tracking

# Validate a Dockerfile
python skills/xynpos-devops/scripts/validate_dockerfile.py backend/services/pos-service/Dockerfile

# Security scan
python skills/xynpos-security/scripts/security_scan.py backend/

# Full Go code review (runs all checks)
python skills/xynpos-code-review/scripts/review_go.py backend/services/pos-service/

# Flutter rule check
python skills/xynpos-mobile/scripts/check_flutter_rules.py mobile/xynpos_mobile/lib/

# Frontend rule check
python skills/xynpos-frontend/scripts/check_fe_rules.py frontend/apps/web-pos/src/

# Validate blueprint docs format
python skills/xynpos-docs-writer/scripts/validate_docs.py docs/blueprints/

# Scaffold a new blueprint
python skills/xynpos-docs-writer/scripts/gen_blueprint.py 25 "Hardware Integration" technical
```

---

## Skill Structure

Each skill folder follows this layout:

```
xynpos-{name}/
├── SKILL.md          ← Main instructions (loaded by Claude)
├── LICENSE.txt       ← MIT license (Extended Synaptic)
├── scripts/          ← Python automation scripts
│   └── *.py
├── references/       ← Deep reference docs (loaded on demand)
│   └── *.md
├── agents/           ← Sub-agent instructions (if applicable)
│   └── *.md
└── evals/            ← Test cases for skill quality
    └── evals.json
```

---

## Recommended Skill Combinations per Role

| Role | Primary Skills | Supporting Skills |
|------|---------------|-------------------|
| **Backend Dev (Go)** | `xynpos-context` + `xynpos-go-backend` | `xynpos-database` + `xynpos-api-design` + `xynpos-security` |
| **Frontend Dev** | `xynpos-context` + `xynpos-frontend` | `xynpos-api-design` |
| **Mobile Dev (Flutter)** | `xynpos-context` + `xynpos-mobile` | `xynpos-api-design` |
| **DevOps / SRE** | `xynpos-context` + `xynpos-devops` | `xynpos-security` |
| **Tech Lead** | `xynpos-context` + `xynpos-code-review` | All others as needed |
| **Product/Docs** | `xynpos-context` + `xynpos-docs-writer` | — |

---

## Contributing: Update a Skill

1. Edit the skill folder files
2. Update `version` in SKILL.md frontmatter (e.g., `1.0.0` → `1.0.1`)
3. Re-package: `python package_skill.py skills/xynpos-{name}/ skills/dist/`
4. Commit: `docs(skills): update xynpos-{name} — description of change`
5. Re-install in Claude Code

## Contributing: Create a New Skill

```bash
# Scaffold a new skill folder
mkdir -p skills/xynpos-newskill/{scripts,references,agents,evals}

# Create required files
touch skills/xynpos-newskill/SKILL.md
touch skills/xynpos-newskill/LICENSE.txt
echo '{"skill_name":"xynpos-newskill","evals":[]}' > skills/xynpos-newskill/evals/evals.json

# Package
python package_skill.py skills/xynpos-newskill/ skills/dist/
```

---

## Skills Roadmap

| Future Skill | Trigger | Est. Quarter |
|-------------|---------|-------------|
| `xynpos-crm-integration` | Wave 5 start | Q4 Y1 |
| `xynpos-efaktur` | Wave 4 start | Q3 Y1 |
| `xynpos-marketplace` | Wave 5 | Q1 Y2 |
| `xynpos-ai-features` | Wave 6 | Q1 Y2 |
| `xynpos-localization` | SEA expansion | Q2 Y2 |

---

*XynPOS Skills — Extended Synaptic | MIT License*  
*Docs: https://github.com/ilramdhan/XynPOS-Docs*
