
# MongoDB Database Layer

## Overview

The `mongodb` module is responsible for managing all persistent application data in the Smart Vehicle Identifier system.

It provides a structured interface for storing, retrieving, updating, and deleting application data while isolating database operations from the rest of the backend.

This module serves as the database implementation layer and is accessed only through the Memory layer.

---

# Architecture Position

```
Frontend
      │
      ▼
Controllers
      │
      ▼
Services
      │
      ▼
Memory Layer
      │
      ▼
MongoDB Layer
      │
      ▼
MongoDB Database
```

---

# Responsibilities

The MongoDB module is responsible for:

- Managing the database connection.
- Storing application data.
- Retrieving stored records.
- Updating existing records.
- Deleting records.
- Managing MongoDB collections.

The MongoDB module is **NOT** responsible for:

- Business logic.
- AI inference.
- HTTP requests.
- Prompt generation.
- Retrieval operations.
- Session management logic.

---

# Folder Structure

```
mongodb/
│
├── mongodb.py
├── session.py
├── vehicle.py
├── history.py
├── comparison.py
└── vector_index.py
```

---

# File Specifications

---

# mongodb.py

## Purpose

Provides the MongoDB database connection and initializes the application database.

All collection modules use this file to access the database.

---

## Main Class

```python
class MongoDBManager
```

---

## Responsibilities

- Connect to MongoDB.
- Initialize the database.
- Provide collection instances.
- Handle connection lifecycle.
- Perform database health checks.

---

## Public Methods

### connect()

Establish database connection.

---

### disconnect()

Close database connection.

---

### get_database()

Return the active database instance.

---

### get_collection()

Return a MongoDB collection.

---

### collection_exists()

Check whether a collection exists.

---

### health_check()

Verify that MongoDB is reachable.

---

# session.py

## Purpose

Manages the **Sessions** collection.

Stores user sessions and conversation metadata.

---

## Main Class

```python
class SessionCollection
```

---

## Responsibilities

- Store sessions.
- Retrieve sessions.
- Update sessions.
- Delete sessions.

---

## Public Methods

### insert()

Insert a new session.

---

### find_by_id()

Retrieve a session.

---

### find_all()

Retrieve all sessions.

---

### update()

Update session data.

---

### delete()

Delete a session.

---

### count()

Return total sessions.

---

# vehicle.py

## Purpose

Manages the **Vehicles** collection.

Stores analyzed vehicle information.

---

## Main Class

```python
class VehicleCollection
```

---

## Responsibilities

- Store vehicle information.
- Retrieve vehicle records.
- Update vehicle data.
- Delete vehicle records.

---

## Public Methods

### insert()

Insert vehicle.

---

### find_by_id()

Retrieve vehicle.

---

### find_all()

Retrieve all vehicles.

---

### update()

Update vehicle.

---

### delete()

Delete vehicle.

---

### count()

Return total vehicles.

---

# history.py

## Purpose

Manages the **History** collection.

Stores user conversation history.

---

## Main Class

```python
class HistoryCollection
```

---

## Responsibilities

- Store chat history.
- Retrieve chat history.
- Update history.
- Delete history.

---

## Public Methods

### insert()

Insert history record.

---

### find_by_id()

Retrieve history.

---

### find_by_session()

Retrieve all messages for a session.

---

### find_all()

Retrieve all history records.

---

### update()

Update history.

---

### delete()

Delete history item.

---

### delete_session_history()

Delete all history for a session.

---

### count()

Return total history records.

---

# comparison.py

## Purpose

Manages the **Comparisons** collection.

Stores vehicle comparison results.

---

## Main Class

```python
class ComparisonCollection
```

---

## Responsibilities

- Store comparisons.
- Retrieve comparisons.
- Update comparisons.
- Delete comparisons.

---

## Public Methods

### insert()

Insert comparison.

---

### find_by_id()

Retrieve comparison.

---

### find_by_session()

Retrieve session comparisons.

---

### find_all()

Retrieve all comparisons.

---

### update()

Update comparison.

---

### delete()

Delete comparison.

---

### count()

Return total comparisons.

---

# vector_index.py

## Purpose

Manages the **Vector Index** collection.

Stores the mapping between FAISS vector IDs and vehicle documents.

---

## Main Class

```python
class VectorIndexCollection
```

---

## Responsibilities

- Store vector mappings.
- Retrieve mappings.
- Update mappings.
- Delete mappings.

---

## Public Methods

### insert()

Insert a new vector mapping.

---

### find_by_id()

Retrieve mapping by document ID.

---

### find_by_vector_id()

Retrieve mapping using a FAISS vector ID.

---

### find_by_vehicle_id()

Retrieve mapping using a vehicle ID.

---

### update()

Update mapping.

---

### delete()

Delete mapping.

---

### count()

Return total mappings.

---

# Database Collections

The MongoDB database contains the following collections:

```
sessions

vehicles

history

comparisons

vector_index
```

---

# Communication

The MongoDB module communicates only with the Memory layer.

```
Memory Layer

↓

MongoDB Layer

↓

MongoDB
```

Controllers, Services, Retrieval, and RAG modules should never access MongoDB directly.

---

# Naming Convention

## Files

```
mongodb.py

session.py

vehicle.py

history.py

comparison.py

vector_index.py
```

---

## Classes

```
MongoDBManager

SessionCollection

VehicleCollection

HistoryCollection

ComparisonCollection

VectorIndexCollection
```

---

## Methods

```
connect()

disconnect()

get_database()

get_collection()

collection_exists()

health_check()

insert()

find_by_id()

find_all()

update()

delete()

count()
```

Method names follow **snake_case**.

Class names follow **PascalCase**.

---

# Development Rules

Every MongoDB component must follow these rules.

- One collection per file.
- One responsibility per class.
- No business logic.
- No AI processing.
- No HTTP communication.
- Return Python objects only.
- Keep database operations isolated from the rest of the backend.

---

# Future Improvements

Possible future collections include:

```
users.py

favorites.py

feedback.py

analytics.py

logs.py

cache.py
```

Each new collection should follow the same architecture and development rules.ط
