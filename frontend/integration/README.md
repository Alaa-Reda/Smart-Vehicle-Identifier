# Frontend <-> Backend Integration Notes

This folder does not contain code that runs — it is documentation for
whoever connects this Streamlit frontend to the FastAPI backend later.
Read this before touching `api/`.

## 1. How the connection works

All backend calls go through three files:

```
api/client.py       -> low-level HTTP wrapper (requests + error handling)
api/vehicle_api.py   -> detection, history, reports
api/chat_api.py       -> AI assistant / RAG chat
```

Pages never call `requests` directly. They import functions from
`vehicle_api.py` / `chat_api.py`. This means the backend team can change
routes or payload shapes and only these two files need updating — no page
code changes.

## 2. Setting the backend URL

The base URL is read from an environment variable:

```
API_BASE_URL=http://localhost:8000
```

Set it before running Streamlit:

```
# Windows PowerShell
$env:API_BASE_URL="http://localhost:8000"
streamlit run app.py

# macOS / Linux
export API_BASE_URL=http://localhost:8000
streamlit run app.py
```

Or copy `integration/.env.example` to `.env` in the project root and load
it with `python-dotenv` at the top of `app.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```//add `python-dotenv` to requirements.txt if you take this route.

## 3. Expected backend routes

| Method | Path                              | Used by                          |
|--------|-----------------------------------|-----------------------------------|
| POST   | /api/vehicles/detect               | api/vehicle_api.detect_vehicle    |
| GET    | /api/vehicles/{id}                 | api/vehicle_api.get_vehicle_details |
| GET    | /api/vehicles/history               | api/vehicle_api.get_detection_history |
| DELETE | /api/vehicles/{id}                 | api/vehicle_api.delete_detection  |
| GET    | /api/vehicles/{id}/report            | api/vehicle_api.download_report   |
| POST   | /api/chat/message                    | api/chat_api.send_message         |
| GET    | /api/chat/history                     | api/chat_api.get_chat_history     |
| GET    | /api/chat/{conversation_id}           | api/chat_api.get_conversation     |
| DELETE | /api/chat/{conversation_id}           | api/chat_api.delete_conversation  |

If the backend uses different paths, only edit the string literals inside
`api/vehicle_api.py` and `api/chat_api.py` — nothing else needs to change.

## 4. Response shape the frontend expects

`detect_vehicle()` should return JSON like:

```json
{
  "detection_id": "VVA202405201030",
  "confidence": 98.8,
  "make": "BMW",
  "model": "M4 Competition",
  "year": 2022,
  "body_type": "Coupe",
  "color": "Blue"
}
```

`send_message()` should return:

```json
{
  "conversation_id": "conv_123",
  "reply": "The BMW M4 Competition 2022 produces 503 hp...",
  "suggested_questions": ["Fuel economy", "Top speed"]
}
```

If the backend's field names differ, adjust the `.get(...)` calls in the
page files (`pages/1_Detect.py`, `pages/4_Chat.py`) rather than renaming
fields on the backend.

## 5. Local demo mode (no backend running)

Every call in `api/` raises `api.client.APIError` on network failure.
Pages already catch this and fall back to placeholder data so designers
and reviewers can click through the UI without the backend running. Once
the real backend responds, the fallback branches simply stop triggering —
no flag to flip.

## 6. Checklist for wiring up a new page

1. Add a function to `api/vehicle_api.py` or `api/chat_api.py` (or a new
   `api/<name>_api.py` file if it's a new domain).
2. Call it from the page inside a `try/except APIError` block.
3. On success, store the result in `st.session_state` via a helper in
   `utils/session.py` if other pages need it.
4. On failure, show `st.warning(...)` with demo data — never crash the page.
