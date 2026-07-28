# FAISS Vector Database

## Overview

The `faiss` module is responsible for managing the vector database used by the Retrieval-Augmented Generation (RAG) system.

It stores vector embeddings of vehicle-related information and enables fast similarity search, allowing the system to retrieve the most relevant context before generating a response.

This module is a core component of the retrieval process and significantly improves the accuracy and efficiency of intelligent question answering.

---

# Architecture Position

```
User Question
      │
      ▼
 Search Service
      │
      ▼
 RAG Manager
      │
      ▼
 Retriever
      │
      ▼
 FAISS Database
      │
      ▼
 Top-K Similar Documents
      │
      ▼
 Context Builder
```

---

# Responsibilities

The FAISS module is responsible for:

- Storing vector embeddings.
- Performing similarity search.
- Returning the Top-K most relevant vectors.
- Managing FAISS indexes.
- Loading and saving vector indexes.
- Associating vectors with metadata.

The FAISS module is **NOT** responsible for:

- Generating embeddings.
- Prompt engineering.
- AI inference.
- Database CRUD.
- HTTP requests.

---

# Folder Structure

```
faiss/
│
├── index/
├── metadata/
└── faiss.py
```

---

# Components

## index/

### Purpose

Stores serialized FAISS index files.

These files contain the vector indexes used for similarity search.

Typical contents include:

- IndexFlatIP
- IndexFlatL2
- IVF indexes
- Other optimized FAISS indexes

---

## metadata/

### Purpose

Stores metadata associated with each vector inside the FAISS index.

Typical metadata includes:

- Vehicle ID
- Brand
- Model
- Year
- Source document
- Chunk ID
- Image ID

The metadata allows the system to map retrieved vectors back to meaningful application data.

---

## faiss.py

### Purpose

Implements all interactions with the FAISS vector database.

---

### Main Class

```python
class FAISSManager
```

---

### Responsibilities

- Create vector indexes.
- Load existing indexes.
- Save indexes.
- Add vectors.
- Remove vectors.
- Search vectors.
- Return Top-K results.

---

### Public Methods

#### initialize()

Initialize the FAISS database.

---

#### load_index()

Load an existing FAISS index.

---

#### save_index()

Persist the current index.

---

#### add_vectors()

Insert new embeddings into the index.

---

#### search()

Perform similarity search.

Input

- Query Embedding
- Top-K

Output

- Ranked Results

---

#### delete_vector()

Remove a vector from the index.

---

# Retrieval Workflow

```
Question

↓

Embedding Model

↓

Query Embedding

↓

FAISS Search

↓

Top-K Results

↓

Metadata Mapping

↓

Context Builder
```

---

# Dependencies

Used by:

- Retriever
- SearchService
- RAG Manager

Depends on:

- Embedding Model
- Metadata Storage

---

# Naming Convention

## Files

```
faiss.py
```

---

## Classes

```
FAISSManager
```

---

## Methods

```
initialize()

load_index()

save_index()

add_vectors()

search()

delete_vector()
```

---

# Development Rules

Every FAISS component must follow these rules.

- One responsibility per class.
- Store vectors only.
- Keep metadata separated from vector indexes.
- Return ranked search results.
- Avoid embedding generation inside this module.
- No business logic.
- No HTTP communication.

---

# Future Improvements

Possible future enhancements include:

- Hybrid Retrieval
- HNSW Indexes
- IVF-PQ Optimization
- GPU Acceleration
- Incremental Index Updates
- Distributed Vector Storage
