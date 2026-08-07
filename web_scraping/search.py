"""
Google Search Handler — Vehicle Specs Focused

Builds targeted search queries for specific vehicle specs pages
and filters out non-automotive results.

Supports two modes:
  1. search_vehicle()       — specific make + model + year
  2. search_brand_overview() — brand only (e.g. "BMW") → lineup overview
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Fix: web_scraping/requests.py shadows the real `requests` library.
# Import the real library by temporarily hiding the local file from sys.path.
_ws_dir = str(Path(__file__).resolve().parent)
_cleaned = [p for p in sys.path if p != _ws_dir]
_orig_path = sys.path[:]
sys.path = _cleaned
import requests as requests  # noqa: E402  — real pip requests
sys.path = _orig_path        # restore

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

# Domains trusted specifically for pricing data
PRICE_DOMAINS = [
    "kbb.com",           # Kelley Blue Book — market average
    "edmunds.com",       # True Market Value
    "autotrader.com",    # dealer listings
    "cars.com",          # dealer + private listings
    "caranddriver.com",  # MSRP
    "motortrend.com",    # MSRP + pricing
    "cargurus.com",      # market analysis
    "truecar.com",       # dealer pricing
    "carmax.com",        # used pricing
]

BLOCKED_DOMAINS = {
    "facebook.com", "instagram.com", "tiktok.com", "youtube.com",
    "twitter.com", "pinterest.com", "reddit.com", "tumblr.com",
    "snapchat.com", "yelp.com", "tripadvisor.com",
}

# Wikipedia's vehicle articles cover an entire nameplate's full production
# run (often 10-20 years, every trim and engine option) in one flattened
# infobox. For a TRIM-SPECIFIC spec search (make+model+year all given),
# treating its infobox as one equally-weighted candidate against a
# dedicated trim review causes exactly the kind of field-level conflicts
# (engine, horsepower, fuel_type, drive all wrong) that merge_pages() has
# to vote on. Excluded from PREFERRED_DOMAINS lookups used for trim-level
# spec queries; still fine for search_brand_overview(), where a lineup
# summary is actually what's wanted.
TRIM_SPEC_EXCLUDED_DOMAINS = {"wikipedia.org"}


def preferred_domain_rank(url: str) -> int:
    """
    Rank a source URL by trust for spec data — lower is more trusted.

    Used by json_builder.merge_pages() to break ties deterministically
    when multiple scraped pages disagree on a field's value and no
    single value has a clear majority. Without this, Python's
    Counter.most_common() breaks ties by insertion order, which
    silently depends on whichever page happened to be scraped first —
    not on which source is actually more reliable.
    """
    for i, domain in enumerate(PREFERRED_DOMAINS):
        if domain in url:
            return i
    return len(PREFERRED_DOMAINS)


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

        # This is a trim-specific query (real model given, not a brand
        # overview) — drop multi-decade nameplate sources like Wikipedia
        # that flatten every trim/year into one infobox and are prone to
        # yielding wrong values for a single specific trim/year.
        is_trim_specific = bool(model and model.strip().lower() not in ("", "unknown"))
        if is_trim_specific:
            results = [
                r for r in results
                if not any(d in r["link"] for d in TRIM_SPEC_EXCLUDED_DOMAINS)
            ]

        results.sort(key=lambda r: preferred_domain_rank(r["link"]))
        urls = [r["link"] for r in results if r["link"]][:num_results]

        logger.info(
            "Found %d URLs for %s %s %s.",
            len(urls), year or "", make, model,
        )
        return urls

    # ----------------------------------------------------------
    # Search Vehicle Price — returns URLs + price snippets
    # ----------------------------------------------------------

    def search_vehicle_price(
        self,
        make: str,
        model: str,
        year: Optional[str] = None,
        num_results: int = 6,
    ) -> list[dict[str, Any]]:
        """
        Search specifically for current vehicle pricing data.

        Returns a list of dicts with:
            - link: str
            - title: str
            - snippet: str   (may contain price info)
            - domain: str
            - is_price_domain: bool

        Results are sorted: trusted price domains first.
        """
        base = f"{year} {make} {model}".strip() if year else f"{make} {model}".strip()

        queries = [
            f"{base} price MSRP",
            f"{base} used price",
            f"{base} average market price",
        ]

        seen_links: set[str] = set()
        results: list[dict[str, Any]] = []

        for query in queries:
            for item in self.search(query, num_results=4):
                link = item.get("link", "")
                if not link or link in seen_links:
                    continue
                if any(d in link for d in BLOCKED_DOMAINS):
                    continue
                seen_links.add(link)
                domain = link.split("/")[2] if "//" in link else link
                results.append({
                    "link":            link,
                    "title":           item.get("title", ""),
                    "snippet":         item.get("snippet", ""),
                    "domain":          domain,
                    "is_price_domain": any(pd in domain for pd in PRICE_DOMAINS),
                })

        # Sort: price-trusted domains first, then by PRICE_DOMAINS order
        def _rank(r: dict) -> int:
            domain = r["domain"]
            for i, pd in enumerate(PRICE_DOMAINS):
                if pd in domain:
                    return i
            return len(PRICE_DOMAINS)

        results.sort(key=_rank)
        logger.info(
            "Price search for '%s %s %s' → %d results (%d from price domains).",
            year or "", make, model, len(results),
            sum(1 for r in results if r["is_price_domain"]),
        )
        return results[:num_results]

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

        # Sort by preferred domains (Wikipedia is fine here — a lineup
        # overview across trims/years is exactly what it's good at).
        all_results.sort(key=lambda r: preferred_domain_rank(r["link"]))
        urls = [r["link"] for r in all_results][:num_results]

        logger.info(
            "Brand overview for '%s' → %d URLs.", make, len(urls)
        )
        return urls