#!/usr/bin/env python3
"""XynPOS TypeScript/React Code Review wrapper."""
import sys, subprocess
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>"); sys.exit(1)
    
    skills_dir = Path(__file__).parent.parent.parent
    fe_check = str(skills_dir / "xynpos-frontend/scripts/check_fe_rules.py")
    
    result = subprocess.run([sys.executable, fe_check, sys.argv[1]], capture_output=False)
    sys.exit(result.returncode)
