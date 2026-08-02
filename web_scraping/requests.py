"""
HTTP Requests Handler

Handles static HTTP requests for downloading webpage content.
Uses requests library with session management and retry logic.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# ==========================================================
# Default Headers
# ==========================================================

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ==========================================================
# HTTP Client
# ==========================================================

class HTTPClient:
    """
    HTTP client with session management, retries, and timeout handling.
    """

    def __init__(
        self,
        timeout: int = 15,
        retries: int = 3,
        delay: float = 1.0,
    ) -> None:

        self.timeout = timeout
        self.delay = delay

        self._session = requests.Session()
        self._session.headers.update(DEFAULT_HEADERS)

        # Retry strategy
        retry = Retry(
            total=retries,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def get(self, url: str, params: Optional[dict] = None) -> Optional[str]:
        """
        Send GET request and return HTML content.

        Parameters
        ----------
        url : str
            Target URL.

        params : dict | None
            Optional query parameters.

        Returns
        -------
        str | None
            Raw HTML content, or None on failure.
        """

        try:
            time.sleep(self.delay)

            response = self._session.get(
                url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            logger.info("GET %s → %d", url, response.status_code)

            return response.text

        except RequestException as error:
            logger.error("Request failed for %s: %s", url, error)
            return None

    def close(self) -> None:
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()