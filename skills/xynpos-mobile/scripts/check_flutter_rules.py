#!/usr/bin/env python3
"""
XynPOS Flutter Rule Checker
Scans Dart files for common mobile violations.

Usage:
    python scripts/check_flutter_rules.py <path>
    python scripts/check_flutter_rules.py mobile/xynpos_mobile/lib/
"""
import sys, re
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Violation:
    file: str; line: int; severity: str; rule: str; message: str; suggestion: str

def check_file(filepath: str) -> List[Violation]:
    violations = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    content = ''.join(lines)
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('//'): continue
        
        # Rule: StatelessWidget watching provider (should be ConsumerWidget)
        if 'ref.watch(' in line or 'ref.read(' in line:
            if 'StatelessWidget' in content and 'ConsumerWidget' not in content:
                if i == 1:
                    violations.append(Violation(filepath, 1, "BLOCKER", "WRONG_WIDGET_TYPE",
                        "Widget uses ref.watch/read but extends StatelessWidget",
                        "Change StatelessWidget to ConsumerWidget and add WidgetRef ref parameter"))
        
        # Rule: Column with .map for lists (should be ListView.builder)
        if re.search(r'Column\s*\(', line):
            context = ''.join(lines[i:min(i+10, len(lines))])
            if '.map(' in context and 'ListView' not in context:
                violations.append(Violation(filepath, i, "BLOCKER", "COLUMN_FOR_LIST",
                    "Column with .map() for list items — performance issue",
                    "Use ListView.builder(itemCount: n, itemBuilder: (_, i) => Widget(items[i]))"))
        
        # Rule: Image.network instead of CachedNetworkImage
        if re.search(r'\bImage\.network\s*\(', line):
            violations.append(Violation(filepath, i, "BLOCKER", "NO_IMAGE_CACHE",
                "Image.network() — no caching, re-downloads on every build",
                "Use CachedNetworkImage with placeholder and errorWidget"))
        
        # Rule: Missing const constructor in StatelessWidget
        if 'StatelessWidget' in line or 'ConsumerWidget' in line:
            context = ''.join(lines[i:min(i+5, len(lines))])
            if 'const' not in context and 'super.key' in context and 'StatefulWidget' not in line:
                violations.append(Violation(filepath, i, "WARNING", "NO_CONST_CONSTRUCTOR",
                    "Widget without const constructor",
                    "Add const to constructor: const MyWidget({super.key});"))
        
        # Rule: direct http.get/dio.get in domain layer
        if 'domain' in filepath.replace('\\', '/') and re.search(r'\b(dio|http|Dio)\b', line):
            violations.append(Violation(filepath, i, "BLOCKER", "INFRA_IN_DOMAIN",
                f"Infrastructure import in domain layer: {stripped[:60]}",
                "Domain layer must not import Dio or HTTP. Use repository interface."))
        
        # Rule: fromJson/toJson in entities (should be in models only)
        if 'entities' in filepath.replace('\\', '/') and re.search(r'fromJson|toJson|@JsonSerializable', line):
            violations.append(Violation(filepath, i, "BLOCKER", "JSON_IN_ENTITY",
                "JSON serialization in domain entity",
                "Move fromJson/toJson to data/models/. Domain entities must be pure."))
    
    return violations

def check_path(path: str) -> List[Violation]:
    all_v = []
    p = Path(path)
    if p.is_file() and p.suffix == '.dart':
        all_v.extend(check_file(str(p)))
    elif p.is_dir():
        for f in p.rglob('*.dart'):
            if '.dart_tool' not in str(f) and 'build/' not in str(f):
                all_v.extend(check_file(str(f)))
    return all_v

def print_report(violations: List[Violation]) -> int:
    if not violations:
        print("✅ No Flutter violations found!"); return 0
    blockers = [v for v in violations if v.severity == "BLOCKER"]
    warnings = [v for v in violations if v.severity == "WARNING"]
    print(f"\nXynPOS Flutter Rule Check")
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
        print(f"Usage: python {sys.argv[0]} <path>"); sys.exit(1)
    sys.exit(print_report(check_path(sys.argv[1])))
