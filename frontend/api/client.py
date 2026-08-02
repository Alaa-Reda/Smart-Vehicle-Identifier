r"""
===========================================================
Smart Vehicle Identifier
API Client
===========================================================

Centralized HTTP client.

Responsibilities
----------------
- HTTP requests
- Timeout handling
- Error handling
- Health checks
- Response validation

All API modules use this client.
"""

from __future__ import annotations

from typing import Any

import requests

from config.settings import settings


# ==========================================================
# Exceptions
# ==========================================================

class APIError(Exception):
    """Base API exception."""


class APIConnectionError(APIError):
    """Backend unreachable."""


class APIResponseError(APIError):
    """Unexpected API response."""


# ==========================================================
# Client
# ==========================================================

class APIClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:

        self.base_url = (
            base_url or settings.API_BASE_URL
        ).rstrip("/")

        self.timeout = (
            timeout or settings.REQUEST_TIMEOUT
        )

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "SmartVehicleIdentifier/1.0",
            }
        )

    # ======================================================

    def _url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    # ======================================================

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:

        try:
            response = self.session.request(
                method=method,
                url=self._url(endpoint),
                timeout=self.timeout,
                **kwargs,
            )

            response.raise_for_status()

        except requests.ConnectionError as exc:
            raise APIConnectionError(
                "Unable to connect to backend."
            ) from exc

        except requests.Timeout as exc:
            raise APIConnectionError(
                "Request timed out."
            ) from exc

        except requests.HTTPError as exc:
            raise APIResponseError(
                f"{response.status_code}: {response.text}"
            ) from exc

        except requests.RequestException as exc:
            raise APIError(str(exc)) from exc

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        if "application/json" in content_type:
            if response.content:
                return response.json()
            return {}

        return response.content

    # ======================================================

    def get(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:

        return self._request(
            "GET",
            endpoint,
            **kwargs,
        )

    # ======================================================

    def post(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:

        return self._request(
            "POST",
            endpoint,
            **kwargs,
        )

    # ======================================================

    def put(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:

        return self._request(
            "PUT",
            endpoint,
            **kwargs,
        )

    # ======================================================

    def delete(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:

        return self._request(
            "DELETE",
            endpoint,
            **kwargs,
        )

    # ======================================================

    def health(self) -> bool:

        try:
            self.get("/health")
            return True

        except APIError:
            return False

    # ======================================================

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()


# ==========================================================
# Singleton
# ==========================================================

client = APIClient()