"""
Google Search Handler — Vehicle Specs Focused

Builds targeted search queries for specific vehicle specs pages
and filters out non-automotive results.

Supports two modes:
  1. search_vehicle()       — specific make + model + year
  2. search_brand_overview() — brand only (e.g. "BMW") → lineup overview
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

logger = logging.getLogger(__name__)

if not _ENV_PATH.exists():
    logger.warning(".env not found at expected path: %s", _ENV_PATH)

SERPAPI_KEY:     str = os.getenv("SERPAPI_KEY", "")
SEARCH_ENDPOINT      = "https://serpapi.com/search"

PREFERRED_DOMAINS = [
    "caranddriver.com",
    "motortrend.com",
    "edmunds.com",
    "cars.com",
    "kbb.com",
    "autotrader.com",
    "motorauthority.com",
    "roadandtrack.com",
    "carbuzz.com",
    "wikipedia.org",
]

BLOCKED_DOMAINS = {
    "facebook.com", "instagram.com", "tiktok.com", "youtube.com",
    "twitter.com", "pinterest.com", "reddit.com", "tumblr.com",
    "snapchat.com", "yelp.com", "tripadvisor.com",
}


class VehicleSearchClient:

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or SERPAPI_KEY
        if not self.api_key:
            raise ValueError(
                "SERPAPI_KEY not found. "
                "Get a free key from https://serpapi.com"
            )

    # ----------------------------------------------------------
    # Query Builder
    # ----------------------------------------------------------

    @staticmethod
    def build_query(
        make: str,
        model: str,
        year: Optional[str] = None,
        focus: str = "specs",
    ) -> str:
        """Build a specific search query for a vehicle."""

        if model and model.strip() and model.lower() not in ("", "unknown"):
            base = f"{year} {make} {model}".strip() if year else f"{make} {model}".strip()
        else:
            base = f"{year} {make}".strip() if year else make.strip()

        focus_map = {
            "specs":  f"{base} specs horsepower engine transmission",
            "review": f"{base} full review",
            "price":  f"{base} MSRP base price",
        }
        return focus_map.get(focus, f"{base} {focus}")

    # ----------------------------------------------------------
    # Core Search
    # ----------------------------------------------------------

    def search(
        self,
        query: str,
        num_results: int = 8,
    ) -> list[dict[str, Any]]:
        """Run Google search and return filtered result list."""

        params = {
            "engine":  "google",
            "q":       query,
            "num":     num_results,
            "hl":      "en",
            "gl":      "us",
            "api_key": self.api_key,
        }

        try:
            r = requests.get(SEARCH_ENDPOINT, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()

            results = []
            for item in data.get("organic_results", []):
                link = item.get("link", "")
                if any(d in link for d in BLOCKED_DOMAINS):
                    continue
                results.append({
                    "title":   item.get("title", ""),
                    "link":    link,
                    "snippet": item.get("snippet", ""),
                })

            logger.info("Search '%s' → %d results.", query, len(results))
            return results[:num_results]

        except requests.RequestException as e:
            logger.error("Search API error: %s", e)
            return []

    # ----------------------------------------------------------
    # Search by Vehicle Name (make + model + year)
    # ----------------------------------------------------------

    def search_vehicle(
        self,
        make: str,
        model: str,
        year: Optional[str] = None,
        num_results: int = 6,
    ) -> list[str]:
        """
        Search for a specific vehicle and return spec page URLs.
        Prefers trusted automotive sources.
        """

        query   = self.build_query(make, model, year, focus="specs")
        results = self.search(query, num_results=num_results * 2)

        def priority(r: dict) -> int:
            link = r["link"]
            for i, domain in enumerate(PREFERRED_DOMAINS):
                if domain in link:
                    return i
            return len(PREFERRED_DOMAINS)

        results.sort(key=priority)
        urls = [r["link"] for r in results if r["link"]][:num_results]

        logger.info(
            "Found %d URLs for %s %s %s.",
            len(urls), year or "", make, model,
        )
        return urls

    # ----------------------------------------------------------
    # Search Brand Overview (make only — no model/year)
    # ----------------------------------------------------------

    def search_brand_overview(
        self,
        make: str,
        year: Optional[str] = None,
        num_results: int = 6,
    ) -> list[str]:
        """
        Search for brand overview pages — full lineup, models, prices.

        Used when the user types only a brand name (e.g. "BMW")
        without specifying a model or year.

        Runs 3 different queries and combines unique results:
          - Full lineup with prices
          - All models specs comparison
          - Brand model range overview

        Returns
        -------
        list[str]
            Deduplicated URLs covering the full brand lineup.
        """

        base = f"{year} {make}" if year else make

        queries = [
            f"{base} full lineup all models prices",
            f"{base} complete model range specs comparison",
            f"{base} buyer's guide all trims overview",
        ]

        all_results: list[dict[str, Any]] = []
        seen_links:  set[str]             = set()

        for query in queries:
            for r in self.search(query, num_results=4):
                link = r["link"]
                if link and link not in seen_links:
                    seen_links.add(link)
                    all_results.append(r)

        # Sort by preferred domains
        def priority(r: dict) -> int:
            link = r["link"]
            for i, domain in enumerate(PREFERRED_DOMAINS):
                if domain in link:
                    return i
            return len(PREFERRED_DOMAINS)

        all_results.sort(key=priority)
        urls = [r["link"] for r in all_results][:num_results]

        logger.info(
            "Brand overview for '%s' → %d URLs.", make, len(urls)
        )
        return urls