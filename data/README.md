

# Database Overview

## Purpose

The **Database** layer is responsible for storing, retrieving, and managing all persistent data used by the Smart Vehicle Identifier system.

Unlike the AI models, which generate predictions and responses, the Database layer preserves important information so it can be reused in future interactions.

The system combines two complementary storage technologies:

- **MongoDB** for structured application data.
- **FAISS** for vector similarity search.

Together, they provide both traditional database operations and semantic retrieval capabilities required by the RAG pipeline.

---

# Responsibilities

The Database layer is responsible for:

- Managing user sessions.
- Storing conversation history.
- Saving vehicle information.
- Saving comparison results.
- Maintaining vector-to-document mappings.
- Managing FAISS vector indexes.
- Providing persistent storage for the RAG system.
- Supporting semantic search.

---

# Architecture

```text
Frontend

↓

Backend

↓

AI Models

↓

Database Layer

├── MongoDB
│
│   ├── Sessions
│   ├── History
│   ├── Vehicles
│   ├── Comparisons
│   └── Vector Mapping
│
└── FAISS
    ├── Vector Index
    └── Similarity Search
```

---

# Folder Structure

```text
database/

├── faiss/
│   ├── faiss_manager.py
│   ├── vector_store.py
│   └── __init__.py
│
└── mongodb/
    ├── mongodb.py
    ├── session.py
    ├── history.py
    ├── vehicle.py
    ├── comparison.py
    └── vector_index.py
```

---

# Main Components

| Component        | Responsibility                            |
| ---------------- | ----------------------------------------- |
| mongodb.py       | MongoDB connection manager (Singleton)    |
| session.py       | Store and manage user sessions            |
| history.py       | Store chat history                        |
| vehicle.py       | Store vehicle information                 |
| comparison.py    | Store vehicle comparisons                 |
| vector_index.py  | Map FAISS vector IDs to MongoDB documents |
| faiss_manager.py | Low-level FAISS index management          |
| vector_store.py  | High-level vector database abstraction    |

---

# Database Workflow

```text
AI Response

↓

Backend

↓

Store Structured Data

↓

MongoDB

↓

Generate Embedding

↓

FAISS

↓

Vector Mapping

↓

Future Semantic Search
```

---

# MongoDB Responsibilities

MongoDB stores all structured application data.

Collections include:

- Sessions
- Chat History
- Vehicles
- Comparisons
- Vector Mapping

MongoDB is responsible for persistence and CRUD operations.

---

# FAISS Responsibilities

FAISS stores numerical embeddings generated from vehicle information.

It is responsible for:

- Fast vector indexing.
- Similarity search.
- Nearest-neighbor retrieval.
- Supporting the RAG pipeline.

FAISS does **not** store the complete vehicle information.

Instead, it stores vector embeddings, while MongoDB stores the actual documents.

---

# MongoDB + FAISS Integration

```text
Vehicle Information

↓

Embedding Model

↓

Vector

↓

FAISS Index

↓

Vector ID

↓

MongoDB Mapping

↓

Vehicle Document
```

This architecture allows the RAG system to retrieve semantically similar vehicles efficiently.

---

# Future Integration

The Database layer is designed to support:

- RAG Retrieval.
- Conversation Memory.
- Recommendation Systems.
- Similar Vehicle Search.
- Long-Term User Memory.
- Vehicle Knowledge Base.
- AI Analytics.

---

# Documentation Strategy

Only files containing database logic are documented in detail.

Training datasets are not documented because they are used only during model training and are not part of the runtime architecture.


# mongodb.py

**File Location**

```text
data/
└── database/
    └── mongodb/
        └── mongodb.py
```

---

# Purpose

`mongodb.py` is the central MongoDB connection manager for the entire project.

It is responsible for creating, maintaining, and sharing a single MongoDB connection across all database collections.

Instead of allowing every collection to create its own database connection, all modules obtain their collections through this manager.

The class follows the **Singleton Pattern** to ensure that only one MongoDB connection exists during the application's lifetime.

---

# Responsibilities

The MongoDB Manager is responsible for:

- Loading database configuration.
- Reading environment variables.
- Establishing MongoDB connections.
- Managing database lifecycle.
- Providing database instances.
- Providing collection instances.
- Verifying database connectivity.
- Closing connections safely.

---

# Architecture

```text
Backend

↓

MongoDBManager

↓

MongoClient

↓

Database

↓

Collections

├── sessions
├── history
├── vehicles
├── comparisons
└── vector_index
```

---

# Dependencies

## Project

None

---

## Third-Party Libraries

```python
pymongo

python-dotenv
```

Used for:

- MongoDB connection.
- Database operations.
- Loading environment variables.

---

## Python Standard Library

```python
os

typing.Optional
```

---

# Environment Variables

The connection manager depends on the following variables.

| Variable         | Purpose                   |
| ---------------- | ------------------------- |
| MONGODB_URI      | MongoDB connection string |
| MONGODB_DATABASE | Database name             |

Both variables are loaded automatically using

```python
load_dotenv()
```

---

# Main Class

## MongoDBManager

This class is responsible for managing the MongoDB connection.

It implements the **Singleton Pattern**, ensuring that all database operations share the same MongoDB client.

---

# Singleton Pattern

```text
Application

↓

MongoDBManager()

↓

Existing Instance ?

↓

YES → Return Existing Connection

NO

↓

Create MongoClient

↓

Store Instance

↓

Return Instance
```

This prevents unnecessary database connections and improves performance.

---

# Main Methods

## connect()

```python
connect()
```

### Purpose

Establish a connection to MongoDB.

### Responsibilities

- Read environment variables.
- Create MongoClient.
- Verify the connection using `ping`.
- Select the active database.
- Store the database instance.

### Raises

```python
ValueError
```

If required environment variables are missing.

```python
ConnectionError
```

If MongoDB cannot be reached.

---

## disconnect()

```python
disconnect()
```

### Purpose

Close the active MongoDB connection.

### Responsibilities

- Close MongoClient.
- Release database resources.
- Reset internal references.

---

## get_database()

```python
get_database()
```

### Purpose

Return the active database instance.

If no active connection exists, a connection is established automatically.

---

## get_collection()

```python
get_collection(
    collection_name
)
```

### Purpose

Return a MongoDB collection.

Every collection class inside the project retrieves its collection through this method.

Example

```text
sessions

history

vehicles

comparisons

vector_index
```

---

## collection_exists()

```python
collection_exists(
    collection_name
)
```

### Purpose

Verify whether a collection exists inside the active database.

### Returns

```python
bool
```

---

## health_check()

```python
health_check()
```

### Purpose

Verify that MongoDB is reachable.

Internally executes

```python
ping
```

against the database server.

### Returns

```python
True
```

Database is reachable.

```python
False
```

Database is unavailable.

---

# Used By

This manager is used by every MongoDB collection.

```text
SessionCollection

HistoryCollection

VehicleCollection

ComparisonCollection

VectorIndexCollection
```

None of these classes create their own MongoDB connection.

---

# Connection Flow

```text
Backend

↓

MongoDBManager

↓

Read .env

↓

MongoClient

↓

Ping Database

↓

Database

↓

Collection

↓

CRUD Operations
```

---

# Error Handling

The manager validates:

- Missing environment variables.
- Connection failures.
- Database availability.

Connection errors are converted into project-specific exceptions before being propagated.

---

# Future Improvements

The connection manager can later support:

- Connection Pooling.
- Automatic Reconnection.
- Database Authentication.
- SSL Connections.
- Replica Sets.
- MongoDB Atlas.
- Logging.
- Performance Monitoring.
- Transaction Support.

---

# Summary

`mongodb.py` is the foundation of the Database layer.

It centralizes MongoDB connectivity, manages the application's single database connection using the Singleton Pattern, provides access to all collections, validates database availability, and serves as the entry point for every MongoDB operation performed by the Smart Vehicle Identifier system.


# session.py

**File Location**

```text
data/
└── database/
    └── mongodb/
        └── session.py
```

---

# Purpose

`session.py` manages all MongoDB operations related to user sessions.

Each user interaction with the Smart Vehicle Identifier system belongs to a session. This module is responsible for creating, updating, retrieving, and deleting session documents stored inside the **sessions** collection.

It provides a clean CRUD interface without exposing MongoDB implementation details to the Backend.

---

# Responsibilities

The Session Collection is responsible for:

- Creating new user sessions.
- Retrieving sessions.
- Updating session information.
- Deleting sessions.
- Counting stored sessions.
- Providing access to the `sessions` MongoDB collection.

---

# Architecture

```text
Frontend

↓

Backend

↓

SessionCollection

↓

MongoDBManager

↓

sessions Collection
```

---

# Collection Name

```text
sessions
```

---

# Dependencies

## Project Imports

```python
from .mongodb import MongoDBManager
```

Provides access to the shared MongoDB connection.

---

## Third-Party Libraries

```python
pymongo

bson.ObjectId
```

Used for:

- CRUD operations.
- MongoDB document lookup.

---

## Python Standard Library

```python
typing.Any
```

---

# Main Class

## SessionCollection

Represents the **sessions** collection inside MongoDB.

Instead of working directly with MongoDB, the Backend interacts with this class.

---

# Initialization

```python
SessionCollection()
```

During initialization:

```
MongoDBManager

↓

get_collection("sessions")

↓

MongoDB Collection
```

The collection object is stored internally for future operations.

---

# Main Methods

## insert()

```python
insert(session_data)
```

### Purpose

Insert a new session document.

### Parameters

```python
dict[str, Any]
```

### Returns

```python
str
```

MongoDB inserted document ID.

---

## find_by_id()

```python
find_by_id(session_id)
```

### Purpose

Retrieve a session document using its MongoDB ObjectId.

### Parameters

```python
session_id: str
```

### Returns

```python
dict | None
```

Returns the session document if found; otherwise returns `None`.

---

## find_all()

```python
find_all()
```

### Purpose

Retrieve every stored session.

### Returns

```python
list[dict]
```

---

## update()

```python
update(
    session_id,
    updated_data
)
```

### Purpose

Update an existing session document.

### Parameters

- Session ID
- Updated fields

### Returns

```python
bool
```

Returns **True** if the document was modified successfully.

---

## delete()

```python
delete(session_id)
```

### Purpose

Delete a session document.

### Returns

```python
bool
```

Returns **True** if the session was deleted.

---

## count()

```python
count()
```

### Purpose

Return the total number of stored sessions.

### Returns

```python
int
```

---

# CRUD Workflow

```text
Backend

↓

SessionCollection

↓

MongoDBManager

↓

sessions Collection

↓

MongoDB

↓

Result
```

---

# Typical Session Lifecycle

```text
User Starts Chat

↓

Create Session

↓

Save Session

↓

User Continues Conversation

↓

Update Session

↓

Retrieve Session

↓

End Session

↓

Delete (Optional)
```

---

# Used By

This module is expected to be used by:

- Chat System
- Conversation Manager
- History Module
- Backend Controllers
- Memory System

Every user interaction begins with a session.

---

# Future Improvements

Possible future extensions include:

- Session expiration.
- Last activity timestamp.
- User authentication.
- Multiple active sessions.
- Session analytics.
- Automatic cleanup of inactive sessions.
- Session metadata.
- Device information.

---

# Summary

`session.py` provides a dedicated interface for managing user sessions stored in MongoDB.

It encapsulates all CRUD operations related to the **sessions** collection, allowing the Backend to manage conversation sessions through a clean and reusable abstraction while relying on the shared `MongoDBManager` connection.


# history.py

**File Location**

```text
data/
└── database/
    └── mongodb/
        └── history.py
```

---

# Purpose

`history.py` manages all MongoDB operations related to conversation history.

Each conversation between the user and the AI assistant is stored as a history document linked to a specific session.

This module provides a dedicated interface for storing, retrieving, updating, and deleting chat history without exposing MongoDB operations to the Backend.

---

# Responsibilities

The History Collection is responsible for:

- Storing conversation messages.
- Retrieving chat history.
- Retrieving history for a specific session.
- Updating chat records.
- Deleting individual history documents.
- Deleting an entire session history.
- Counting stored history records.

---

# Architecture

```text
Frontend

↓

Backend

↓

HistoryCollection

↓

MongoDBManager

↓

history Collection
```

---

# Collection Name

```text
history
```

---

# Dependencies

## Project Imports

```python
from .mongodb import MongoDBManager
```

Provides access to the shared MongoDB connection.

---

## Third-Party Libraries

```python
pymongo

bson.ObjectId
```

Used for MongoDB CRUD operations and ObjectId conversion.

---

## Python Standard Library

```python
typing.Any
```

---

# Main Class

## HistoryCollection

Represents the **history** collection inside MongoDB.

All conversation history operations are performed through this class.

---

# Initialization

```python
HistoryCollection()
```

Initialization workflow

```text
MongoDBManager

↓

get_collection("history")

↓

MongoDB Collection
```

---

# Main Methods

## insert()

```python
insert(history_data)
```

### Purpose

Insert a new chat history document.

### Parameters

```python
dict[str, Any]
```

### Returns

```python
str
```

MongoDB inserted document ID.

---

## find_by_id()

```python
find_by_id(history_id)
```

### Purpose

Retrieve a chat history document using its MongoDB ObjectId.

### Returns

```python
dict | None
```

---

## find_by_session()

```python
find_by_session(session_id)
```

### Purpose

Retrieve every chat message belonging to a specific session.

### Parameters

```python
session_id
```

### Returns

```python
list[dict]
```

This is the primary method used to reconstruct previous conversations.

---

## find_all()

```python
find_all()
```

### Purpose

Retrieve all stored conversation history.

### Returns

```python
list[dict]
```

---

## update()

```python
update(
    history_id,
    updated_data
)
```

### Purpose

Update an existing history document.

### Returns

```python
bool
```

Returns **True** if the document was modified successfully.

---

## delete()

```python
delete(history_id)
```

### Purpose

Delete a single history document.

### Returns

```python
bool
```

---

## delete_session_history()

```python
delete_session_history(
    session_id
)
```

### Purpose

Delete all chat messages belonging to a specific session.

### Returns

```python
int
```

Returns the number of deleted documents.

---

## count()

```python
count()
```

### Purpose

Return the total number of stored history documents.

### Returns

```python
int
```

---

# Conversation Workflow

```text
User Sends Message

↓

Backend

↓

HistoryCollection

↓

Insert Message

↓

MongoDB

↓

Future Retrieval

↓

Conversation Reconstruction
```

---

# Relationship with Sessions

Every history document belongs to a session.

```text
Session

↓

History Messages

↓

AI Conversation

↓

User Continues Chat
```

This relationship allows the system to restore previous conversations using the session identifier.

---

# Used By

This module is expected to be used by:

- Chat Controller
- Conversation Manager
- Memory System
- RAG Pipeline
- AI Assistant

Whenever previous conversation context is required.

---

# Future Improvements

Possible future enhancements include:

- Conversation summarization.
- Message timestamps.
- Message ordering.
- Soft delete.
- Conversation search.
- Conversation export.
- Conversation analytics.
- Token usage tracking.

---

# Summary

`history.py` provides a dedicated MongoDB interface for managing conversation history.

It encapsulates all CRUD operations related to the **history** collection, allowing the Backend and Memory System to efficiently store, retrieve, update, and remove chat messages while maintaining the relationship between conversations and user sessions.


# vehicle.py

**File Location**

```text
data/
└── database/
    └── mongodb/
        └── vehicle.py
```

---

# Purpose

`vehicle.py` manages all MongoDB operations related to vehicle documents.

Each identified vehicle can be stored inside the **vehicles** collection, allowing the system to retrieve vehicle information without repeating AI inference or external searches.

This collection serves as the primary knowledge repository for vehicle information generated by the AI pipeline.

---

# Responsibilities

The Vehicle Collection is responsible for:

- Storing vehicle information.
- Retrieving stored vehicles.
- Updating vehicle data.
- Deleting vehicle records.
- Counting stored vehicles.
- Providing CRUD operations for the `vehicles` collection.

---

# Architecture

```text
Classification Model

↓

Groq Vision

↓

Web Scraping (Optional)

↓

Backend

↓

VehicleCollection

↓

vehicles Collection
```

---

# Collection Name

```text
vehicles
```

---

# Dependencies

## Project Imports

```python
from .mongodb import MongoDBManager
```

Provides the shared MongoDB connection.

---

## Third-Party Libraries

```python
pymongo

bson.ObjectId
```

Used for CRUD operations and MongoDB ObjectId handling.

---

## Python Standard Library

```python
typing.Any
```

---

# Main Class

## VehicleCollection

Represents the **vehicles** collection inside MongoDB.

The Backend interacts with this class instead of communicating directly with MongoDB.

---

# Initialization

```python
VehicleCollection()
```

Initialization Flow

```text
MongoDBManager

↓

get_collection("vehicles")

↓

MongoDB Collection
```

---

# Main Methods

## insert()

```python
insert(vehicle_data)
```

### Purpose

Insert a new vehicle document.

### Parameters

```python
dict[str, Any]
```

### Returns

```python
str
```

MongoDB inserted document ID.

---

## find_by_id()

```python
find_by_id(vehicle_id)
```

### Purpose

Retrieve a vehicle document using its MongoDB ObjectId.

### Returns

```python
dict | None
```

Returns the vehicle document if found.

---

## find_all()

```python
find_all()
```

### Purpose

Retrieve all stored vehicle documents.

### Returns

```python
list[dict]
```

---

## update()

```python
update(
    vehicle_id,
    updated_data
)
```

### Purpose

Update an existing vehicle document.

### Returns

```python
bool
```

Returns **True** if the document was updated successfully.

---

## delete()

```python
delete(vehicle_id)
```

### Purpose

Delete a vehicle document.

### Returns

```python
bool
```

Returns **True** if the document was deleted successfully.

---

## count()

```python
count()
```

### Purpose

Return the total number of stored vehicle documents.

### Returns

```python
int
```

---

# Vehicle Storage Workflow

```text
Vehicle Image

↓

Classification Model

↓

Vehicle Name

↓

Groq Vision

↓

Vehicle Details

↓

Backend

↓

VehicleCollection

↓

MongoDB
```

---

# Relationship with Other Modules

The stored vehicle information can later be used by:

- Web Scraping Cache.
- RAG Pipeline.
- Vehicle Comparison.
- Conversation Memory.
- Recommendation System.

Instead of generating the same information multiple times, the system can retrieve existing vehicle records from the database.

---

# Used By

This collection is expected to be used by:

- Vehicle Service
- RAG Manager
- Web Scraping Service
- Comparison Service
- AI Assistant

Whenever vehicle information needs to be stored or retrieved.

---

# Future Improvements

Possible future enhancements include:

- Search by vehicle name.
- Search by manufacturer.
- Search by model year.
- Vehicle filtering.
- Similar vehicle lookup.
- Vehicle popularity statistics.
- Cached AI responses.
- Automatic duplicate detection.

---

# Summary

`vehicle.py` provides a dedicated MongoDB interface for managing vehicle information.

It encapsulates all CRUD operations related to the **vehicles** collection, allowing the Backend to persist vehicle data generated by the AI pipeline and reuse it across future analyses, comparisons, and RAG retrieval without repeating expensive AI inference.


# comparison.py

**File Location**

```text
data/
└── database/
    └── mongodb/
        └── comparison.py
```

---

# Purpose

`comparison.py` manages all MongoDB operations related to vehicle comparison documents.

Whenever the user compares two or more vehicles, the comparison result can be stored inside the **comparisons** collection for future retrieval.

This allows the system to preserve comparison history instead of generating it repeatedly.

---

# Responsibilities

The Comparison Collection is responsible for:

- Storing comparison results.
- Retrieving comparison documents.
- Retrieving comparisons for a specific session.
- Updating comparison records.
- Deleting stored comparisons.
- Counting comparison documents.

---

# Architecture

```text
Frontend

↓

Backend

↓

Comparison Service

↓

ComparisonCollection

↓

comparisons Collection

↓

MongoDB
```

---

# Collection Name

```text
comparisons
```

---

# Dependencies

## Project Imports

```python
from .mongodb import MongoDBManager
```

Provides the shared MongoDB connection.

---

## Third-Party Libraries

```python
pymongo

bson.ObjectId
```

Used for MongoDB CRUD operations and ObjectId conversion.

---

## Python Standard Library

```python
typing.Any
```

---

# Main Class

## ComparisonCollection

Represents the **comparisons** collection inside MongoDB.

The Backend communicates with this class instead of interacting directly with MongoDB.

---

# Initialization

```python
ComparisonCollection()
```

Initialization Flow

```text
MongoDBManager

↓

get_collection("comparisons")

↓

MongoDB Collection
```

---

# Main Methods

## insert()

```python
insert(comparison_data)
```

### Purpose

Insert a new comparison document.

### Parameters

```python
dict[str, Any]
```

### Returns

```python
str
```

MongoDB inserted document ID.

---

## find_by_id()

```python
find_by_id(comparison_id)
```

### Purpose

Retrieve a comparison document using its MongoDB ObjectId.

### Returns

```python
dict | None
```

---

## find_by_session()

```python
find_by_session(session_id)
```

### Purpose

Retrieve every comparison performed during a specific session.

### Returns

```python
list[dict]
```

This method is useful for rebuilding the user's comparison history.

---

## find_all()

```python
find_all()
```

### Purpose

Retrieve all stored comparison documents.

### Returns

```python
list[dict]
```

---

## update()

```python
update(
    comparison_id,
    updated_data
)
```

### Purpose

Update an existing comparison document.

### Returns

```python
bool
```

Returns **True** if the comparison was successfully updated.

---

## delete()

```python
delete(comparison_id)
```

### Purpose

Delete a comparison document.

### Returns

```python
bool
```

Returns **True** if the comparison was successfully removed.

---

## count()

```python
count()
```

### Purpose

Return the total number of stored comparison documents.

### Returns

```python
int
```

---

# Comparison Workflow

```text
User Selects Vehicles

↓

Backend

↓

Comparison Service

↓

Generate Comparison

↓

ComparisonCollection

↓

MongoDB
```

---

# Relationship with Other Modules

The comparison records may later be used by:

- Comparison Service.
- Conversation History.
- Recommendation Engine.
- Analytics Dashboard.
- User Memory.
- RAG System.

Storing comparison results avoids unnecessary regeneration of identical comparisons.

---

# Used By

This collection is expected to be used by:

- Comparison Controller.
- Compare Service.
- History Service.
- Memory System.
- AI Assistant.

---

# Future Improvements

Possible future enhancements include:

- Comparison search.
- Comparison statistics.
- Favorite comparisons.
- Comparison templates.
- Vehicle recommendation based on previous comparisons.
- AI-generated comparison summaries.

---

# Summary

`comparison.py` provides a dedicated MongoDB interface for managing vehicle comparison records.

It encapsulates all CRUD operations related to the **comparisons** collection, allowing the Backend to store, retrieve, update, and reuse comparison results across different sessions while maintaining a clean separation between business logic and database operations.


# vector_index.py

**File Location**

```text
data/
└── database/
    └── mongodb/
        └── vector_index.py
```

---

# Purpose

`vector_index.py` manages the relationship between FAISS vectors and MongoDB vehicle documents.

FAISS stores only numerical vector embeddings and cannot store complete vehicle information. Therefore, this collection acts as a mapping layer that connects each FAISS vector ID with its corresponding MongoDB vehicle document.

This mapping enables the system to retrieve complete vehicle information after performing a similarity search.

---

# Responsibilities

The Vector Index Collection is responsible for:

- Mapping FAISS vector IDs to vehicle documents.
- Retrieving mappings by vector ID.
- Retrieving mappings by vehicle ID.
- Updating mappings.
- Deleting mappings.
- Counting stored mappings.

---

# Architecture

```text
Vehicle Information

↓

Embedding Model

↓

Vector

↓

FAISS

↓

Vector ID

↓

VectorIndexCollection

↓

MongoDB

↓

Vehicle Document
```

---

# Collection Name

```text
vector_index
```

---

# Dependencies

## Project Imports

```python
from .mongodb import MongoDBManager
```

Provides access to the shared MongoDB connection.

---

## Third-Party Libraries

```python
pymongo

bson.ObjectId
```

Used for MongoDB CRUD operations and ObjectId conversion.

---

## Python Standard Library

```python
typing.Any
```

---

# Main Class

## VectorIndexCollection

Represents the **vector_index** collection inside MongoDB.

Instead of storing embeddings, this collection stores the relationship between a FAISS vector and the original MongoDB document.

---

# Initialization

```python
VectorIndexCollection()
```

Initialization Flow

```text
MongoDBManager

↓

get_collection("vector_index")

↓

MongoDB Collection
```

---

# Main Methods

## insert()

```python
insert(document)
```

### Purpose

Insert a new vector mapping document.

### Parameters

```python
dict[str, Any]
```

Example

```json
{
    "vector_id": 152,
    "vehicle_id": "687d91..."
}
```

### Returns

```python
str
```

Inserted MongoDB document ID.

---

## find_by_id()

```python
find_by_id(document_id)
```

### Purpose

Retrieve a mapping document using its MongoDB ObjectId.

### Returns

```python
dict | None
```

---

## find_by_vector_id()

```python
find_by_vector_id(vector_id)
```

### Purpose

Retrieve the MongoDB document associated with a FAISS vector.

### Returns

```python
dict | None
```

---

## find_by_vehicle_id()

```python
find_by_vehicle_id(vehicle_id)
```

### Purpose

Retrieve the vector mapping associated with a vehicle document.

### Returns

```python
dict | None
```

---

## update()

```python
update(
    document_id,
    data
)
```

### Purpose

Update an existing vector mapping.

### Returns

```python
bool
```

Returns **True** if the mapping was successfully updated.

---

## delete()

```python
delete(document_id)
```

### Purpose

Delete a vector mapping.

### Returns

```python
bool
```

Returns **True** if the mapping was successfully deleted.

---

## count()

```python
count()
```

### Purpose

Return the total number of vector mappings stored in MongoDB.

### Returns

```python
int
```

---

# RAG Retrieval Workflow

```text
User Query

↓

Embedding Model

↓

Query Vector

↓

FAISS Search

↓

Vector IDs

↓

VectorIndexCollection

↓

Vehicle IDs

↓

VehicleCollection

↓

Vehicle Documents

↓

LLM Context
```

---

# Relationship with Other Modules

This collection connects:

- FAISS Vector Index
- Vehicle Collection
- Embedding Pipeline
- RAG Retrieval System

Without this mapping layer, FAISS would only return vector indices, making it impossible to retrieve the corresponding vehicle information stored in MongoDB.

---

# Used By

This collection is expected to be used by:

- FAISS Manager.
- Vector Store.
- RAG Retrieval Pipeline.
- Embedding Service.
- Recommendation Engine.

---

# Future Improvements

Possible future enhancements include:

- Multiple embeddings per vehicle.
- Embedding version control.
- Automatic re-indexing.
- Metadata filtering.
- Hybrid search support.
- Batch mapping operations.
- Embedding statistics.

---

# Summary

`vector_index.py` acts as the bridge between **FAISS** and **MongoDB**.

It stores the mapping between vector IDs and vehicle documents, enabling the RAG pipeline to retrieve complete vehicle information after semantic similarity search. This separation keeps FAISS lightweight while allowing MongoDB to store the full structured data required by the application.


# faiss_manager.py

**File Location**

```text
data/
└── database/
    └── faiss/
        └── faiss_manager.py
```

---

# Purpose

`faiss_manager.py` is the low-level vector index manager responsible for creating, maintaining, saving, loading, and searching FAISS indexes.

It provides a unified interface for vector operations while supporting two execution modes:

- Native **FAISS** when available.
- NumPy fallback implementation when FAISS is unavailable.

This design allows the application to work in environments where the FAISS library cannot be installed.

---

# Responsibilities

The FAISS Manager is responsible for:

- Creating vector indexes.
- Managing embedding vectors.
- Adding new vectors.
- Performing similarity search.
- Saving indexes to disk.
- Loading existing indexes.
- Counting indexed vectors.
- Providing a NumPy fallback when FAISS is unavailable.

---

# Architecture

```text
Embedding Model

↓

Vector

↓

FAISSManager

↓

FAISS Index

↓

Similarity Search

↓

Vector IDs

↓

MongoDB Mapping

↓

Vehicle Document
```

---

# Dependencies

## Third-Party Libraries

```python
faiss

numpy
```

If FAISS is unavailable, the manager automatically switches to the NumPy implementation.

---

## Python Standard Library

```python
pathlib.Path
```

---

# Main Classes

## FAISSManager

The primary class responsible for managing the vector index.

It hides all low-level FAISS operations from the rest of the project.

---

## _NumpyIndex

Internal fallback implementation.

This class is automatically used when the FAISS library is not installed.

It mimics the most important FAISS operations:

- Add vectors.
- Search vectors.
- Count vectors.

This class is **not intended to be used directly** outside `FAISSManager`.

---

# Default Configuration

| Parameter        | Default Value |
| ---------------- | ------------- |
| Vector Dimension | 768           |
| Search Metric    | L2 Distance   |
| Default Top K    | 5             |

---

# Main Methods

## create_index()

```python
create_index()
```

### Purpose

Create a new vector index.

Behavior

```
FAISS Installed

↓

Create IndexFlatL2

OR

↓

Create _NumpyIndex
```

---

## add_vectors()

```python
add_vectors(vectors)
```

### Purpose

Insert one or more embedding vectors into the current index.

### Validation

- Correct dimensions.
- Float32 conversion.
- Two-dimensional array.

---

## search()

```python
search(
    query_vector,
    top_k=5
)
```

### Purpose

Perform semantic similarity search.

### Parameters

| Parameter    | Description                 |
| ------------ | --------------------------- |
| query_vector | Query embedding             |
| top_k        | Number of nearest neighbors |

### Returns

```python
(scores, indices)
```

Where

```
scores

↓

Similarity Distance

indices

↓

Matching Vector IDs
```

---

## count()

```python
count()
```

### Purpose

Return the total number of indexed vectors.

### Returns

```python
int
```

---

## save_index()

```python
save_index(index_path)
```

### Purpose

Persist the current vector index to disk.

Behavior

```
FAISS

↓

vehicle.index

OR

NumPy

↓

vehicle.npy
```

---

## load_index()

```python
load_index(index_path)
```

### Purpose

Load a previously saved vector index.

If the index file exists, it is loaded into memory.

Otherwise, the manager starts with an empty index.

### Returns

```python
bool
```

---

# Validation

The manager validates:

- Vector dimensions.
- Query dimensions.
- Positive Top-K values.
- Empty indexes.
- Missing files.

Invalid inputs raise descriptive exceptions before reaching FAISS.

---

# Similarity Search Workflow

```text
Query

↓

Embedding Model

↓

768-D Vector

↓

FAISSManager

↓

Nearest Neighbors

↓

Vector IDs

↓

MongoDB Mapping

↓

Vehicle Documents
```

---

# Relationship with Other Modules

`FAISSManager` works together with:

- `vector_store.py`
- `vector_index.py`
- `VehicleCollection`
- Embedding Model
- RAG Retrieval Pipeline

It never stores vehicle information directly.

Instead, it only manages numerical vector embeddings.

---

# Used By

The manager is expected to be used by:

- Vector Store
- RAG System
- Semantic Search
- Recommendation Engine
- Similar Vehicle Search

---

# Future Improvements

Possible future enhancements include:

- IVF Indexes.
- HNSW Indexes.
- GPU Acceleration.
- Cosine Similarity.
- Batch Search.
- Metadata Filtering.
- Incremental Index Updates.
- Distributed Indexes.

---

# Summary

`faiss_manager.py` is the core vector indexing engine of the Smart Vehicle Identifier project.

It manages the complete lifecycle of embedding vectors, including index creation, vector insertion, similarity search, persistence, and loading. By supporting both native FAISS and a NumPy fallback, it ensures reliable semantic search across different execution environments while remaining fully integrated with the MongoDB mapping layer.


# vector_store.py

**File Location**

```text
data/
└── database/
    └── faiss/
        └── vector_store.py
```

---

# Purpose

`vector_store.py` provides a high-level abstraction over the FAISS vector database.

Instead of interacting directly with `FAISSManager`, the Backend communicates with `VectorStore`, which simplifies vector operations such as loading indexes, inserting embeddings, searching similar vectors, saving indexes, and resetting the vector database.

This class acts as the primary interface between the application and the FAISS indexing engine.

---

# Responsibilities

The Vector Store is responsible for:

- Initializing the vector database.
- Loading existing indexes automatically.
- Adding embedding vectors.
- Searching similar vectors.
- Saving indexes.
- Resetting indexes.
- Returning vector statistics.
- Providing a simplified interface for semantic search.

---

# Architecture

```text
Backend

↓

VectorStore

↓

FAISSManager

↓

FAISS Index

↓

Similarity Search

↓

Vector IDs

↓

VectorIndexCollection

↓

Vehicle Documents
```

---

# Dependencies

## Project Imports

```python
from .faiss_manager import FAISSManager
```

---

## Third-Party Libraries

```python
numpy
```

---

## Python Standard Library

```python
pathlib.Path
```

---

# Main Class

## VectorStore

The high-level interface used by the Backend for all vector database operations.

Unlike `FAISSManager`, this class hides implementation details and exposes only the operations required by the application.

---

# Default Configuration

| Parameter          | Default Value |
| ------------------ | ------------- |
| Vector Dimension   | 768           |
| Default Index File | vehicle.index |

When no custom path is provided, the index is stored beside this module as:

```text
vehicle.index
```

If FAISS is unavailable, a NumPy fallback file (`vehicle.npy`) is used automatically.

---

# Initialization

```python
VectorStore(
    dimension=768,
    index_path=None
)
```

Initialization workflow

```text
Create FAISSManager

↓

Load Existing Index

↓

Ready for Search
```

---

# Main Methods

## _load_existing()

```python
_load_existing()
```

### Purpose

Automatically load an existing vector index during initialization.

If no index exists, an empty vector database is created.

---

## reset()

```python
reset()
```

### Purpose

Reset the vector database.

Responsibilities

- Create a new empty index.
- Remove existing index files.
- Remove NumPy fallback files.

Used when rebuilding the knowledge base.

---

## add()

```python
add(vectors)
```

### Purpose

Insert one or more embedding vectors into the vector database.

Internally delegates the operation to:

```python
FAISSManager.add_vectors()
```

---

## search()

```python
search(
    query_vector,
    top_k=5
)
```

### Purpose

Search for the nearest embedding vectors.

### Returns

```python
(scores, indices)
```

Where

- **scores** → similarity distances.
- **indices** → matching vector IDs.

Internally delegates the operation to:

```python
FAISSManager.search()
```

---

## save()

```python
save()
```

### Purpose

Persist the current vector index to disk.

Internally calls

```python
FAISSManager.save_index()
```

---

## count()

```python
count()
```

### Purpose

Return the number of stored vectors.

### Returns

```python
int
```

---

## get_dimension()

```python
get_dimension()
```

### Purpose

Return the embedding dimension used by the vector database.

### Returns

```python
int
```

Default value

```text
768
```

---

# Semantic Search Workflow

```text
Vehicle Information

↓

Embedding Model

↓

768-D Vector

↓

VectorStore

↓

FAISSManager

↓

Similarity Search

↓

Vector IDs

↓

VectorIndexCollection

↓

MongoDB

↓

Vehicle Information
```

---

# Relationship with Other Modules

`VectorStore` is the main entry point for semantic retrieval.

It communicates with:

- FAISSManager
- VectorIndexCollection
- VehicleCollection
- Embedding Pipeline
- RAG System

Unlike `FAISSManager`, it is intended to be imported directly by the Backend.

---

# Used By

The Vector Store is expected to be used by:

- RAG Pipeline
- Semantic Search
- Recommendation System
- Similar Vehicle Search
- Backend Retrieval Service

---

# Future Improvements

Possible future enhancements include:

- Batch vector insertion.
- Batch semantic search.
- Automatic index optimization.
- Metadata filtering.
- Hybrid retrieval.
- Distributed vector storage.
- Cloud-based vector databases.
- Incremental indexing.

---

# Summary

`vector_store.py` is the high-level vector database interface used throughout the Smart Vehicle Identifier project.

It simplifies interaction with FAISS by providing a clean abstraction for loading indexes, inserting vectors, performing similarity searches, saving indexes, and resetting the vector database. This separation allows the Backend and RAG system to work with semantic retrieval without dealing with low-level FAISS implementation details.
