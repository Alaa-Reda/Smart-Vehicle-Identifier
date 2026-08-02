"""
===========================================================
Smart Vehicle Identifier
Analysis Service
===========================================================

Coordinates the complete vehicle analysis workflow.

Responsibilities
----------------
- Validate input
- Call backend API
- Handle errors
- Update session state
- Store history
- Return domain models

No UI code lives here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from PIL import Image

from api.vehicle_api import vehicle_api
from models.vehicle import VehicleResult
from utils.session import get, set


# ==========================================================
# Exceptions
# ==========================================================

class AnalysisError(Exception):
    """Base analysis exception."""


class NoImageError(AnalysisError):
    """Raised when no image is supplied."""


# ==========================================================
# Analysis Record
# ==========================================================

@dataclass(frozen=True, slots=True)
class AnalysisRecord:
    """Single analysis history record."""

    timestamp: datetime
    result: VehicleResult


# ==========================================================
# Service
# ==========================================================

class AnalysisService:
    """Coordinates the vehicle analysis workflow."""

    # ======================================================

    def analyze(
        self,
        image: Image.Image | None,
    ) -> VehicleResult:
        """
        Analyze a vehicle image.
        """

        if image is None:
            raise NoImageError(
                "No image was provided."
            )

        result = vehicle_api.classify(image)

        self._save_result(result)
        self._append_history(result)

        return result

    # ======================================================

    def latest(self) -> VehicleResult | None:
        """Return the latest analysis result."""

        return get("analysis_result")

    # ======================================================

    def history(self) -> list[AnalysisRecord]:
        """Return the analysis history."""

        return get("analysis_history", [])

    # ======================================================

    def clear(self) -> None:
        """Clear analysis session data."""

        set("analysis_result", None)
        set("analysis_history", [])

    # ======================================================

    def _save_result(
        self,
        result: VehicleResult,
    ) -> None:
        """Save the latest analysis result."""

        set("analysis_result", result)

    # ======================================================

    def _append_history(
        self,
        result: VehicleResult,
    ) -> None:
        """Append a result to the analysis history."""

        history = self.history()

        history.append(
            AnalysisRecord(
                timestamp=datetime.now(),
                result=result,
            )
        )

        set("analysis_history", history)


# ==========================================================
# Singleton
# ==========================================================

analysis_service = AnalysisService()