"""
JSON Document Builder

Converts cleaned vehicle data into a standardized MongoDB document.
Now includes thumbnail images from Google Lens.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _price_to_int(price: Optional[str]) -> Optional[int]:
    """'$115,000' -> 115000. Returns None if unparsable."""

    if not price:
        return None
    digits = re.sub(r"[^\d]", "", price)
    return int(digits) if digits else None


def _price_range(prices: list[dict[str, str]]) -> dict[str, str]:
    """Compute {min, max} formatted as '$X,XXX' from a list of price entries."""

    values = [
        v for v in (_price_to_int(p.get("price")) for p in prices) if v is not None
    ]
    if not values:
        return {}
    return {
        "min": f"${min(values):,}",
        "max": f"${max(values):,}",
    }


class VehicleDocumentBuilder:

    def build(
        self,
        make: str,
        model: str,
        year: Optional[str],
        cleaned_data: dict[str, Any],
        sources: Optional[list[str]] = None,
        images: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Build a vehicle MongoDB document.

        Parameters
        ----------
        images : list[str] | None
            Thumbnail URLs from Google Lens visual matches.
        cleaned_data : dict
            May include "price_list": [{"label", "price", "source"}, ...]
            collected across every scraped page (built by merge_pages()).
        """

        now = datetime.now(timezone.utc)
        price_list = cleaned_data.get("price_list", [])

        document = {
            "make":  make.strip().title(),
            "model": model.strip(),
            "year":  year.strip() if year else None,

            "body_type":    cleaned_data.get("body_type"),
            "engine":       cleaned_data.get("engine"),
            "horsepower":   cleaned_data.get("horsepower"),
            "torque":       cleaned_data.get("torque"),
            "transmission": cleaned_data.get("transmission"),
            "fuel_economy": cleaned_data.get("fuel_economy"),
            "fuel_type":    cleaned_data.get("fuel_type"),
            "drive":        cleaned_data.get("drive"),
            "cylinders":    cleaned_data.get("cylinders"),
            "price":        cleaned_data.get("price"),
            "price_range":  _price_range(price_list),
            "prices":       price_list,

            "dimensions":  cleaned_data.get("dimensions", {}),
            "features":    cleaned_data.get("features", []),
            "description": cleaned_data.get("description"),
            "images":      images or [],
            "sources":     sources or [],
            "created_at":  now,
            "updated_at":  now,
        }

        document = {k: v for k, v in document.items() if v not in (None, {}, [], "")}

        logger.info(
            "Built document for %s %s %s — %d fields.",
            year or "", make, model, len(document),
        )
        return document

    def merge_pages(self, pages: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge cleaned data from multiple scraped pages."""

        scalar_fields = [
            "body_type", "engine", "horsepower", "torque",
            "transmission", "fuel_economy", "fuel_type",
            "drive", "cylinders", "price", "description",
        ]

        merged: dict[str, Any] = {"dimensions": {}, "features": [], "price_list": []}
        seen_prices: set[tuple[str, str, str]] = set()

        for page in pages:
            source = page.get("source_url", "")

            for field in scalar_fields:
                if field not in merged and page.get(field):
                    merged[field] = page[field]

            if page.get("dimensions"):
                merged["dimensions"].update(page["dimensions"])

            if page.get("features"):
                existing = set(merged["features"])
                for f in page["features"]:
                    if f not in existing:
                        merged["features"].append(f)
                        existing.add(f)

            for entry in page.get("price_list", []):
                label = entry.get("label", "")
                price = entry.get("price", "")
                key = (label.lower(), price, source)
                if price and key not in seen_prices:
                    seen_prices.add(key)
                    merged["price_list"].append({
                        "label":  label,
                        "price":  price,
                        "source": source,
                    })

        return merged