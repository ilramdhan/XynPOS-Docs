#!/usr/bin/env python3
"""
XynPOS Go Backend Rule Checker
Scans Go files for common violations of XynPOS dev rules.

Usage:
    python scripts/check_rules.py <path>
    python scripts/check_rules.py backend/services/pos-service/
    python scripts/check_rules.py backend/services/pos-service/internal/delivery/http/handler.go

Output: List of violations with file, line, severity, and fix suggestion.
"""

import sys
import re
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Violation:
    file: str
    line: int
    severity: str  # BLOCKER | WARNING
    rule: str
    message: str
    suggestion: str


def check_file(filepath: str) -> List[Violation]:
    violations = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    content = ''.join(lines)
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # RULE 1: No fmt.Println (use zap)
        if 'fmt.Println(' in line or 'fmt.Printf(' in line or 'fmt.Print(' in line:
            if not line.strip().startswith('//'):
                violations.append(Violation(
                    file=filepath, line=i,
                    severity="BLOCKER",
                    rule="NO_FMT_PRINT",
                    message=f"fmt print found: {stripped[:80]}",
                    suggestion="Use logger.Info/Error/Debug with zap fields instead"
                ))
        
        # RULE 2: log.Printf/Println (standard library logger)
        if re.search(r'\blog\.(Printf|Println|Print|Fatal|Panic)\(', line):
            if not line.strip().startswith('//'):
                violations.append(Violation(
                    file=filepath, line=i,
                    severity="BLOCKER",
                    rule="NO_STD_LOGGER",
                    message=f"Standard logger used: {stripped[:80]}",
                    suggestion="Use zap structured logger from shared/pkg/logger"
                ))
        
        # RULE 3: Bare error return (no wrapping)
        if re.search(r'return\s+nil,\s+err\s*$', line):
            if not line.strip().startswith('//'):
                violations.append(Violation(
                    file=filepath, line=i,
                    severity="WARNING",
                    rule="UNWRAPPED_ERROR",
                    message="Error returned without context wrapping",
                    suggestion='Use: return nil, fmt.Errorf("operation context: %w", err)'
                ))
        
        # RULE 4: Panic in non-main files
        if 'panic(' in line and not line.strip().startswith('//'):
            if 'cmd/main.go' not in filepath and '_test.go' not in filepath:
                violations.append(Violation(
                    file=filepath, line=i,
                    severity="BLOCKER",
                    rule="NO_PANIC",
                    message=f"panic() in non-main file: {stripped[:80]}",
                    suggestion="Return an error instead of panicking"
                ))
        
        # RULE 5: c.Query("tenant_id") or similar - tenant from request
        if re.search(r'c\.(Query|Params|FormValue)\s*\(\s*["\']tenant', line, re.IGNORECASE):
            if not line.strip().startswith('//'):
                violations.append(Violation(
                    file=filepath, line=i,
                    severity="BLOCKER",
                    rule="TENANT_FROM_REQUEST",
                    message="Tenant ID taken from request — security violation!",
                    suggestion='Use: tenantID := c.Locals("tenantID").(string)'
                ))
        
        # RULE 6: db.Find(&x) without Select — potential SELECT *
        if re.search(r'db\.(Find|First|Last)\s*\(', line):
            # Check if Select() is called in the chain (look at surrounding context)
            context_lines = ''.join(lines[max(0, i-5):i+2])
            if '.Select(' not in context_lines and not line.strip().startswith('//'):
                violations.append(Violation(
                    file=filepath, line=i,
                    severity="WARNING",
                    rule="SELECT_STAR",
                    message="Query may be SELECT * — specify needed columns",
                    suggestion='Add .Select("id", "name", ...) before .Find()/.First()'
                ))
        
        # RULE 7: Log sensitive fields
        sensitive_patterns = ['password', 'passwd', 'pin', 'secret', 'token', 'npwp', 'card_number', 'cvv']
        for sp in sensitive_patterns:
            if re.search(rf'zap\.\w+\(\s*["\']({sp})["\']', line, re.IGNORECASE):
                if not line.strip().startswith('//'):
                    violations.append(Violation(
                        file=filepath, line=i,
                        severity="BLOCKER",
                        rule="LOG_SENSITIVE",
                        message=f"Logging sensitive field '{sp}'",
                        suggestion=f"Remove or mask '{sp}' from logs"
                    ))
        
        # RULE 8: Hardcoded secrets
        if re.search(r'(secret|password|apikey|api_key)\s*:?=\s*["\'][^"\']{8,}["\']', line, re.IGNORECASE):
            if not line.strip().startswith('//') and 'test' not in filepath.lower() and 'example' not in filepath.lower():
                violations.append(Violation(
                    file=filepath, line=i,
                    severity="BLOCKER",
                    rule="HARDCODED_SECRET",
                    message=f"Possible hardcoded secret: {stripped[:60]}",
                    suggestion="Load from environment variables via config.Load()"
                ))
    
    return violations


def check_path(path: str) -> List[Violation]:
    all_violations = []
    p = Path(path)
    
    if p.is_file() and p.suffix == '.go':
        all_violations.extend(check_file(str(p)))
    elif p.is_dir():
        for go_file in p.rglob('*.go'):
            # Skip vendor and generated files
            if any(skip in str(go_file) for skip in ['vendor/', 'mock/', '.pb.go', '_mock.go']):
                continue
            all_violations.extend(check_file(str(go_file)))
    
    return all_violations


def print_report(violations: List[Violation]) -> int:
    if not violations:
        print("✅ No violations found!")
        return 0
    
    blockers = [v for v in violations if v.severity == "BLOCKER"]
    warnings = [v for v in violations if v.severity == "WARNING"]
    
    print(f"\n{'='*60}")
    print(f"XynPOS Go Rule Check Results")
    print(f"{'='*60}")
    print(f"🔴 BLOCKERS: {len(blockers)}")
    print(f"⚠️  WARNINGS: {len(warnings)}")
    print(f"Total: {len(violations)}")
    print(f"{'='*60}\n")
    
    # Print blockers first
    if blockers:
        print("🔴 BLOCKERS (must fix before PR merge):\n")
        for v in blockers:
            print(f"  [{v.rule}] {v.file}:{v.line}")
            print(f"  Problem: {v.message}")
            print(f"  Fix:     {v.suggestion}")
            print()
    
    if warnings:
        print("⚠️  WARNINGS (should fix):\n")
        for v in warnings:
            print(f"  [{v.rule}] {v.file}:{v.line}")
            print(f"  Problem: {v.message}")
            print(f"  Fix:     {v.suggestion}")
            print()
    
    return 1 if blockers else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>")
        print("  <path> can be a .go file or directory")
        sys.exit(1)
    
    target = sys.argv[1]
    if not os.path.exists(target):
        print(f"❌ Path not found: {target}")
        sys.exit(1)
    
    violations = check_path(target)
    exit_code = print_report(violations)
    sys.exit(exit_code)
