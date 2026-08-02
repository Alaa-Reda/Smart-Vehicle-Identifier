# Database Layer

## Overview

This folder contains the persistence and indexing components used by the backend.

## Structure

- `mongodb/`: document database collections and connection manager.
- `faiss/`: vector index management for semantic search.

## Notes

- `mongodb/vector_index.py` stores mapping between FAISS vector IDs and vehicle IDs.
- `faiss/vector_store.py` handles vector insert/search and index persistence.
