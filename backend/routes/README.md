
# Backend Routes Module

# 🌐 API Gateway Module

The `routes` module defines all API endpoints exposed by the backend.

It acts as the communication bridge between the Frontend and the Backend Controllers.

Every request from the frontend must pass through this module before reaching any business logic.

---

# Module Overview

The Routes module is responsible for:

- Registering API endpoints.
- Mapping URLs to Controllers.
- Organizing REST APIs.
- Separating application features into independent routes.

Routes should remain as lightweight as possible.

They should never contain any business logic.

---

# Architecture Position

```
           Streamlit Frontend
                    │
                    ▼
              HTTP Request
                    │
                    ▼
          FastAPI Router (Routes)
                    │
                    ▼
              Controller Layer
                    │
                    ▼
              Service Layer
                    │
                    ▼
        RAG / Memory / Database
```

---

# Responsibilities

The Routes module is responsible for:

- Defining API endpoints.
- Receiving HTTP requests.
- Passing requests to Controllers.
- Returning Controller responses.

The Routes module is NOT responsible for:

- AI inference.
- Vehicle analysis.
- Database operations.
- Prompt generation.
- Web scraping.
- Business logic.

---

# Folder Structure

```
routes/
│
├── image_routes.py
├── chat_routes.py
├── compare_routes.py
└── history_routes.py
```

---

# API Design

Base URL

```
/api/v1/
```

Every endpoint should be grouped by feature.

Example

```
/api/v1/chat
/api/v1/image
/api/v1/compare
/api/v1/history
```

---

# File Specifications

---

# image_routes.py

## Purpose

Defines all endpoints related to vehicle image processing.

---

## Main Router

```python
APIRouter
```

---

## Endpoints

### POST

```
/image/upload
```

Upload vehicle image.

---

### POST

```
/image/analyze
```

Analyze uploaded image.

---

### DELETE

```
/image/delete
```

Delete temporary uploaded image.

---

## Controller

```
ImageController
```

---

# chat_routes.py

## Purpose

Defines chat-related endpoints.

---

## Main Router

```python
APIRouter
```

---

## Endpoints

### POST

```
/chat
```

Generate answer.

---

### POST

```
/chat/new-session
```

Create new chat session.

---

### GET

```
/chat/session/{session_id}
```

Retrieve session.

---

## Controller

```
ChatController
```

---

# compare_routes.py

## Purpose

Defines vehicle comparison endpoints.

---

## Main Router

```python
APIRouter
```

---

## Endpoints

### POST

```
/compare
```

Compare two vehicles.

---

### GET

```
/compare/history
```

Retrieve previous comparisons.

---

### DELETE

```
/compare/{comparison_id}
```

Delete comparison.

---

## Controller

```
CompareController
```

---

# history_routes.py

## Purpose

Defines user history endpoints.

---

## Main Router

```python
APIRouter
```

---

## Endpoints

### GET

```
/history
```

Retrieve user history.

---

### DELETE

```
/history
```

Clear all history.

---

### DELETE

```
/history/{history_id}
```

Delete one history record.

---

## Controller

```
HistoryController
```

---

# Route Registration

Every route file should expose one router object.

Example

```python
router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)
```

The application entry point (`backend/app.py`) is responsible for registering all routers.

---

# Request Flow

```
Frontend

↓

HTTP Request

↓

FastAPI Route

↓

Controller

↓

Service

↓

RAG / Memory / Database

↓

Controller

↓

HTTP Response

↓

Frontend
```

---

# Response Format

Every endpoint should return a unified response.

Success

```json
{
    "success": true,
    "message": "Success",
    "data": {}
}
```

Error

```json
{
    "success": false,
    "message": "Validation Error",
    "error": {}
}
```

---

# Naming Convention

Files

```
image_routes.py

chat_routes.py

compare_routes.py

history_routes.py
```

Routers

```
image_router

chat_router

compare_router

history_router
```

Endpoint Names

```
upload_image

analyze_image

chat

compare

get_history
```

---

# Development Rules

Every route must follow these rules.

✅ One router per file.

✅ One feature per router.

✅ Routes must call Controllers only.

✅ No Business Logic.

✅ No Database Access.

✅ No AI Models.

✅ No Web Scraping.

✅ Return HTTP responses only.

---

# Future Extensions

Possible future route modules

```
authentication_routes.py

admin_routes.py

feedback_routes.py

analytics_routes.py

health_routes.py
```

Every new router should follow the same architecture and naming conventions.
