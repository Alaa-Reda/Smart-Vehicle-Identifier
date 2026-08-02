"""
Data Cleaner

Cleans and normalizes raw extracted vehicle information
before it is passed to the JSON builder.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ==========================================================
# Cleaning Rules
# ==========================================================

# Maximum field lengths
MAX_LENGTHS = {
    "description": 2000,
    "engine":       100,
    "horsepower":    50,
    "torque":        50,
    "transmission": 100,
    "fuel_economy":  50,
    "fuel_type":     50,
    "body_type":     50,
    "drive":         50,
    "cylinders":     30,
    "price":         50,
}


# ==========================================================
# Cleaner
# ==========================================================

class DataCleaner:
    """
    Normalizes and validates extracted vehicle data.

    - Strips whitespace and extra characters
    - Removes duplicates from lists
    - Normalizes casing for key fields
    - Truncates oversized fields
    - Removes null/empty values
    """

    # ----------------------------------------------------------
    # String Cleaners
    # ----------------------------------------------------------

    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        """Strip whitespace, collapse internal spaces, remove control chars."""

        if not text:
            return None

        text = re.sub(r"[\r\n\t]+", " ", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = text.strip()

        return text if text else None

    @staticmethod
    def clean_price(price: Optional[str]) -> Optional[str]:
        """Normalize price to '$XX,XXX' format."""

        if not price:
            return None

        # Keep only digits and $ and ,
        cleaned = re.sub(r"[^\d$,.]", "", price).strip()
        return cleaned if cleaned else None

    @staticmethod
    def clean_horsepower(hp: Optional[str]) -> Optional[str]:
        """Extract numeric HP value with unit."""

        if not hp:
            return None

        match = re.search(r"(\d{2,4})\s*(?:hp|bhp|ps)?", hp, re.IGNORECASE)
        if match:
            return f"{match.group(1)} hp"
        return None

    @staticmethod
    def clean_fuel_economy(mpg: Optional[str]) -> Optional[str]:
        """Normalize fuel economy value."""

        if not mpg:
            return None

        match = re.search(r"(\d{1,2}(?:\.\d)?)", mpg)
        if match:
            return f"{match.group(1)} mpg"
        return None

    @staticmethod
    def normalize_drive(drive: Optional[str]) -> Optional[str]:
        """Normalize drivetrain to standard abbreviations."""

        if not drive:
            return None

        mapping = {
            "all-wheel drive": "AWD",
            "all wheel drive": "AWD",
            "four-wheel drive": "4WD",
            "four wheel drive": "4WD",
            "4x4": "4WD",
            "front-wheel drive": "FWD",
            "front wheel drive": "FWD",
            "rear-wheel drive": "RWD",
            "rear wheel drive": "RWD",
        }

        lower = drive.lower().strip()
        for phrase, abbr in mapping.items():
            if phrase in lower:
                return abbr

        return drive.upper().strip()

    @classmethod
    def clean_price_list(cls, entries: Optional[list[dict[str, Any]]]) -> list[dict[str, str]]:
        """Clean each {label, price} entry and drop unusable/duplicate ones."""

        if not entries:
            return []

        cleaned: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()

        for entry in entries:
            price = cls.clean_price(entry.get("price"))
            if not price:
                continue
            label = cls.clean_text(entry.get("label")) or ""
            key = (label.lower(), price)
            if key in seen:
                continue
            seen.add(key)
            cleaned.append({"label": label, "price": price})

        return cleaned

    @staticmethod
    def clean_list(items: list[str]) -> list[str]:
        """Remove duplicates and empty strings from a list."""

        seen: set[str] = set()
        cleaned = []

        for item in items:
            item = item.strip()
            if item and item.lower() not in seen:
                seen.add(item.lower())
                cleaned.append(item)

        return cleaned

    # ----------------------------------------------------------
    # Field-Level Cleaning
    # ----------------------------------------------------------

    def _truncate(self, value: Optional[str], field: str) -> Optional[str]:
        """Truncate field to its max allowed length."""

        if not value:
            return value

        max_len = MAX_LENGTHS.get(field, 500)
        return value[:max_len] if len(value) > max_len else value

    # ----------------------------------------------------------
    # Full Clean
    # ----------------------------------------------------------

    def clean(self, extracted: dict[str, Any]) -> dict[str, Any]:
        """
        Clean and normalize all extracted vehicle fields.

        Parameters
        ----------
        extracted : dict
            Raw output from VehicleExtractor.extract()

        Returns
        -------
        dict
            Cleaned vehicle data ready for JSON building.
        """

        cleaned = {
            "source_url":   self.clean_text(extracted.get("source_url")),
            "page_title":   self.clean_text(extracted.get("page_title")),
            "description":  self._truncate(
                self.clean_text(extracted.get("description")), "description"
            ),
            "engine":       self._truncate(
                self.clean_text(extracted.get("engine")), "engine"
            ),
            "horsepower":   self.clean_horsepower(extracted.get("horsepower")),
            "torque":       self._truncate(
                self.clean_text(extracted.get("torque")), "torque"
            ),
            "transmission": self._truncate(
                self.clean_text(extracted.get("transmission")), "transmission"
            ),
            "fuel_economy": self.clean_fuel_economy(extracted.get("fuel_economy")),
            "fuel_type":    self.clean_text(extracted.get("fuel_type")),
            "body_type":    self.clean_text(extracted.get("body_type")),
            "drive":        self.normalize_drive(extracted.get("drive")),
            "cylinders":    self.clean_text(extracted.get("cylinders")),
            "price":        self.clean_price(extracted.get("price")),
            "price_list":   self.clean_price_list(extracted.get("price_list")),
            "dimensions":   {
                k: self.clean_text(v)
                for k, v in (extracted.get("dimensions") or {}).items()
                if self.clean_text(v)
            },
            "features":     self.clean_list(extracted.get("features") or []),
        }

        # Remove top-level None values
        cleaned = {k: v for k, v in cleaned.items() if v not in (None, {}, [])}

        return cleaned