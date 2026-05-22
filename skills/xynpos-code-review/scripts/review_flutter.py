#!/usr/bin/env python3
"""XynPOS Flutter Code Review wrapper."""
import sys, subprocess
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>"); sys.exit(1)
    
    skills_dir = Path(__file__).parent.parent.parent
    flutter_check = str(skills_dir / "xynpos-mobile/scripts/check_flutter_rules.py")
    
    result = subprocess.run([sys.executable, flutter_check, sys.argv[1]], 
                           capture_output=False)
    sys.exit(result.returncode)
