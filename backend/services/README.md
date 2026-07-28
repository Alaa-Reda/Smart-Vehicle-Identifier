
# Backend Services Module

# ⚙️ Business Logic Layer

The `services` module contains the business logic of the Smart Vehicle Identifier system.

It acts as the bridge between the Controller layer and the core backend components such as the RAG module, Memory layer, AI Models, and Database.

Every business operation should be implemented inside a Service.

Controllers must never contain business logic.

---

# Architecture Position

```
Frontend
      │
      ▼
Routes
      │
      ▼
Controllers
      │
      ▼
Services
      │
 ┌────┼───────────────┐
 │    │       │       │
 ▼    ▼       ▼       ▼
RAG Memory Database Models
```

---

# Responsibilities

The Services module is responsible for:

- Implementing business logic.
- Coordinating backend modules.
- Managing complete workflows.
- Calling AI models.
- Communicating with the RAG pipeline.
- Managing Memory operations.
- Returning processed data to Controllers.

The Services module is NOT responsible for:

- HTTP Requests.
- API Routing.
- Database CRUD implementation.
- UI rendering.

---

# Folder Structure

```
services/
│
├── vehicle_service.py
├── search_service.py
└── compare_service.py
```

---

# File Specifications

---

# vehicle_service.py

## Purpose

Handles the complete vehicle analysis workflow.

This service is responsible for processing uploaded vehicle images and generating structured vehicle information.

---

## Main Class

```python
class VehicleService
```

---

## Responsibilities

- Receive image from Controller.
- Validate image.
- Call vehicle recognition model.
- Retrieve vehicle information.
- Save analysis result.
- Return vehicle object.

---

## Public Methods

### analyze_vehicle()

Complete vehicle analysis.

---

### validate_image()

Validate uploaded image.

---

### identify_vehicle()

Run vehicle recognition.

---

### save_vehicle()

Store analyzed vehicle.

---

### build_vehicle_response()

Generate final response object.

---

## Dependencies

Uses

- RAG Module
- Vehicle Memory
- Vehicle AI Model

---

# search_service.py

## Purpose

Handles intelligent search operations inside the system.

This service communicates with the RAG module to retrieve relevant information and generate contextual answers.

---

## Main Class

```python
class SearchService
```

---

## Responsibilities

- Receive search request.
- Build search workflow.
- Call RAG Manager.
- Retrieve relevant context.
- Generate intelligent response.

---

## Public Methods

### search()

Main search workflow.

---

### retrieve_context()

Retrieve relevant information.

---

### generate_answer()

Generate final answer.

---

### save_search_history()

Store search session.

---

## Dependencies

Uses

- RAG Manager
- Session Memory
- Retriever

---

# compare_service.py

## Purpose

Handles vehicle comparison operations.

This service compares two analyzed vehicles and generates a structured comparison report.

---

## Main Class

```python
class CompareService
```

---

## Responsibilities

- Load vehicle information.
- Validate comparison request.
- Generate comparison report.
- Save comparison history.
- Return formatted comparison.

---

## Public Methods

### compare()

Compare two vehicles.

---

### load_vehicle()

Retrieve vehicle information.

---

### validate_comparison()

Validate comparison request.

---

### build_report()

Generate comparison report.

---

### save_comparison()

Store comparison result.

---

## Dependencies

Uses

- Vehicle Memory
- Comparison Memory
- RAG Manager

---

# Service Workflow

```
Controller

↓

Service

↓

Business Logic

↓

RAG / Memory / Database

↓

Return Result
```

---

# Naming Convention

Files

```
vehicle_service.py

search_service.py

compare_service.py
```

Classes

```
VehicleService

SearchService

CompareService
```

Methods

```
analyze_vehicle()

search()

compare()

build_report()
```

---

# Development Rules

Every Service must follow these rules.

✅ One class per file.

✅ One business feature per service.

✅ Business logic belongs only here.

✅ Services may communicate with RAG, Memory, Models, and Database.

❌ No HTTP Requests.

❌ No Route Definitions.

❌ No UI Logic.

❌ No Direct Frontend Communication.

---

# Future Extensions

Possible future services

```
recommendation_service.py

analytics_service.py

authentication_service.py

feedback_service.py
```

Every new service should follow the same architecture and design principles.
