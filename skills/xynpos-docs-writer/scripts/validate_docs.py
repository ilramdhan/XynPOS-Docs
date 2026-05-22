#!/usr/bin/env python3
"""
XynPOS Blueprint Format Validator
Checks all blueprint files for format compliance.

Usage:
    python scripts/validate_docs.py [docs-path]
    python scripts/validate_docs.py docs/blueprints/
"""
import sys, re
from pathlib import Path

def validate_blueprint(filepath: str) -> list:
    issues = []
    content = Path(filepath).read_text(encoding='utf-8', errors='ignore')
    lines = content.splitlines()
    
    # Must start with # XynPOS — Blueprint
    if not lines or not lines[0].startswith('# XynPOS'):
        issues.append(f"Title must start with '# XynPOS — Blueprint N:'")
    
    # Must have frontmatter-style > line
    if len(lines) < 2 or not lines[1].startswith('> Extended Synaptic'):
        issues.append("Second line must be '> Extended Synaptic | Version ...'")
    
    # Must have cross-reference footer
    if '*Blueprint ini inline dengan:' not in content and '*Last updated:' not in content:
        issues.append("Missing footer with cross-references and update date")
    
    # Must have at least 2 sections (##)
    sections = [l for l in lines if l.startswith('## ')]
    if len(sections) < 2:
        issues.append(f"Too few sections ({len(sections)}) — add more content")
    
    return issues

def validate_path(path: str) -> dict:
    results = {}
    p = Path(path)
    
    pattern = '**/*.md'
    files = list(p.glob(pattern)) if p.is_dir() else [p]
    
    for f in files:
        if f.name in ['README.md', 'CHANGELOG.md']:
            continue
        issues = validate_blueprint(str(f))
        if issues:
            results[str(f)] = issues
    
    return results

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "docs/blueprints"
    results = validate_path(path)
    
    if not results:
        total = len(list(Path(path).glob('**/*.md'))) if Path(path).is_dir() else 1
        print(f"✅ All {total} blueprint files pass format validation!")
        sys.exit(0)
    
    print(f"\n⚠️ Blueprint Format Issues:")
    for f, issues in results.items():
        print(f"\n📄 {f}:")
        for issue in issues:
            print(f"   ⚠️ {issue}")
    sys.exit(1)
