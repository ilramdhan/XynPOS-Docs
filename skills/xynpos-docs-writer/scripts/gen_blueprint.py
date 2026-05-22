#!/usr/bin/env python3
"""
XynPOS Blueprint Generator
Scaffolds a new blueprint document with proper format.

Usage:
    python scripts/gen_blueprint.py <number> <title> <category>
    python scripts/gen_blueprint.py 25 "Hardware Integration Guide" technical

Categories: business, product, technical, infrastructure, developer, compliance
"""
import sys
from pathlib import Path
from datetime import datetime

CATEGORY_DIRS = {
    "business": "docs/blueprints/business",
    "product": "docs/blueprints/product",
    "technical": "docs/blueprints/technical",
    "infrastructure": "docs/blueprints/infrastructure",
    "developer": "docs/blueprints/developer",
    "compliance": "docs/blueprints/compliance",
}

def gen_blueprint(number: int, title: str, category: str, repo_root: str = "."):
    if category not in CATEGORY_DIRS:
        print(f"❌ Unknown category: {category}")
        print(f"Valid: {', '.join(CATEGORY_DIRS.keys())}")
        return
    
    slug = title.lower().replace(' ', '-').replace('/', '-')
    filename = f"{number:02d}-{slug}.md"
    
    output_dir = Path(repo_root) / CATEGORY_DIRS[category]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    
    content = f"""# XynPOS — Blueprint {number}: {title}
> Extended Synaptic | Version 1.0 | {category.title()} — {title}

---

## 1. Overview

<!-- TODO: Write overview -->

---

## 2. {title} Details

<!-- TODO: Add detailed content -->

---

## 3. Implementation Guide

<!-- TODO: Add implementation steps -->

---

## 4. Reference

<!-- TODO: Add references, links, related docs -->

---
*Blueprint ini inline dengan: [list related BPs here]*
*Last updated: {datetime.now().year} | Extended Synaptic — XynPOS*
"""
    
    output_path.write_text(content)
    print(f"✅ Blueprint created: {output_path}")
    print(f"\nNext steps:")
    print(f"  1. Edit {output_path}")
    print(f"  2. Add cross-references to related blueprints")
    print(f"  3. Update docs/README.md blueprint table")
    print(f"  4. Update CHANGELOG.md")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage: python {sys.argv[0]} <number> <title> <category>")
        sys.exit(1)
    gen_blueprint(int(sys.argv[1]), sys.argv[2], sys.argv[3],
                  sys.argv[4] if len(sys.argv) > 4 else ".")
