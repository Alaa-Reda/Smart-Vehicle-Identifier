"""
Vehicle Information Extractor

Extracts meaningful vehicle specifications from parsed HTML.
Improved: better price extraction, description filtering,
and image URL collection.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ==========================================================
# Regex Patterns
# ==========================================================

PATTERNS = {
    "engine": re.compile(
        r"(\d+\.\d+[\s-]?(?:liter|L|litre)|V\d+|inline[\s-]?\d+|I\d+|"
        r"flat[\s-]?\d+|boxer[\s-]?\d+)",
        re.IGNORECASE,
    ),
    "horsepower": re.compile(
        r"(\d{2,4})\s*(?:hp|horsepower|bhp|ps)\b",
        re.IGNORECASE,
    ),
    "torque": re.compile(
        r"(\d{2,4})\s*(?:lb[\s-]?ft|nm|pound[\s-]?feet)\b",
        re.IGNORECASE,
    ),
    "transmission": re.compile(
        r"(\d[\s-]?speed\s+(?:automatic|manual|cvt|dct|amt)|"
        r"(?:automatic|manual|cvt|dual[\s-]?clutch)(?:\s+transmission)?)",
        re.IGNORECASE,
    ),
    "fuel_economy": re.compile(
        r"(\d{1,2}(?:\.\d)?)\s*(?:mpg|miles per gallon|l/100km)",
        re.IGNORECASE,
    ),
    # Price: must be $10,000 or more (avoids $599 doc fees, $2,000 options etc.)
    "price": re.compile(
        r"\$\s*((?:[1-9]\d{1,2},\d{3}|\d{3},\d{3})(?:\.\d{2})?)\b",
    ),
    "year": re.compile(r"\b(19[89]\d|20[0-3]\d)\b"),
    "cylinders": re.compile(r"(\d)[\s-]?cylinder", re.IGNORECASE),
    "drive": re.compile(
        r"\b(AWD|4WD|FWD|RWD|4x4|all[\s-]wheel drive|"
        r"front[\s-]wheel drive|rear[\s-]wheel drive)\b",
        re.IGNORECASE,
    ),
    "fuel_type": re.compile(
        r"\b(gasoline|petrol|diesel|hybrid|electric|plug[\s-]?in hybrid|PHEV)\b",
        re.IGNORECASE,
    ),
    "body_type": re.compile(
        r"\b(sedan|coupe|convertible|hatchback|SUV|crossover|"
        r"pickup|truck|van|minivan|wagon|estate)\b",
        re.IGNORECASE,
    ),
}

SPEC_ALIASES = {
    "engine":       ["engine", "displacement", "engine size", "powertrain", "engine type"],
    "horsepower":   ["horsepower", "hp", "power", "bhp", "output", "max output"],
    "torque":       ["torque", "lb-ft", "nm", "max torque"],
    "transmission": ["transmission", "gearbox", "trans"],
    "fuel_economy": ["fuel economy", "mpg", "fuel efficiency", "mileage", "combined mpg", "highway mpg"],
    "price":        ["msrp", "base price", "starting price", "starting msrp"],
    "drive":        ["drivetrain", "drive", "driven wheels", "drive type"],
    "fuel_type":    ["fuel type", "fuel", "engine type"],
    "body_type":    ["body type", "body style", "style", "category", "vehicle type"],
    "cylinders":    ["cylinders", "no. of cylinders", "cylinder count", "number of cylinders"],
    "dimensions":   ["length", "width", "height", "wheelbase", "weight", "curb weight"],
}

# Noise phrases — paragraphs containing these are skipped as description
NOISE_PHRASES = [
    "cookie", "privacy policy", "javascript", "enable javascript",
    "browser", "captcha", "bot", "cloudflare", "please enable",
    "we use cookies", "terms of service", "subscribe", "newsletter",
    "advertisement", "sponsored", "all rights reserved",
]


class VehicleExtractor:

    def __init__(self, parsed: dict[str, Any]) -> None:
        self._parsed     = parsed
        self._text       = parsed.get("full_text", "")
        self._tables     = parsed.get("tables", [])
        self._paragraphs = parsed.get("paragraphs", [])

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    def _match(self, pattern_name: str) -> Optional[str]:
        p = PATTERNS.get(pattern_name)
        if not p:
            return None
        m = p.search(self._text)
        return m.group(0).strip() if m else None

    def _from_tables(self, field: str) -> Optional[str]:
        aliases = SPEC_ALIASES.get(field, [field])
        for table in self._tables:
            for key, value in table.items():
                if any(alias.lower() in key.lower() for alias in aliases):
                    return value.strip()
        return None

    def _get(self, field: str) -> Optional[str]:
        return self._from_tables(field) or self._match(field)

    # ----------------------------------------------------------
    # Spec Extractors
    # ----------------------------------------------------------

    def extract_engine(self)       -> Optional[str]: return self._get("engine")
    def extract_horsepower(self)   -> Optional[str]: return self._get("horsepower")
    def extract_torque(self)       -> Optional[str]: return self._get("torque")
    def extract_transmission(self) -> Optional[str]: return self._get("transmission")
    def extract_fuel_economy(self) -> Optional[str]: return self._get("fuel_economy")
    def extract_drive(self)        -> Optional[str]: return self._get("drive")
    def extract_fuel_type(self)    -> Optional[str]: return self._get("fuel_type")
    def extract_body_type(self)    -> Optional[str]: return self._get("body_type")
    def extract_cylinders(self)    -> Optional[str]: return self._get("cylinders")

    def extract_price(self) -> Optional[str]:
        """
        Extract MSRP price — must be ≥ $10,000.
        Skips loyalty/credit/lease/financing context lines.
        Prefers lines containing 'MSRP', 'starting', 'base price'.
        """
        # Noise context that usually surrounds fake prices
        PRICE_NOISE_CONTEXT = [
            "loyalty", "credit", "lease", "financing", "apr",
            "due at signing", "per month", "/mo", "doc fee",
            "destination", "rebate", "incentive", "discount",
            "paint protection", "dealer",
        ]

        # Try spec table first (most reliable)
        table_price = self._from_tables("price")
        if table_price:
            return table_price

        # Split text into lines and find price in MSRP context
        lines = self._text.split("\n") if "\n" in self._text else [self._text]

        best_price: Optional[str] = None

        for line in lines:
            line_lower = line.lower()

            # Skip lines with noise context
            if any(noise in line_lower for noise in PRICE_NOISE_CONTEXT):
                continue

            m = PATTERNS["price"].search(line)
            if not m:
                continue

            candidate = f"${m.group(1)}"

            # Prefer lines that explicitly mention MSRP or starting price
            if any(kw in line_lower for kw in ["msrp", "starting", "base price"]):
                return candidate  # Best possible match — return immediately

            # Otherwise keep as fallback
            if best_price is None:
                best_price = candidate

        # If no line-level match, try full text but skip first $XX,XXX after noise words
        if best_price is None:
            # Find all price matches and skip ones near noise
            for m in PATTERNS["price"].finditer(self._text):
                start = max(0, m.start() - 100)
                context = self._text[start:m.start()].lower()
                if not any(noise in context for noise in PRICE_NOISE_CONTEXT):
                    best_price = f"${m.group(1)}"
                    break

        return best_price

    def extract_price_list(self) -> list[dict[str, str]]:
        """
        Extract EVERY plausible trim/price pair found on the page
        (not just the single 'best' MSRP). Used to build a min/max
        price range and to show which trim costs what.

        Returns
        -------
        list[dict]
            [{"label": "X7 M60i", "price": "$115,000"}, ...]
            "label" is the nearest heading/table-key/line text that
            looks like a trim name; falls back to "" if none found.
        """

        PRICE_NOISE_CONTEXT = [
            "loyalty", "credit", "lease", "financing", "apr",
            "due at signing", "per month", "/mo", "doc fee",
            "destination", "rebate", "incentive", "discount",
            "paint protection", "dealer",
        ]

        entries: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()

        def _add(label: str, price: str) -> None:
            key = (label.strip().lower(), price)
            if price and key not in seen:
                seen.add(key)
                entries.append({"label": label.strip(), "price": price})

        # 1) Spec tables: a row's own key often IS the trim/field name.
        for table in self._tables:
            for key, value in table.items():
                m = PATTERNS["price"].search(value)
                if m:
                    _add(key, f"${m.group(1)}")

        # 2) Line-by-line scan of full text — pair the price with the
        #    most recent trim-looking token on the same line, or the
        #    nearest preceding heading if the line has no clear label.
        headings = self._parsed.get("headings", [])
        lines = self._text.split("\n") if "\n" in self._text else [self._text]
        last_heading = ""
        heading_idx = 0

        for line in lines:
            line_lower = line.lower()
            if any(noise in line_lower for noise in PRICE_NOISE_CONTEXT):
                continue

            for m in PATTERNS["price"].finditer(line):
                price = f"${m.group(1)}"
                # Text on the line before the price, stripped of noise words,
                # is usually the trim/model name (e.g. "ALPINA XB7 ... $156,000").
                before = line[: m.start()].strip(" -:|•\t")
                label = before if 0 < len(before) <= 60 else last_heading
                _add(label, price)

            # Advance the "nearest heading" pointer opportunistically —
            # cheap heuristic since we don't have per-line source positions.
            if heading_idx < len(headings) and headings[heading_idx].strip() and \
                    headings[heading_idx].lower() in line_lower:
                last_heading = headings[heading_idx]
                heading_idx += 1

        return entries

    def extract_description(self) -> Optional[str]:
        """Return best informative paragraph — skip cookie/privacy noise."""
        candidates = [
            p for p in self._paragraphs
            if len(p) > 80
            and not any(noise in p.lower() for noise in NOISE_PHRASES)
        ]
        if not candidates:
            return None
        # Prefer paragraphs that mention the vehicle make/model
        vehicle_keywords = ["engine", "horsepower", "torque", "drive",
                            "performance", "acceleration", "mpg", "sedan",
                            "suv", "coupe", "mph", "cylinder"]
        scored = sorted(
            candidates,
            key=lambda p: sum(kw in p.lower() for kw in vehicle_keywords),
            reverse=True,
        )
        return scored[0]

    def extract_dimensions(self) -> dict[str, str]:
        dims: dict[str, str] = {}
        dim_keys = SPEC_ALIASES["dimensions"]
        for table in self._tables:
            for key, value in table.items():
                if any(d.lower() in key.lower() for d in dim_keys):
                    dims[key] = value
        return dims

    def extract_features(self) -> list[str]:
        """Extract feature bullets — skip navigation/menu noise."""
        features: list[str] = []
        feature_keywords = [
            "feature", "standard", "option", "equipment",
            "include", "come with", "safety", "infotainment",
            "connectivity", "audio",
        ]
        noise_keywords = [
            "read more", "click here", "subscribe", "cookie",
            "privacy", "terms", "newsletter", "shop now",
        ]
        for items_list in self._parsed.get("lists", []):
            joined = " ".join(items_list).lower()
            if not any(kw in joined for kw in feature_keywords):
                continue
            for item in items_list:
                item = item.strip()
                # Skip noise items and very short ones
                if (
                    len(item) < 5
                    or any(n in item.lower() for n in noise_keywords)
                    or len(item) > 300
                ):
                    continue
                features.append(item)
        return list(dict.fromkeys(features))

    # ----------------------------------------------------------
    # Full Extraction
    # ----------------------------------------------------------

    def extract(self) -> dict[str, Any]:
        return {
            "source_url":   self._parsed.get("url", ""),
            "page_title":   self._parsed.get("title", ""),
            "description":  self.extract_description(),
            "engine":       self.extract_engine(),
            "horsepower":   self.extract_horsepower(),
            "torque":       self.extract_torque(),
            "transmission": self.extract_transmission(),
            "fuel_economy": self.extract_fuel_economy(),
            "fuel_type":    self.extract_fuel_type(),
            "body_type":    self.extract_body_type(),
            "drive":        self.extract_drive(),
            "cylinders":    self.extract_cylinders(),
            "price":        self.extract_price(),
            "price_list":   self.extract_price_list(),
            "dimensions":   self.extract_dimensions(),
            "features":     self.extract_features(),
        }