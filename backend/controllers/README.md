
# Backend Controllers

## Module Overview

The `controllers` module is the entry point of the backend.

Its responsibility is to receive HTTP requests from the frontend, validate incoming data, call the appropriate Service layer, and return standardized HTTP responses.

Controllers do **not** contain business logic.

---

# Architecture Position

```
Frontend (Streamlit)
        │
        ▼
 FastAPI Router
        │
        ▼
   Controller
        │
        ▼
    Service Layer
        │
        ▼
RAG / Database / AI Models
        │
        ▼
 JSON Response
```

---

# Responsibilities

Controllers are responsible for:

- Receiving HTTP requests.
- Parsing request data.
- Validating request parameters.
- Calling the correct Service.
- Returning JSON responses.
- Handling HTTP exceptions.

Controllers are NOT responsible for:

- AI inference.
- Vehicle classification.
- Prompt engineering.
- Web scraping.
- Database queries.
- FAISS retrieval.
- MongoDB operations.
- Business logic.

Those responsibilities belong to other backend modules.

---

# Folder Structure

```
controllers/
│
├── chat_controller.py
├── compare_controller.py
├── history_controller.py
└── image_controller.py
```

---

# File Specifications

---

# image_controller.py

## Purpose

Handles every request related to vehicle images.

This controller is the first backend component executed after the user uploads an image.

---

## Main Class

```python
class ImageController
```

---

## Responsibilities

- Receive uploaded images.
- Validate image format.
- Validate image size.
- Store image temporarily.
- Call VehicleService.
- Return vehicle information.
- Delete temporary files.

---

## Public Methods

### upload_image()

Receive uploaded image.

Input

- Image File

Output

- Image ID
- Upload Status

---

### analyze_image()

Starts the vehicle analysis workflow.

Workflow

```
Upload Image

↓

VehicleService

↓

Vehicle Classification

↓

Google Lens Search

↓

Return Vehicle Information
```

---

### delete_temp_image()

Remove temporary image after processing.

---

### build_response()

Generate standard JSON response.

---

## Dependencies

Uses

- VehicleService

Never communicates directly with

- MongoDB
- FAISS
- Qwen
- Playwright

---

# chat_controller.py

## Purpose

Handles all user chat requests.

Acts as the communication layer between the frontend and the RAG Pipeline.

---

## Main Class

```python
class ChatController
```

---

## Responsibilities

- Receive user question.
- Validate request.
- Manage Session ID.
- Call ChatService.
- Return generated response.

---

## Public Methods

### chat()

Main chat endpoint.

Input

- Session ID
- Question
- Image ID (Optional)

Output

- Generated Answer

---

### validate_request()

Validate

- Session
- Question
- Image ID

---

### build_response()

Generate standard JSON response.

---

### handle_exception()

Handle unexpected errors.

---

## Dependencies

Uses

- ChatService

Never communicates directly with

- MongoDB
- FAISS
- Qwen

---

# compare_controller.py

## Purpose

Handles vehicle comparison requests.

---

## Main Class

```python
class CompareController
```

---

## Responsibilities

- Receive two vehicle identifiers.
- Validate comparison request.
- Call CompareService.
- Return comparison result.

---

## Public Methods

### compare()

Compare two vehicles.

---

### validate_request()

Validate both vehicle IDs.

---

### build_response()

Generate comparison JSON.

---

### handle_exception()

Handle comparison errors.

---

## Dependencies

Uses

- CompareService

---

# history_controller.py

## Purpose

Handles user history operations.

---

## Main Class

```python
class HistoryController
```

---

## Responsibilities

- Retrieve history.
- Delete one record.
- Clear history.
- Return history response.

---

## Public Methods

### get_history()

Return conversation history.

---

### delete_history_item()

Delete one history record.

---

### clear_history()

Delete all history.

---

### build_response()

Generate history JSON.

---

## Dependencies

Uses

- HistoryService

---

# Response Standard

Every controller must return the same response structure.

Success

```json
{
    "success": true,
    "message": "Operation completed successfully.",
    "data": {},
    "timestamp": ""
}
```

Error

```json
{
    "success": false,
    "message": "Validation Error",
    "error": "",
    "timestamp": ""
}
```

---

# Naming Convention

## Files

```
image_controller.py
chat_controller.py
compare_controller.py
history_controller.py
```

---

## Classes

```
ImageController
ChatController
CompareController
HistoryController
```

---

## Methods

```
upload_image()

analyze_image()

chat()

compare()

get_history()

build_response()

handle_exception()
```

Method names must use **snake_case**.

Class names must use **PascalCase**.

---

# Development Rules

Every controller must follow these rules.

✅ One file = One Controller class.

✅ Controllers must remain lightweight.

✅ No business logic.

✅ No AI processing.

✅ No database queries.

✅ No scraping code.

✅ Return JSON only.

✅ Validate every incoming request.

✅ Handle exceptions.

---

# Future Extensions

Possible future controllers

```
feedback_controller.py

authentication_controller.py

admin_controller.py

analytics_controller.py
```

These controllers should follow the same architecture and design rules.
