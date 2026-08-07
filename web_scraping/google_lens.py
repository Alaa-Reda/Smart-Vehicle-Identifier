"""
Google Lens API Handler

Uses Google Lens (via SerpAPI) to identify vehicles visually.
Uploads image to Litterbox (free, no key) then queries SerpAPI.

Requires
--------
SERPAPI_KEY  — in .env  (https://serpapi.com)

Optional
--------
IMGBB_API_KEY — in .env fallback (https://api.imgbb.com)
"""

from __future__ import annotations

import base64
import io
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional, Union

# Fix: web_scraping/requests.py shadows the real `requests` library.
_ws_dir = str(Path(__file__).resolve().parent)
_orig_path = sys.path[:]
sys.path = [p for p in sys.path if p != _ws_dir]
import requests as requests  # noqa — real pip requests
sys.path = _orig_path

from dotenv import load_dotenv
from PIL import Image

# load_dotenv() with no args only searches upward from the CURRENT WORKING
# DIRECTORY of the process that started Python — not from this file's location.
# If the app is launched from a different cwd (e.g. `uvicorn` run from inside
# web_scraping/, or from an IDE with a different working dir), it silently
# finds no .env and every os.getenv() below returns "". Point it explicitly
# at the project root instead: web_scraping/google_lens.py -> parent.parent.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

logger = logging.getLogger(__name__)

if not _ENV_PATH.exists():
    logger.warning(".env not found at expected path: %s", _ENV_PATH)

SERPAPI_KEY:   str = os.getenv("SERPAPI_KEY", "")
IMGBB_API_KEY: str = os.getenv("IMGBB_API_KEY", "")

LITTERBOX_ENDPOINT = "https://litterbox.catbox.moe/resources/internals/api.php"
IMGBB_ENDPOINT     = "https://api.imgbb.com/1/upload"
ZEROXZERO_ENDPOINT = "https://0x0.st"
LENS_ENDPOINT      = "https://serpapi.com/search"

# Litterbox/Catbox sit behind an anti-bot check that returns 412 for requests
# that look like they came from a bare script (no browser-like headers).
UPLOAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
}

BLOCKED_DOMAINS = {
    "facebook.com", "instagram.com", "tiktok.com",
    "youtube.com", "twitter.com", "pinterest.com",
    "reddit.com", "tumblr.com", "snapchat.com",
}


def _describe_error(e: requests.RequestException) -> str:
    """
    Distinguish 'DNS couldn't resolve the host' (a local network/firewall/
    DNS problem — not something this code can fix) from an actual HTTP-level
    failure, so the log line tells you which one you're looking at.
    """
    msg = str(e)
    if "getaddrinfo failed" in msg or "NameResolutionError" in msg or "Failed to resolve" in msg:
        return f"DNS RESOLUTION FAILED (local network/firewall/DNS issue, not a code bug): {msg}"
    body = getattr(e.response, "text", "")[:200] if getattr(e, "response", None) else ""
    return f"{msg} | body={body!r}"


class GoogleLensClient:
    """Submit vehicle images to Google Lens via SerpAPI."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or SERPAPI_KEY
        if not self.api_key:
            raise ValueError(
                "SERPAPI_KEY not found. "
                "Get a free key from https://serpapi.com"
            )

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    @staticmethod
    def _to_bytes(image: Image.Image) -> bytes:
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG", quality=90)
        return buf.getvalue()

    @staticmethod
    def _load_image(image: Union[str, Path, Image.Image]) -> Image.Image:
        if isinstance(image, (str, Path)):
            return Image.open(image).convert("RGB")
        if isinstance(image, Image.Image):
            return image.convert("RGB")
        raise TypeError(f"Unsupported image type: {type(image)}")

    # ----------------------------------------------------------
    # Image hosting — Provider 1: Litterbox (no key needed)
    # ----------------------------------------------------------

    @staticmethod
    def _upload_litterbox(img_bytes: bytes, retries: int = 2) -> Optional[str]:
        last_error: Optional[str] = None

        for attempt in range(1, retries + 1):
            try:
                r = requests.post(
                    LITTERBOX_ENDPOINT,
                    headers=UPLOAD_HEADERS,
                    data={"reqtype": "fileupload", "time": "1h"},
                    files={"fileToUpload": ("vehicle.jpg", img_bytes, "image/jpeg")},
                    timeout=30,
                )
                r.raise_for_status()
                url = r.text.strip()
                if url.startswith("https://"):
                    logger.info("Litterbox upload OK: %s", url)
                    return url
                logger.warning("Litterbox unexpected response: %r", url[:200])
                return None
            except requests.RequestException as e:
                last_error = _describe_error(e)
                logger.warning(
                    "Litterbox upload attempt %d/%d failed: %s",
                    attempt, retries, last_error,
                )

        logger.warning("Litterbox upload failed after %d attempts: %s", retries, last_error)
        return None

    # ----------------------------------------------------------
    # Image hosting — Provider 2: ImgBB (free key)
    # ----------------------------------------------------------

    @staticmethod
    def _upload_imgbb(img_bytes: bytes) -> Optional[str]:
        if not IMGBB_API_KEY:
            logger.warning("IMGBB_API_KEY not set — skipping ImgBB.")
            return None
        try:
            r = requests.post(
                IMGBB_ENDPOINT,
                headers=UPLOAD_HEADERS,
                params={"key": IMGBB_API_KEY},
                data={"image": base64.b64encode(img_bytes).decode()},
                timeout=30,
            )
            r.raise_for_status()
            url = r.json().get("data", {}).get("url")
            if url:
                logger.info("ImgBB upload OK: %s", url)
                return url
            return None
        except requests.RequestException as e:
            logger.warning("ImgBB upload failed: %s", _describe_error(e))
            return None

    # ----------------------------------------------------------
    # Image hosting — Provider 3: 0x0.st (no key needed)
    # ----------------------------------------------------------

    @staticmethod
    def _upload_0x0st(img_bytes: bytes) -> Optional[str]:
        try:
            r = requests.post(
                ZEROXZERO_ENDPOINT,
                headers=UPLOAD_HEADERS,
                files={"file": ("vehicle.jpg", img_bytes, "image/jpeg")},
                timeout=30,
            )
            r.raise_for_status()
            url = r.text.strip()
            if url.startswith("https://"):
                logger.info("0x0.st upload OK: %s", url)
                return url
            logger.warning("0x0.st unexpected response: %r", url[:200])
            return None
        except requests.RequestException as e:
            logger.warning("0x0.st upload failed: %s", _describe_error(e))
            return None

    def _get_public_url(self, img_bytes: bytes) -> Optional[str]:
        # Litterbox's 412 is most likely Cloudflare/anti-bot filtering at the
        # TLS or request-fingerprint level (not just a missing header) — a
        # plain `requests` call may never pass it reliably. ImgBB with a key
        # is deterministic, so use it first whenever a key is configured;
        # Litterbox and 0x0.st stay as free fallbacks. If ALL THREE fail with
        # a DNS-resolution error, it's a local network/firewall issue, not
        # something any of these providers can fix — see the log message.
        if IMGBB_API_KEY:
            return (
                self._upload_imgbb(img_bytes)
                or self._upload_litterbox(img_bytes)
                or self._upload_0x0st(img_bytes)
            )
        return (
            self._upload_litterbox(img_bytes)
            or self._upload_0x0st(img_bytes)
            or self._upload_imgbb(img_bytes)
        )

    # ----------------------------------------------------------
    # SerpAPI Google Lens
    # ----------------------------------------------------------

    def search_by_image(
        self,
        image: Union[str, Path, Image.Image],
    ) -> dict[str, Any]:
        """Upload image publicly then query Google Lens."""

        pil  = self._load_image(image)
        data = self._to_bytes(pil)
        url  = self._get_public_url(data)

        if not url:
            logger.error("All image hosts failed. Cannot query Google Lens.")
            return {}

        try:
            r = requests.get(
                LENS_ENDPOINT,
                params={
                    "engine":  "google_lens",
                    "api_key": self.api_key,
                    "url":     url,
                    "hl": "en",
                    "gl": "us",
                },
                timeout=30,
            )
            r.raise_for_status()
            result = r.json()
            if "error" in result:
                logger.error("SerpAPI error: %s", result["error"])
                return {}
            logger.info("Google Lens response received.")
            return result
        except requests.RequestException as e:
            logger.error("Google Lens API error: %s", e)
            return {}

    def get_vehicle_info(
        self,
        image: Union[str, Path, Image.Image],
    ) -> dict[str, Any]:
        """Search image → return title + filtered URLs + thumbnails."""

        raw = self.search_by_image(image)
        if not raw:
            return {"title": None, "urls": [], "visual_matches": [], "knowledge_graph": {}}

        visual_matches = [
            {
                "title":     m.get("title", ""),
                "link":      m.get("link", ""),
                "source":    m.get("source", ""),
                "thumbnail": m.get("thumbnail", ""),
            }
            for m in raw.get("visual_matches", [])[:15]
        ]

        urls = [
            m["link"] for m in visual_matches
            if m["link"] and not any(d in m["link"] for d in BLOCKED_DOMAINS)
        ]

        thumbnails = [
            m["thumbnail"] for m in visual_matches
            if m.get("thumbnail")
        ]

        knowledge_graph = raw.get("knowledge_graph", {})
        title = (
            knowledge_graph.get("title")
            or (visual_matches[0]["title"] if visual_matches else None)
        )

        logger.info(
            "Google Lens: %d matches → %d usable URLs.",
            len(visual_matches), len(urls),
        )

        return {
            "title":           title,
            "urls":            urls,
            "thumbnails":      thumbnails,
            "visual_matches":  visual_matches,
            "knowledge_graph": knowledge_graph,
        }