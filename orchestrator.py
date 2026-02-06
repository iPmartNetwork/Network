#!/usr/bin/env python3
from core.engine import Engine
import sys, os

def require_root():
    if os.geteuid() != 0:
        print("Run as root")
        sys.exit(1)

if __name__ == "__main__":
    require_root()
    engine = Engine()

    if "--daemon" in sys.argv:
        engine.run_daemon()
    else:
        engine.run_once()
