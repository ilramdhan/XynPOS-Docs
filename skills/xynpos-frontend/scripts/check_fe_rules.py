#!/usr/bin/env python3
"""
XynPOS Frontend Rule Checker
Scans TypeScript/TSX files for common frontend violations.

Usage:
    python scripts/check_fe_rules.py <path>
    python scripts/check_fe_rules.py frontend/apps/web-pos/src/
"""
import sys, os, re
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Violation:
    file: str
    line: int
    severity: str
    rule: str
    message: str
    suggestion: str

def check_file(filepath: str) -> List[Violation]:
    violations = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    content = ''.join(lines)
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('*'): continue
        
        # Rule: No any type
        if re.search(r':\s*any\b', line) and 'eslint-disable' not in line:
            violations.append(Violation(filepath, i, "WARNING", "NO_ANY_TYPE",
                f"TypeScript 'any' type: {stripped[:70]}",
                "Use proper typing or 'unknown' with type guard"))
        
        # Rule: No direct fetch in components/hooks
        if re.search(r'\bfetch\s*\(', line) and '/api/' in content[:1000]:
            if 'lib/api' not in filepath and 'features' not in filepath.replace('\\','/').split('/')[-2:][0] if len(filepath.replace('\\','/').split('/')) > 2 else True:
                violations.append(Violation(filepath, i, "BLOCKER", "DIRECT_FETCH",
                    f"Direct fetch() call: {stripped[:70]}",
                    "Use centralized api client from lib/api.ts"))
        
        # Rule: useState for server data (useState + useEffect combo)
        if 'useState' in content and 'useEffect' in content and 'fetch(' in content:
            if i == 1:  # Report once per file
                violations.append(Violation(filepath, 1, "BLOCKER", "STATE_FOR_SERVER_DATA",
                    "useState+useEffect pattern detected for server data",
                    "Use TanStack Query: useQuery({ queryKey, queryFn })"))
        
        # Rule: inline styles (static)
        if re.search(r'style=\{\{[^}]{20,}\}\}', line):
            violations.append(Violation(filepath, i, "WARNING", "INLINE_STYLE",
                f"Inline style found: {stripped[:70]}",
                "Use Tailwind classes instead of inline styles"))
        
        # Rule: Missing loading state
        if 'useQuery' in content and 'isLoading' not in content and i == 1:
            violations.append(Violation(filepath, 1, "WARNING", "NO_LOADING_STATE",
                "useQuery used but no isLoading handling visible",
                "Add loading state: if (isLoading) return <LoadingSkeleton />"))
    
    return violations

def check_path(path: str) -> List[Violation]:
    all_v = []
    p = Path(path)
    extensions = {'.tsx', '.ts'}
    if p.is_file() and p.suffix in extensions:
        all_v.extend(check_file(str(p)))
    elif p.is_dir():
        for f in p.rglob('*'):
            if f.suffix in extensions and 'node_modules' not in str(f) and '.next' not in str(f):
                all_v.extend(check_file(str(f)))
    return all_v

def print_report(violations: List[Violation]) -> int:
    if not violations:
        print("✅ No frontend violations found!")
        return 0
    blockers = [v for v in violations if v.severity == "BLOCKER"]
    warnings = [v for v in violations if v.severity == "WARNING"]
    print(f"\nXynPOS Frontend Rule Check")
    print(f"🔴 BLOCKERS: {len(blockers)} | ⚠️ WARNINGS: {len(warnings)}")
    print("="*50)
    for v in violations:
        icon = "🔴" if v.severity == "BLOCKER" else "⚠️"
        print(f"\n{icon} [{v.rule}] {v.file}:{v.line}")
        print(f"   Problem: {v.message}")
        print(f"   Fix:     {v.suggestion}")
    return 1 if blockers else 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>")
        sys.exit(1)
    violations = check_path(sys.argv[1])
    sys.exit(print_report(violations))
