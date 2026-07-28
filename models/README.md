# AI Models

## Overview

The `models` module contains all artificial intelligence models used by the Smart Vehicle Identifier system.

These models provide the core AI capabilities of the application, including vehicle classification, semantic embedding generation, and visual language understanding.

Each model has a dedicated responsibility and operates independently within the overall AI pipeline.

---

# Architecture Position

```
Vehicle Image
      │
      ▼
Car Classification Model
      │
      ▼
Detected Vehicle
      │
      ├──────────────┐
      ▼              ▼
Embedding Model   Qwen Vision-Language Model
      │              │
      ▼              ▼
FAISS Retrieval   Intelligent Reasoning
      │              │
      └──────┬───────┘
             ▼
      Final AI Response
```

---

# Folder Structure

```
models/
│
├── README.md
├── loaders.py
│
├── car_classification_model/
│
├── embedding/
│
└── qwen/
```

---

# Model Specifications

## Car Classification Model

### Purpose

Analyzes vehicle images and predicts the most likely vehicle class.

### Responsibilities

- Vehicle recognition
- Vehicle classification
- Confidence estimation

---

## Embedding Model

### Purpose

Converts textual information into vector embeddings for semantic search.

### Responsibilities

- Text encoding
- Vector generation
- Query embedding
- Knowledge embedding

---

## Qwen Vision-Language Model

### Purpose

Provides intelligent reasoning and natural language understanding.

### Responsibilities

- Visual Question Answering (VQA)
- Vehicle understanding
- Context-aware response generation
- Natural language interaction

---

## loaders.py

### Purpose

Provides a centralized interface for loading and managing all AI models used by the project.

This module ensures that models are loaded consistently and can be shared across the application.

---

### Responsibilities

- Load AI models.
- Initialize model resources.
- Manage model instances.
- Provide reusable model loaders.

---

# Model Workflow

```
Image

↓

Car Classification Model

↓

Vehicle Prediction

↓

Vehicle Service

↓

Embedding Model

↓

FAISS Retrieval

↓

Qwen Model

↓

Generated Response
```

---

# Design Principles

The models module follows these principles:

- One responsibility per model.
- Centralized model loading.
- Independent model management.
- Reusable AI components.
- Separation between model assets and application logic.

---

# Communication

The models module is used by:

- Vehicle Service
- Search Service
- Compare Service
- RAG Pipeline

The models do not communicate directly with:

- Frontend
- Database
- Controllers
- Routes

---

# Development Rules

Every model should:

- Have a single responsibility.
- Be loaded through `loaders.py`.
- Remain independent from business logic.
- Avoid direct database communication.
- Avoid HTTP communication.
- Focus only on AI inference.

---

# Future Improvements

Possible future enhancements include:

- Additional vision models.
- OCR integration.
- Object detection models.
- Model quantization.
- GPU optimization.
- Automatic model selection.
- Multi-model ensemble support.
