#!/usr/bin/env python3
"""
XynPOS Security Scanner
Multi-language security pattern scanner.

Usage:
    python scripts/security_scan.py <path>
    python scripts/security_scan.py backend/
    python scripts/security_scan.py backend/services/auth-service/
"""
import sys, re, os
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Finding:
    file: str; line: int; severity: str; cwe: str; title: str; detail: str; fix: str

def scan_go(filepath: str, lines: list) -> List[Finding]:
    findings = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith('//'): continue
        
        # CWE-89: SQL Injection
        if re.search(r'(Exec|Raw)\s*\(["\'].*\+', line):
            findings.append(Finding(filepath, i, "CRITICAL", "CWE-89",
                "SQL Injection", f"String concatenation in SQL: {s[:80]}",
                "Use parameterized queries: db.Where(\"id = ?\", id)"))
        
        # CWE-522: Broken Auth - tenant from request
        if re.search(r'c\.(Query|Params|FormValue)\s*\(\s*["\']tenant_id', line, re.I):
            findings.append(Finding(filepath, i, "CRITICAL", "CWE-284",
                "Tenant Isolation Bypass", "tenant_id read from request — attacker can impersonate",
                'Use: tenantID := c.Locals("tenantID").(string)'))
        
        # CWE-532: Sensitive data in logs
        for sensitive in ['password', 'passwd', 'pin', 'secret', 'token', 'npwp', 'card_number']:
            if re.search(rf'zap\.\w+\(\s*["\'][^"\']*{sensitive}', line, re.I):
                findings.append(Finding(filepath, i, "HIGH", "CWE-532",
                    "Sensitive Data in Log", f"Logging sensitive field '{sensitive}'",
                    "Remove or mask sensitive data from logs"))
        
        # CWE-798: Hardcoded credentials
        if re.search(r'(password|secret|apikey)\s*:?=\s*["\'][^"\']{8,}["\']', line, re.I):
            if 'test' not in filepath.lower() and 'example' not in filepath.lower():
                findings.append(Finding(filepath, i, "CRITICAL", "CWE-798",
                    "Hardcoded Credential", f"Possible hardcoded secret: {s[:60]}",
                    "Load from environment: os.Getenv(\"SECRET_KEY\")"))
        
        # CWE-390: panic in non-main
        if 'panic(' in line and 'cmd/main.go' not in filepath and '_test.go' not in filepath:
            findings.append(Finding(filepath, i, "MEDIUM", "CWE-390",
                "Panic in Production Code", "panic() will crash the entire service",
                "Return error instead of panicking"))
    
    return findings

def scan_file(filepath: str) -> List[Finding]:
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return []
    
    ext = Path(filepath).suffix
    if ext == '.go':
        return scan_go(filepath, lines)
    # Add .ts, .dart scanners as needed
    return []

def scan_path(path: str) -> List[Finding]:
    all_findings = []
    p = Path(path)
    if p.is_file():
        all_findings.extend(scan_file(str(p)))
    elif p.is_dir():
        for f in p.rglob('*'):
            if f.is_file() and f.suffix in {'.go', '.ts', '.dart'}:
                skip = {'vendor/', 'node_modules/', '.git/', 'mock/', '.pb.go'}
                if not any(s in str(f) for s in skip):
                    all_findings.extend(scan_file(str(f)))
    return all_findings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>"); sys.exit(1)
    findings = scan_path(sys.argv[1])
    if not findings:
        print("✅ No security issues found!"); sys.exit(0)
    
    by_sev = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
    for f in findings:
        by_sev.get(f.severity, by_sev['LOW']).append(f)
    
    print(f"\n🔒 XynPOS Security Scan Results")
    print(f"🚨 CRITICAL: {len(by_sev['CRITICAL'])} | 🔴 HIGH: {len(by_sev['HIGH'])} | ⚠️ MEDIUM: {len(by_sev['MEDIUM'])}")
    print("="*60)
    
    for sev in ['CRITICAL', 'HIGH', 'MEDIUM']:
        for f in by_sev[sev]:
            icons = {'CRITICAL':'🚨','HIGH':'🔴','MEDIUM':'⚠️'}
            print(f"\n{icons[sev]} [{f.cwe}] {f.title}")
            print(f"   File: {f.file}:{f.line}")
            print(f"   Detail: {f.detail}")
            print(f"   Fix: {f.fix}")
    
    sys.exit(1 if by_sev['CRITICAL'] or by_sev['HIGH'] else 0)
