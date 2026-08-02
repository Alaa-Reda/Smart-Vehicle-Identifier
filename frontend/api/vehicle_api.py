"""
===========================================================
Smart Vehicle Identifier
Vehicle API
===========================================================

High-level interface for vehicle endpoints.

Returns domain models instead of dictionaries.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image

from api.client import client
from models.vehicle import VehicleResult


class VehicleAPI:
    """High-level wrapper around vehicle-related API endpoints."""

    # ======================================================
    # Helpers
    # ======================================================

    @staticmethod
    def _image_file(image: Image.Image) -> tuple[str, bytes, str]:
        """
        Convert a PIL image into an uploadable file tuple.
        """

        with BytesIO() as buffer:
            image.save(
                buffer,
                format="JPEG",
                quality=95,
            )

            return (
                "vehicle.jpg",
                buffer.getvalue(),
                "image/jpeg",
            )

    # ======================================================
    # Health
    # ======================================================

    def health(self) -> bool:
        return client.health()

    # ======================================================
    # Classification
    # ======================================================

    def classify(
        self,
        image: Image.Image,
    ) -> VehicleResult:

        response = client.post(
            "/vehicle/classify",
            files={
                "image": self._image_file(image)
            },
        )

        return VehicleResult.from_api(response)

    # ======================================================
    # Predictions
    # ======================================================

    def predictions(
        self,
        image: Image.Image,
    ) -> list[dict[str, Any]]:

        response = client.post(
            "/vehicle/predictions",
            files={
                "image": self._image_file(image)
            },
        )

        return response.get(
            "predictions",
            [],
        )

    # ======================================================
    # Vehicle Details
    # ======================================================

    def details(
        self,
        vehicle_id: str,
    ) -> VehicleResult:

        response = client.get(
            f"/vehicle/{vehicle_id}"
        )

        return VehicleResult.from_api(response)

    # ======================================================
    # Compare
    # ======================================================

    def compare(
        self,
        first_vehicle: str,
        second_vehicle: str,
    ) -> dict[str, Any]:

        return client.post(
            "/vehicle/compare",
            json={
                "first_vehicle": first_vehicle,
                "second_vehicle": second_vehicle,
            },
        )


# ==========================================================
# Singleton
# ==========================================================

vehicle_api = VehicleAPI()