"""
Vehicle comparison endpoints.

Matches controllers/compare_controller.py (prefix: /api/v1/compare):

    POST   /api/v1/compare/text                   vehicles:[names], aspect?, session_id?, language?
    POST   /api/v1/compare/images                  2-5 image files, aspect?, session_id?, language?
    GET    /api/v1/compare/history/{session_id}     limit
    DELETE /api/v1/compare/{comparison_id}

None of the pages you've shared reference a comparison feature yet — this
file is here so it exists if/when a "Compare vehicles" page gets added.
Delete it if you don't need it; it costs nothing sitting unused.
"""

from api.client import api_client


def compare_by_text(
    vehicles: list[str],
    aspect: str | None = None,
    session_id: str | None = None,
    language: str | None = None,
) -> dict:
    payload = {"vehicles": vehicles}
    if aspect:
        payload["aspect"] = aspect
    if session_id:
        payload["session_id"] = session_id
    if language:
        payload["language"] = language
    return api_client.post("/api/v1/compare/text", json=payload)


def compare_by_images(
    images: list[tuple[bytes, str]],
    aspect: str | None = None,
    session_id: str | None = None,
    language: str | None = None,
) -> dict:
    """`images` is a list of (image_bytes, filename) tuples, 2 to 5 items.

    Note: api/client.py's `post(files=...)` is typed as `dict` but `requests`
    also accepts a list of (field_name, (filename, bytes, content_type))
    tuples for repeated fields like this — that's what's used here.
    """
    files = [("files", (name, data, "image/jpeg")) for data, name in images]
    data = {}
    if aspect:
        data["aspect"] = aspect
    if session_id:
        data["session_id"] = session_id
    if language:
        data["language"] = language
    return api_client.post("/api/v1/compare/images", files=files, data=data)


def get_comparison_history(session_id: str, limit: int = 10) -> dict:
    return api_client.get(f"/api/v1/compare/history/{session_id}", params={"limit": limit})


def delete_comparison(comparison_id: str) -> dict:
    return api_client.delete(f"/api/v1/compare/{comparison_id}")