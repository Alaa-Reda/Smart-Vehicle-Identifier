
# Backend Memory Module

## Module Overview

The `memory` module is responsible for managing the application's runtime memory and user-related context.

It stores and retrieves user sessions, analyzed vehicles, comparison history, and conversation history.

This module acts as the communication layer between the backend services and the database layer.

---

# Architecture Position

```
Frontend
      │
      ▼
 Controller
      │
      ▼
 Service Layer
      │
      ▼
 Memory Layer
      │
      ▼
MongoDB / FAISS
```

---

# Responsibilities

The Memory module is responsible for:

- Managing user sessions.
- Storing analyzed vehicles.
- Storing comparison results.
- Storing chat history.
- Retrieving previous conversations.
- Retrieving previously analyzed vehicles.
- Updating existing records.
- Deleting records when requested.

The Memory module is NOT responsible for:

- AI inference.
- Prompt generation.
- Web scraping.
- Vehicle detection.
- Business logic.
- API handling.

---

# Folder Structure

```
memory/
│
├── session_memory.py
├── vehicle_memory.py
└── comparison_memory.py
```

---

# File Specifications

---

# session_memory.py

## Purpose

Responsible for managing user sessions.

Each user interaction belongs to one Session.

A session stores everything related to a single conversation.

---

## Main Class

```python
class SessionMemory
```

---

## Responsibilities

- Create new session.
- Load existing session.
- Update session.
- Delete expired sessions.
- Save current conversation state.

---

## Public Methods

### create_session()

Create a new session.

Returns

- Session ID

---

### get_session()

Retrieve session information.

Input

- Session ID

Output

- Session Object

---

### update_session()

Update session metadata.

---

### delete_session()

Delete session permanently.

---

### session_exists()

Check whether session already exists.

Returns

- True / False

---

## Dependencies

Uses

- MongoDB

Never communicates directly with

- Qwen
- FAISS
- Playwright

---

# vehicle_memory.py

## Purpose

Stores analyzed vehicles.

Every analyzed vehicle should be cached to avoid repeated searches.

---

## Main Class

```python
class VehicleMemory
```

---

## Responsibilities

- Save analyzed vehicle.
- Retrieve vehicle by ID.
- Retrieve vehicle by image hash.
- Update vehicle information.
- Delete vehicle.

---

## Public Methods

### save_vehicle()

Store analyzed vehicle.

---

### get_vehicle()

Retrieve vehicle information.

---

### update_vehicle()

Update vehicle data.

---

### delete_vehicle()

Delete vehicle.

---

### vehicle_exists()

Check whether vehicle already exists.

Returns

- True / False

---

## Dependencies

Uses

- MongoDB
- FAISS Metadata

---

# comparison_memory.py

## Purpose

Stores comparison history between vehicles.

Allows users to revisit previous comparisons without generating them again.

---

## Main Class

```python
class ComparisonMemory
```

---

## Responsibilities

- Save comparison.
- Retrieve comparison.
- Delete comparison.
- List previous comparisons.

---

## Public Methods

### save_comparison()

Save comparison result.

---

### get_comparison()

Retrieve saved comparison.

---

### delete_comparison()

Delete comparison.

---

### get_all_comparisons()

Return comparison history.

---

## Dependencies

Uses

- MongoDB

---

# Memory Flow

```
User

↓

Controller

↓

Service

↓

Memory

↓

MongoDB

↓

Return Object
```

---

# Database Collections

Suggested MongoDB collections

```
sessions

vehicles

comparisons

history
```

---

# Naming Convention

## Files

```
session_memory.py

vehicle_memory.py

comparison_memory.py
```

---

## Classes

```
SessionMemory

VehicleMemory

ComparisonMemory
```

---

## Methods

```
create_session()

get_session()

save_vehicle()

get_vehicle()

save_comparison()

get_comparison()
```

Method names must follow **snake_case**.

Class names must follow **PascalCase**.

---

# Development Rules

Every Memory class must follow these rules.

✅ One file = One Memory class.

✅ Memory communicates only with the Database layer.

✅ No AI logic.

✅ No Prompt Engineering.

✅ No Web Scraping.

✅ No HTTP Requests.

✅ No Business Logic.

✅ Return Python objects only.

---

# Future Extensions

Possible future memory modules

```
history_memory.py

favorites_memory.py

cache_memory.py

analytics_memory.py
```

Each new module should follow the same architecture and naming conventions.
