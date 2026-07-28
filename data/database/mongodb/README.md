
# MongoDB Database Layer

## Overview

The `mongodb` module is responsible for managing all persistent application data in the Smart Vehicle Identifier system.

It provides a structured interface for storing, retrieving, updating, and deleting application data while isolating database operations from the rest of the backend.

This module serves as the database implementation layer and is accessed only through the Memory module.

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

The MongoDB module is NOT responsible for:

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
└── comparison.py
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

- Create session.
- Retrieve session.
- Update session.
- Delete session.

---

## Public Methods

### create()

Insert a new session.

---

### find_by_id()

Retrieve a session.

---

### update()

Update session data.

---

### delete()

Delete a session.

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

### update()

Update vehicle.

---

### delete()

Delete vehicle.

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
- Retrieve conversation history.
- Delete conversation records.

---

## Public Methods

### insert()

Save history record.

---

### get_history()

Retrieve history.

---

### delete()

Delete history item.

---

### clear()

Delete all history.

---

# comparison.py

## Purpose

Manages the **Comparisons** collection.

Stores previous vehicle comparison results.

---

## Main Class

```python
class ComparisonCollection
```

---

## Responsibilities

- Save comparison.
- Retrieve comparison.
- Delete comparison.
- List comparisons.

---

## Public Methods

### insert()

Save comparison.

---

### find_by_id()

Retrieve comparison.

---

### get_all()

Retrieve comparison history.

---

### delete()

Delete comparison.

---

# Database Collections

The MongoDB database contains the following collections:

```
sessions

vehicles

history

comparisons
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

Controllers, Services, and the RAG module should never access MongoDB directly.

---

# Naming Convention

## Files

```
mongodb.py

session.py

vehicle.py

history.py

comparison.py
```

---

## Classes

```
MongoDBManager

SessionCollection

VehicleCollection

HistoryCollection

ComparisonCollection
```

---

## Methods

```
connect()

disconnect()

insert()

update()

delete()

find_by_id()

get_all()
```

Method names should follow **snake_case**.

Class names should follow **PascalCase**.

---

# Development Rules

Every MongoDB component must follow these rules.

- One collection per file.
- One responsibility per class.
- No business logic.
- No AI processing.
- No HTTP communication.
- Return Python objects only.
- Keep database operations isolated from other backend modules.

---

# Future Improvements

Possible future collections include:

```
users.py

favorites.py

feedback.py

analytics.py

logs.py
```

Each new collection should follow the same architecture and development rules.
