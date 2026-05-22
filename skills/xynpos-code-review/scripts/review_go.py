#!/usr/bin/env python3
"""
XynPOS Go Code Review
Comprehensive review combining all Go rules.

Usage:
    python scripts/review_go.py <path>
"""
import sys, subprocess
from pathlib import Path

def run_check(script: str, path: str) -> tuple:
    """Run a check script and return (returncode, output)"""
    try:
        result = subprocess.run(
            [sys.executable, script, path],
            capture_output=True, text=True
        )
        return result.returncode, result.stdout + result.stderr
    except FileNotFoundError:
        return 0, f"[Script {script} not found — skipping]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>"); sys.exit(1)
    
    path = sys.argv[1]
    print(f"\n{'='*60}")
    print(f"XynPOS Go Code Review: {path}")
    print(f"{'='*60}")
    
    skills_dir = Path(__file__).parent.parent.parent
    
    checks = [
        (str(skills_dir / "xynpos-go-backend/scripts/check_rules.py"), "Go Dev Rules"),
        (str(skills_dir / "xynpos-security/scripts/security_scan.py"), "Security Scan"),
        (str(skills_dir / "xynpos-api-design/scripts/check_api_consistency.py"), "API Consistency"),
    ]
    
    total_blockers = 0
    for script, name in checks:
        print(f"\n▶ Running: {name}")
        rc, output = run_check(script, path)
        print(output)
        if rc != 0:
            total_blockers += 1
    
    print(f"\n{'='*60}")
    if total_blockers == 0:
        print("✅ CODE REVIEW PASSED — no blockers found")
    else:
        print(f"🔴 {total_blockers} check(s) found blockers — fix before merging")
    print(f"{'='*60}\n")
    sys.exit(0 if total_blockers == 0 else 1)
