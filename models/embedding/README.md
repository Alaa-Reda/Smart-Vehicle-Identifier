
# Embedding Model

## Overview

The Embedding Model is responsible for converting textual information into high-dimensional vector representations.

These vectors enable semantic similarity search within the Retrieval-Augmented Generation (RAG) pipeline, allowing the system to retrieve the most relevant vehicle information before generating a response.

The embedding model serves as the foundation of the project's retrieval system.

---

# Architecture Position

```
Vehicle Information

↓

Embedding Model

↓

Vector Embeddings

↓

FAISS Database

↓

Similarity Search

↓

Retrieved Context
```

---

# Responsibilities

The Embedding Model is responsible for:

- Converting text into vector embeddings.
- Supporting semantic search.
- Providing vectors for FAISS indexing.
- Encoding user queries before retrieval.

The model is NOT responsible for:

- Answer generation.
- Vehicle classification.
- Prompt engineering.
- Database operations.
- Business logic.

---

# Folder Structure

```
embedding/
│
├── README.md
├── install_embedding_model.py
├── local_embedding.py
└── online_embedding.py
```

---

# Files

## install_embedding_model.py

Downloads the embedding model for local execution.

This script is optional.

---

## local_embedding.py

Loads the locally installed embedding model and generates embeddings without requiring an internet connection.

---

## online_embedding.py

Uses an online embedding service for generating embeddings.

This is the default implementation if local execution is unavailable.

---

# Workflow

```
Input Text

↓

Embedding Model

↓

Vector

↓

FAISS Index

↓

Semantic Search
```

---

# Current Configuration

Default Mode

```
Online Embedding
```

Optional Mode

```
Local Embedding
```

---

# Used By

- Retriever
- FAISS Database
- Search Service
- RAG Pipeline

---

# Development Rules

- Generate embeddings only.
- Do not perform retrieval.
- Do not communicate with databases.
- Do not generate AI responses.
- Return vector representations only.

---

# Future Improvements

Possible future enhancements include:

- Local GPU acceleration.
- Multi-language embeddings.
- Hybrid embedding models.
- Automatic model selection.
- Cached embeddings.
