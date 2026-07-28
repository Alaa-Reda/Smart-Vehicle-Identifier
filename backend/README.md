
# Backend

# Smart Vehicle Identifier Backend

## Overview

The Backend is the core processing layer of the Smart Vehicle Identifier system.

It is responsible for receiving API requests, executing business logic, managing AI workflows, retrieving vehicle knowledge, storing user sessions, and generating intelligent responses.

The backend follows a layered architecture based on the **Separation of Concerns (SoC)** principle, ensuring that every module has a single, well-defined responsibility.

---

# High-Level Architecture

```
                 Smart Vehicle Identifier Backend

                      FastAPI (app.py)
                             │
                             ▼
                         API Routes
                             │
                             ▼
                        Controllers
                             │
                             ▼
                          Services
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
             RAG Module          Memory Module
                  │                     │
                  └──────────┬──────────┘
                             ▼
                     Database Layer
                   MongoDB + FAISS
```

---

# Detailed Backend Architecture

```
                           Smart Vehicle Identifier Backend

                                        FastAPI
                                           │
                                           ▼
                                   backend/app.py
                                           │
                                           ▼
                                     API Routers
                                           │
               ┌──────────────┬────────────┴──────────────┬──────────────┐
               ▼              ▼                           ▼              ▼
        Image Routes    Chat Routes               Compare Routes   History Routes
               │              │                           │              │
               └──────────────┴────────────┬──────────────┴──────────────┘
                                           ▼
                                     Controllers Layer
               ┌──────────────┬────────────┴──────────────┬──────────────┐
               ▼              ▼                           ▼              ▼
       ImageController  ChatController           CompareController  HistoryController
                                           │
                                           ▼
                                      Services Layer
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
             VehicleService       SearchService      CompareService
                                           │
                 ┌─────────────────────────┼──────────────────────────┐
                 ▼                         ▼                          ▼
            RAG Module              Memory Module             AI Models
                 │                         │
      ┌──────────┼──────────┐             │
      ▼          ▼          ▼             ▼
 Retriever  ContextBuilder PromptBuilder SessionMemory
      │          │          │             │
      ▼          ▼          ▼             ▼
 ResponseGenerator    RAGManager     VehicleMemory
                                          │
                                          ▼
                                  ComparisonMemory
                                          │
                                          ▼
                                  Database Layer
                                          │
                             MongoDB + FAISS + Cache
```

---

# Backend Structure

```
backend/
│
├── app.py
│
├── controllers/
│   ├── README.md
│   ├── chat_controller.py
│   ├── compare_controller.py
│   ├── history_controller.py
│   └── image_controller.py
│
├── routes/
│   ├── README.md
│   ├── chat_routes.py
│   ├── compare_routes.py
│   ├── history_routes.py
│   └── image_routes.py
│
├── services/
│   ├── README.md
│   ├── vehicle_service.py
│   ├── search_service.py
│   └── compare_service.py
│
├── rag/
│   ├── README.md
│   ├── pipeline.py
│   ├── rag_manager.py
│   ├── retriever.py
│   ├── context_builder.py
│   ├── prompt_builder.py
│   └── response_generator.py
│
└── memory/
    ├── README.md
    ├── session_memory.py
    ├── vehicle_memory.py
    └── comparison_memory.py
```

---

# Module Responsibilities

## Routes

Responsible for defining and registering all API endpoints.

**Responsibilities**

- Register API endpoints.
- Receive HTTP requests.
- Forward requests to Controllers.

Documentation

```
backend/routes/README.md
```

---

## Controllers

Responsible for handling incoming requests.

**Responsibilities**

- Validate requests.
- Receive user input.
- Call Services.
- Return standardized JSON responses.

Documentation

```
backend/controllers/README.md
```

---

## Services

Responsible for implementing the application's business logic.

**Responsibilities**

- Coordinate backend workflows.
- Call RAG.
- Communicate with Memory.
- Manage AI operations.

Documentation

```
backend/services/README.md
```

---

## RAG ⭐

**Core Intelligence Module**

The RAG module is the heart of the Smart Vehicle Identifier system.

It combines Retrieval-Augmented Generation with AI models to provide intelligent, contextual answers.

**Responsibilities**

- Retrieval
- Context Building
- Prompt Engineering
- Response Generation
- AI Workflow Orchestration

Documentation

```
backend/rag/README.md
```

---

## Memory

Responsible for maintaining user state and application memory.

**Responsibilities**

- Session Management
- Vehicle Cache
- Comparison History
- Conversation Memory

Documentation

```
backend/memory/README.md
```

---

# Backend Request Flow

```
Frontend

↓

FastAPI

↓

Routes

↓

Controllers

↓

Services

↓

RAG / Memory

↓

Database

↓

JSON Response

↓

Frontend
```

---

# Vehicle Analysis Workflow

```
User Uploads Image

↓

Image Route

↓

Image Controller

↓

Vehicle Service

↓

Vehicle Recognition Model

↓

Vehicle Memory

↓

Frontend
```

---

# Vehicle Question Answering Workflow

```
User Question

↓

Chat Route

↓

Chat Controller

↓

Search Service

↓

RAG Manager

↓

Retriever

↓

Context Builder

↓

Prompt Builder

↓

Response Generator

↓

Frontend
```

---

# Vehicle Comparison Workflow

```
User Selects Two Vehicles

↓

Compare Route

↓

Compare Controller

↓

Compare Service

↓

Vehicle Memory

↓

RAG Manager

↓

Comparison Report

↓

Frontend
```

---

# Design Principles

The backend architecture follows modern software engineering principles:

- Separation of Concerns (SoC)
- Single Responsibility Principle (SRP)
- Layered Architecture
- Modular Design
- Loose Coupling
- High Cohesion
- Scalability
- Maintainability

---

# Layer Dependency

Each layer communicates only with the layer directly below it.

```
Routes

↓

Controllers

↓

Services

↓

RAG / Memory

↓

Database
```

This dependency model minimizes coupling and makes the backend easier to maintain, test, and extend.

---

# Development Guidelines

All backend modules should follow these rules:

- One responsibility per module.
- One class per file.
- Controllers must remain lightweight.
- Business logic belongs only in Services.
- RAG handles all intelligent reasoning.
- Memory manages sessions and cached data.
- Routes should only register API endpoints.
- Database access should never occur directly inside Controllers.

---

# Future Improvements

Possible future backend modules:

```
authentication/

analytics/

feedback/

recommendation/

notifications/

logging/
```

Each new module should follow the same architecture and design principles.

---

# Related Documentation

```
backend/
│
├── README.md
│
├── controllers/
│   └── README.md
│
├── services/
│   └── README.md
│
├── rag/
│   └── README.md
│
├── memory/
│   └── README.md
│
└── routes/
    └── README.md
```

Each submodule contains its own detailed documentation describing its files, classes, methods, workflows, and development guidelines.
