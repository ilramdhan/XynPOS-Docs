#!/usr/bin/env python3
"""
XynPOS Dockerfile Validator
Checks Dockerfiles against XynPOS infrastructure rules.

Usage:
    python scripts/validate_dockerfile.py <Dockerfile-path>
    python scripts/validate_dockerfile.py backend/services/pos-service/Dockerfile
"""
import sys, re
from pathlib import Path

def validate(path: str) -> list:
    issues = []
    content = Path(path).read_text()
    lines = content.splitlines()
    
    # Rule: Must be multi-stage
    from_count = sum(1 for l in lines if re.match(r'^FROM\s', l, re.I))
    if from_count < 2:
        issues.append(("BLOCKER", "NOT_MULTISTAGE", "Single-stage Dockerfile — must use multi-stage build", 
                       "Add a builder stage and a minimal runtime stage (alpine)"))
    
    # Rule: No :latest tag
    for i, line in enumerate(lines, 1):
        if re.match(r'^FROM\s+\S+:latest', line, re.I):
            issues.append(("BLOCKER", "LATEST_TAG", f"Line {i}: ':latest' tag used — must pin exact version",
                          "Pin version: FROM golang:1.22.3-alpine3.19"))
    
    # Rule: Non-root user
    if 'adduser' not in content and 'addgroup' not in content and 'USER' not in content:
        issues.append(("BLOCKER", "ROOT_USER", "No non-root user — container runs as root",
                      "Add: RUN addgroup -S app && adduser -S app -G app\nUSER app"))
    
    # Rule: HEALTHCHECK
    if 'HEALTHCHECK' not in content:
        issues.append(("WARNING", "NO_HEALTHCHECK", "No HEALTHCHECK instruction",
                      "Add: HEALTHCHECK --interval=30s --timeout=10s CMD wget -qO- http://localhost:${PORT}/health || exit 1"))
    
    # Rule: .dockerignore should exist
    dockerfile_dir = Path(path).parent
    dockerignore = dockerfile_dir / '.dockerignore'
    if not dockerignore.exists():
        issues.append(("WARNING", "NO_DOCKERIGNORE", "No .dockerignore file found",
                      "Create .dockerignore to exclude: .git, *.env, *_test.go, node_modules/"))
    
    # Rule: No secrets in ENV
    for i, line in enumerate(lines, 1):
        if re.match(r'^ENV\s.*(SECRET|PASSWORD|KEY|TOKEN)\s*=\s*.+', line, re.I):
            issues.append(("BLOCKER", "SECRET_IN_ENV", f"Line {i}: Secret in ENV instruction",
                          "Use --build-arg or runtime environment injection via Doppler"))
    
    return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <Dockerfile>"); sys.exit(1)
    
    issues = validate(sys.argv[1])
    if not issues:
        print("✅ Dockerfile passes all XynPOS rules!"); sys.exit(0)
    
    blockers = [i for i in issues if i[0] == "BLOCKER"]
    print(f"\n🔴 BLOCKERS: {len(blockers)} | ⚠️ WARNINGS: {len(issues)-len(blockers)}")
    for severity, rule, msg, fix in issues:
        icon = "🔴" if severity == "BLOCKER" else "⚠️"
        print(f"\n{icon} [{rule}]\n   Problem: {msg}\n   Fix: {fix}")
    sys.exit(1 if blockers else 0)
