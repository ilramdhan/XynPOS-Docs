#!/usr/bin/env python3
"""
XynPOS API Consistency Checker
Validates Go HTTP handlers for XynPOS API conventions.

Usage:
    python scripts/check_api_consistency.py <path>
    python scripts/check_api_consistency.py backend/services/pos-service/internal/delivery/http/
"""
import sys, re
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Issue:
    file: str; line: int; severity: str; rule: str; message: str; suggestion: str

def check_handler_file(filepath: str) -> List[Issue]:
    issues = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.splitlines()
    
    # Find all handler functions
    handler_pattern = re.compile(r'func \([^)]+\)\s+(\w+)\(c \*fiber\.Ctx\)\s+error')
    
    for i, line in enumerate(lines, 1):
        m = handler_pattern.search(line)
        if not m:
            continue
        
        handler_name = m.group(1)
        # Get context around this handler (next 50 lines)
        ctx = '\n'.join(lines[i:min(i+50, len(lines))])
        
        # Rule: Response must use response package
        has_standard_response = ('response.Success' in ctx or 'response.Error' in ctx or
                                 'response.ValidationError' in ctx or 'response.SuccessList' in ctx)
        has_raw_json = re.search(r'c\.JSON\(map\[', ctx) or re.search(r'c\.JSON\(fiber\.Map', ctx)
        
        if has_raw_json and not has_standard_response:
            issues.append(Issue(filepath, i, "BLOCKER", "NON_STANDARD_RESPONSE",
                f"Handler {handler_name}: raw JSON response instead of standard format",
                "Use response.Success(data) or response.Error(code, msg) from shared/pkg/response"))
        
        # Rule: Should have Swagger annotation
        preceding = '\n'.join(lines[max(0,i-10):i])
        if '@Router' not in preceding and '@Summary' not in preceding:
            issues.append(Issue(filepath, i, "WARNING", "NO_SWAGGER",
                f"Handler {handler_name}: missing Swagger annotation",
                "Add // @Summary, @Description, @Param, @Success, @Failure, @Router annotations"))
        
        # Rule: tenantID from Locals (check if handler uses tenant but takes from wrong source)
        if re.search(r'c\.(Query|Params)\s*\(\s*["\']tenant', ctx, re.I):
            issues.append(Issue(filepath, i, "BLOCKER", "TENANT_FROM_REQUEST",
                f"Handler {handler_name}: tenant_id from request params/query",
                'Use: tenantID := c.Locals("tenantID").(string)'))
    
    return issues

def check_path(path: str) -> List[Issue]:
    all_issues = []
    p = Path(path)
    if p.is_file():
        all_issues.extend(check_handler_file(str(p)))
    elif p.is_dir():
        for f in p.rglob('*.go'):
            if 'handler' in f.name.lower() and '_test' not in f.name:
                all_issues.extend(check_handler_file(str(f)))
    return all_issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>"); sys.exit(1)
    issues = check_path(sys.argv[1])
    if not issues:
        print("✅ All handlers pass API consistency check!"); sys.exit(0)
    blockers = [i for i in issues if i.severity == "BLOCKER"]
    print(f"\nXynPOS API Consistency Check")
    print(f"🔴 BLOCKERS: {len(blockers)} | ⚠️ WARNINGS: {len(issues)-len(blockers)}")
    for v in issues:
        icon = "🔴" if v.severity == "BLOCKER" else "⚠️"
        print(f"\n{icon} [{v.rule}] {v.file}:{v.line}\n   {v.message}\n   Fix: {v.suggestion}")
    sys.exit(1 if blockers else 0)
