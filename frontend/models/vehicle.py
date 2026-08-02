"""
===========================================================
Smart Vehicle Identifier
Domain Models
===========================================================

Shared models used across the application.

Used by:
- API Layer
- Services
- Components
- Pages
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ==========================================================
# Prediction
# ==========================================================

@dataclass(frozen=True, slots=True)
class Prediction:
    """
    Single classification prediction.
    """

    label: str
    confidence: float


# ==========================================================
# Vehicle Result
# ==========================================================

@dataclass(frozen=True, slots=True)
class VehicleResult:
    """
    Complete inference result.
    """

    make: str
    model: str

    year: str | None = None

    confidence: float = 0.0

    description: str = ""

    image_id: str | None = None

    processing_time: float | None = None

    predictions: list[Prediction] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    # ======================================================

    @property
    def full_name(self) -> str:
        """Return the full vehicle name."""

        return f"{self.make} {self.model}"

    # ======================================================

    @property
    def confidence_percent(self) -> str:
        """Return formatted confidence."""

        return f"{self.confidence:.2%}"

    # ======================================================

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
    ) -> "VehicleResult":
        """
        Create model from backend response.
        """

        predictions = [
            Prediction(
                label=item.get("label", "Unknown"),
                confidence=float(item.get("confidence", 0.0)),
            )
            for item in data.get("predictions", [])
        ]

        return cls(
            make=data.get("make", "Unknown"),
            model=data.get("model", "Unknown"),
            year=data.get("year"),
            confidence=float(data.get("confidence", 0.0)),
            description=data.get("description", ""),
            image_id=data.get("image_id"),
            processing_time=data.get("processing_time"),
            predictions=predictions,
            metadata=data.get("metadata", {}),
        )

    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize object.
        """

        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "confidence": self.confidence,
            "description": self.description,
            "image_id": self.image_id,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
            "predictions": [
                {
                    "label": prediction.label,
                    "confidence": prediction.confidence,
                }
                for prediction in self.predictions
            ],
        }