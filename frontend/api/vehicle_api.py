"""
Vehicle image identification endpoints.

Matches controllers/image_controller.py (prefix: /api/v1/image):

    POST /api/v1/image/identify                 -> identify a vehicle from an image
    POST /api/v1/image/identify-with-question    -> identify + answer a question about it
    POST /api/v1/image/google-lens               -> fallback identification via Google Lens

IMPORTANT changes vs. the old stub (api/vehicle_api.py before):
  * The multipart field name the backend expects is `file`, not `image`
    (FastAPI param is `file: UploadFile = File(...)`).
  * There is NO detection_id concept on the backend at all:
      - no GET  /api/v1/image/{detection_id}
      - no DELETE /api/v1/image/{detection_id}
      - no GET  /api/v1/image/{detection_id}/report  (no PDF endpoint exists)
    Everything is scoped by `session_id` instead. For "all vehicles seen in
    this session" or "past detections", use api/history_api.py.
  * download_report() has been REMOVED — there is nothing on the backend
    to call. If pages/11_PDF_Report.py needs a PDF, we have two options:
      (a) ask the backend team to add a report endpoint, or
      (b) generate the PDF client-side in Streamlit (e.g. with reportlab
          or the existing docx/pdf tooling) from whatever
          identify_vehicle() / history_api.get_vehicle_history() return.
    Send me pages/11_PDF_Report.py and I'll wire whichever you pick.
"""

from api.client import api_client


def identify_vehicle(
    image_bytes: bytes,
    filename: str,
    session_id: str | None = None,
    language: str | None = None,
    content_type: str = "image/jpeg",
) -> dict:
    """Upload an image and get back the identification result.

    The exact response shape comes from services.vehicle_service, which
    isn't visible in the controller — confirm the real fields once you can
    hit this endpoint directly (e.g. via /docs) so pages/3_Result.py reads
    the right keys.
    """
    files = {"file": (filename, image_bytes, content_type)}
    data = {}
    if session_id:
        data["session_id"] = session_id
    if language:
        data["language"] = language
    return api_client.post("/api/v1/image/identify", files=files, data=data)


def identify_with_question(
    image_bytes: bytes,
    filename: str,
    question: str,
    session_id: str | None = None,
    language: str | None = None,
    content_type: str = "image/jpeg",
) -> dict:
    """Identify a vehicle AND answer a specific question about it in one call."""
    files = {"file": (filename, image_bytes, content_type)}
    data = {"question": question}
    if session_id:
        data["session_id"] = session_id
    if language:
        data["language"] = language
    return api_client.post("/api/v1/image/identify-with-question", files=files, data=data)


def identify_via_google_lens(
    image_bytes: bytes,
    filename: str,
    session_id: str | None = None,
    language: str | None = None,
    content_type: str = "image/jpeg",
) -> dict:
    """Fallback path when the primary classifier can't confidently identify the vehicle."""
    files = {"file": (filename, image_bytes, content_type)}
    data = {}
    if session_id:
        data["session_id"] = session_id
    if language:
        data["language"] = language
    return api_client.post("/api/v1/image/google-lens", files=files, data=data)
# ----------------------------------------------------------------------
# Backward compatibility
# ----------------------------------------------------------------------

def detect_vehicle(
    image_bytes: bytes,
    filename: str,
    session_id: str | None = None,
    language: str | None = None,
    content_type: str = "image/jpeg",
):
    return identify_vehicle(
        image_bytes=image_bytes,
        filename=filename,
        session_id=session_id,
        language=language,
        content_type=content_type,
    )