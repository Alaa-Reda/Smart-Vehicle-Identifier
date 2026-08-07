"""
JSON Document Builder

Converts cleaned vehicle data into a standardized MongoDB document.
Now includes thumbnail images from Google Lens.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional

from .search import preferred_domain_rank

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


def _plausible_numeric_spec(value: Optional[str], field: str) -> bool:
    """
    Reject values whose extracted number is implausible for the field.

    Catches cases like horsepower="2017 hp", where a year sitting near a
    spec table got misread by the extractor as the numeric value instead
    of an actual date. No production car is anywhere close to these
    limits, so a number above them is a strong signal of mis-extraction
    rather than a real spec.
    """
    if not value:
        return True
    digits = re.search(r"\d[\d,]*", value)
    if not digits:
        return True
    try:
        number = int(digits.group(0).replace(",", ""))
    except ValueError:
        return True
    limits = {"horsepower": 2000, "torque": 2000}
    limit = limits.get(field)
    return limit is None or number <= limit


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

        content = f"""
        Make: {make}
        Model: {model}
        Year: {year or ""}

        Body Type: {cleaned_data.get("body_type", "")}
        Engine: {cleaned_data.get("engine", "")}
        Horsepower: {cleaned_data.get("horsepower", "")}
        Torque: {cleaned_data.get("torque", "")}
        Transmission: {cleaned_data.get("transmission", "")}
        Fuel Type: {cleaned_data.get("fuel_type", "")}
        Fuel Economy: {cleaned_data.get("fuel_economy", "")}

        Description:
        {cleaned_data.get("description", "")}

        Features:
        {", ".join(cleaned_data.get("features", []))}
        """.strip()

        document = {
            "make":  make.strip().title(),
            "model": model.strip(),
            "year":  year.strip() if year else None,

            "content": content,

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
        """
        Merge cleaned data from multiple scraped pages.

        Different search results can describe DIFFERENT trims/variants of
        the same nameplate (e.g. "Zonda S" vs "Zonda Cinque" vs "Zonda R"
        all surfacing for a "Pagani Zonda" search, or a Wikipedia page that
        covers an entire model generation across several years). The old
        version took the FIRST non-empty value found for each field,
        independent of which page it came from — so the engine could come
        from one trim's page while the horsepower came from a totally
        different trim's page, silently stitching together a
        self-contradictory "Frankenstein" document.

        This now collects every candidate value per field across all pages
        first, then:
          - if every page agrees (the common case), uses that value as before;
          - if pages disagree, takes the value the MOST pages agree on
            (majority vote) instead of whichever page happened to be
            scraped first, and logs the conflict so it's visible instead of
            silently baked into the saved document;
          - discards individual candidate values that are numerically
            implausible for the field (e.g. horsepower="2017 hp", which is
            almost always a year misread as a spec number rather than a
            real value).
        """
        scalar_fields = [
            "body_type", "engine", "horsepower", "torque",
            "transmission", "fuel_economy", "fuel_type",
            "drive", "cylinders", "price", "description",
        ]

        merged: dict[str, Any] = {"dimensions": {}, "features": [], "price_list": []}
        seen_prices: set[tuple[str, str, str]] = set()

        # field -> [(value, source_url), ...] across all pages
        candidates: dict[str, list[tuple[str, str]]] = {f: [] for f in scalar_fields}
        dimension_candidates: dict[str, list[tuple[str, str]]] = {}

        for page in pages:
            source = page.get("source_url", "")

            for field in scalar_fields:
                value = page.get(field)
                if not value:
                    continue
                if not _plausible_numeric_spec(value, field):
                    logger.warning(
                        "Discarding implausible '%s' value %r from %s "
                        "(likely a misread year/date, not a real spec).",
                        field, value, source,
                    )
                    continue
                candidates[field].append((value, source))

            for dim_key, dim_val in (page.get("dimensions") or {}).items():
                if dim_val:
                    dimension_candidates.setdefault(dim_key, []).append((dim_val, source))

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

        # Resolve each scalar field: agree → use it; disagree → majority
        # vote, with ties broken by trusted-source rank + log.
        for field, values in candidates.items():
            if not values:
                continue
            distinct = {v for v, _ in values}
            if len(distinct) == 1:
                merged[field] = values[0][0]
                continue

            winner, is_tie = self._resolve_conflict(values)
            merged[field] = winner
            logger.warning(
                "Conflicting '%s' values across scraped pages — likely "
                "different trims/variants matched the same search. Using "
                "%s value %r. All candidates: %s",
                field, "domain-rank tiebreak" if is_tie else "majority", winner, values,
            )

        # Same conflict-aware treatment for nested dimension fields.
        for dim_key, values in dimension_candidates.items():
            distinct = {v for v, _ in values}
            if len(distinct) == 1:
                merged["dimensions"][dim_key] = values[0][0]
                continue

            winner, is_tie = self._resolve_conflict(values)
            merged["dimensions"][dim_key] = winner
            logger.warning(
                "Conflicting dimension '%s' values across scraped pages. "
                "Using %s value %r. All candidates: %s",
                dim_key, "domain-rank tiebreak" if is_tie else "majority", winner, values,
            )

        return merged

    @staticmethod
    def _resolve_conflict(values: list[tuple[str, str]]) -> tuple[str, bool]:
        """
        Pick a winning value from disagreeing (value, source_url) candidates.

        - If one value has strictly more votes than any other, it wins —
          a genuine majority.
        - Otherwise (including the common case where every page gives a
          DIFFERENT value, so every value is tied at count=1), the old
          code fell through to Counter.most_common()'s tie-break, which
          is Python's stable insertion order — i.e. whichever page
          happened to be scraped/listed first. That's not a real signal
          of correctness, just an accident of iteration order. Instead,
          break ties using the same trusted-domain ranking already used
          to prioritize which URLs to scrape in the first place, so the
          choice is explainable and consistent regardless of scrape order.

        Returns
        -------
        (winning_value, was_tie) — was_tie is True when the winner was
        picked by domain rank rather than a genuine vote majority, so
        callers can log which kind of resolution happened.
        """
        counts = Counter(v for v, _ in values)
        top_count = max(counts.values())
        tied_values = [v for v in counts if counts[v] == top_count]

        if len(tied_values) == 1:
            return tied_values[0], False

        # Genuine tie: rank each tied value by the best (lowest-rank)
        # source that proposed it, and take the most-trusted one.
        best_rank_for_value: dict[str, int] = {}
        for value, source in values:
            if value not in tied_values:
                continue
            rank = preferred_domain_rank(source)
            if value not in best_rank_for_value or rank < best_rank_for_value[value]:
                best_rank_for_value[value] = rank

        winner = min(tied_values, key=lambda v: best_rank_for_value.get(v, 999))
        return winner, True