"""
run.py — Smart Vehicle Identifier launcher

Usage:
    cd D:\Smart-Vehicle-Identifier\backend
    python run.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ── Fix sys.path BEFORE uvicorn spawns the reloader subprocess ────────────
# When reload=True, uvicorn spawns a child process that re-imports app.py.
# That child inherits sys.path from THIS file, not from app.py.
# So ALL path setup must happen here.

_BACKEND_DIR      = Path(__file__).resolve().parent
_PROJECT_ROOT     = _BACKEND_DIR.parent
_DATA_DIR         = _PROJECT_ROOT / "data"          # contains database/
_MODELS_DIR       = _PROJECT_ROOT / "models"
_WEB_SCRAPING_DIR = _PROJECT_ROOT / "web_scraping"

for _p in [
    str(_BACKEND_DIR),
    str(_PROJECT_ROOT),
    str(_DATA_DIR),
    str(_MODELS_DIR),
    str(_WEB_SCRAPING_DIR),
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Load .env before importing anything else
from dotenv import load_dotenv
load_dotenv(str(_PROJECT_ROOT / ".env"))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        # reload=True causes the reloader subprocess to re-import app.py.
        # Keep False in production; set ENV=development to enable.
        reload=os.environ.get("ENV", "production") == "development",
        log_level="info",
    )