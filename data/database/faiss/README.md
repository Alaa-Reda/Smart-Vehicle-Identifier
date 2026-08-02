# FAISS Database Layer

## Overview

This module manages vector indexing and similarity search for embeddings.

It is designed as a lightweight infrastructure layer used by retrieval components.

## Files

- `faiss_manager.py`: low-level index creation, add, search, save, and load.
- `vector_store.py`: high-level wrapper with default storage path and lifecycle helpers.

## Notes

- Uses `faiss` when available.
- Falls back to a NumPy in-memory index when `faiss` is not installed.
