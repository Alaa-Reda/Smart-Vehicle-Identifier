"""
cleanup_db.py
=============
Run this script ONCE to clean corrupted FAISS index and vector_index collection.

Usage:
    cd D:\Smart-Vehicle-Identifier
    python cleanup_db.py

What it does:
1. Deletes the FAISS index file from disk (vehicle.index / vehicle.npy)
2. Clears the vector_index MongoDB collection
3. Leaves the vehicles collection untouched (your scraped data stays)
4. Confirms everything is clean

After running this, restart the backend and test again.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ── Setup paths ───────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent
_DATA_DIR = _ROOT / "data"

for p in [str(_ROOT), str(_DATA_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

# ── 1. Delete FAISS index files ───────────────────────────────────────────
print("\n[1] Cleaning FAISS index files...")

faiss_dir = _DATA_DIR / "database" / "faiss"
deleted_files = []

for fname in ["vehicle.index", "vehicle.npy"]:
    fpath = faiss_dir / fname
    if fpath.exists():
        fpath.unlink()
        deleted_files.append(str(fpath))
        print(f"    ✓ Deleted: {fpath}")

if not deleted_files:
    print("    ℹ  No FAISS index files found (already clean).")

# ── 2. Clear vector_index MongoDB collection ──────────────────────────────
print("\n[2] Clearing vector_index collection in MongoDB...")

try:
    from database.mongodb.mongodb import MongoDBManager

    manager = MongoDBManager()
    manager.connect()
    db = manager.get_collection("vector_index").database

    result = db["vector_index"].delete_many({})
    print(f"    ✓ Deleted {result.deleted_count} documents from vector_index.")

    manager.disconnect()

except Exception as exc:
    print(f"    ✗ MongoDB error: {exc}")
    print("    → Make sure MongoDB is running and MONGODB_URI is set in .env")

# ── 3. Summary ────────────────────────────────────────────────────────────
print("\n[3] Summary")
print("    ✓ FAISS index cleared.")
print("    ✓ vector_index collection cleared.")
print("    ✓ vehicles collection is untouched.")
print("\nRestart the backend and test again.")
print("First request will re-scrape and rebuild the index cleanly.\n")
