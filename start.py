from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

PYTHON = sys.executable

print("=" * 50)
print("Starting Smart Vehicle Identifier")
print("=" * 50)

# تشغيل Backend
backend = subprocess.Popen(
    [PYTHON, "run.py"],
    cwd=BACKEND,
)

# انتظار بسيط
time.sleep(5)

# تشغيل Frontend
frontend = subprocess.Popen(
    [
        PYTHON,
        "-m",
        "streamlit",
        "run",
        "app.py",
    ],
    cwd=FRONTEND,
)

try:
    backend.wait()
    frontend.wait()
except KeyboardInterrupt:
    backend.terminate()
    frontend.terminate()