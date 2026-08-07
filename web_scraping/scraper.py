"""
Vehicle Scraper — Main Orchestrator

Coordinates the complete scraping pipeline and passes
image thumbnails from Google Lens to the final document.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Optional, Union

from PIL import Image

from .search import VehicleSearchClient
from .google_lens import GoogleLensClient
from .requests import HTTPClient
from .playwright import BrowserSession
from .parser import HTMLParser
from .extractor import VehicleExtractor
from .cleaner import DataCleaner
from .json_builder import VehicleDocumentBuilder

logger = logging.getLogger(__name__)
MAX_PAGES = 5

BLOCKED_DOMAINS = {
    "facebook.com", "instagram.com", "tiktok.com", "youtube.com",
    "twitter.com", "pinterest.com", "reddit.com", "tumblr.com",
}


class VehicleScraper:

    def __init__(
        self,
        use_selenium_for_all: bool = False,
        headless: bool = True,
        max_pages: int = MAX_PAGES,
    ) -> None:
        self._http    = HTTPClient()
        self._cleaner = DataCleaner()
        self._builder = VehicleDocumentBuilder()
        self._search  = VehicleSearchClient()
        self._lens    = GoogleLensClient()

        self.use_selenium_for_all = use_selenium_for_all
        self.headless  = headless
        self.max_pages = max_pages

    def _fetch(self, url: str) -> Optional[str]:
        html = self._http.get(url)
        needs_selenium = (
            self.use_selenium_for_all
            or html is None
            or len(html) < 3000
            or "<noscript>" in (html or "")
        )
        if needs_selenium:
            logger.info("Selenium fallback: %s", url)
            with BrowserSession(headless=self.headless) as browser:
                html = browser.get_page(url, scroll=True)
        return html

    def _process_url(
        self,
        url: str,
        make: str = "",
        model: str = "",
        year: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        # Each URL is isolated: a flaky site (connection reset, a crashed
        # Selenium/driver session, an unexpected page structure, etc.)
        # must only cost us that ONE source, not the whole batch. Before
        # this, an unhandled exception from _fetch()/parsing on a single
        # URL propagated all the way up through _process_urls() and
        # scrape_by_name(), throwing away every page that had already been
        # scraped successfully in the same run.
        try:
            html = self._fetch(url)
        except Exception as exc:
            logger.warning("Failed to fetch %s — skipping this source: %s", url, exc)
            return None

        if not html:
            return None

        try:
            parsed    = HTMLParser(html, url=url).parse()
            extractor = VehicleExtractor(parsed)

            # Reject pages that loaded/rendered fine but aren't actually
            # about the requested vehicle (bad Selenium fallback content,
            # redirect to an unrelated "latest review", stale search hit,
            # etc.) BEFORE trusting any of their extracted fields as
            # candidate values for this vehicle.
            if not extractor.is_relevant(make, model, year):
                logger.warning(
                    "Skipping %s — page content does not appear to be "
                    "about %s %s %s (relevance check failed).",
                    url, year or "", make, model,
                )
                return None

            extracted = extractor.extract()
            cleaned   = self._cleaner.clean(extracted)
        except Exception as exc:
            logger.warning("Failed to parse/extract %s — skipping this source: %s", url, exc)
            return None

        return cleaned if cleaned else None

    def _process_urls(
        self,
        urls: list[str],
        make: str = "",
        model: str = "",
        year: Optional[str] = None,
    ) -> tuple[dict[str, Any], list[str]]:
        pages:   list[dict[str, Any]] = []
        sources: list[str]            = []

        filtered = [
            u for u in urls
            if not any(d in u for d in BLOCKED_DOMAINS)
        ]

        for url in filtered[:self.max_pages]:
            result = self._process_url(url, make=make, model=model, year=year)
            if result:
                pages.append(result)
                sources.append(url)
                logger.info("Scraped: %s", url)

        if not pages:
            return {}, []

        return self._builder.merge_pages(pages), sources

    def scrape_by_name(
        self,
        make: str,
        model: str,
        year: Optional[str] = None,
        images: Optional[list[str]] = None,
    ) -> Optional[dict[str, Any]]:
        """Scrape vehicle info by make/model/year."""

        logger.info("Scraping by name: %s %s %s", year or "", make, model)
        urls = self._search.search_vehicle(make, model, year, num_results=self.max_pages)
        if not urls:
            return None

        merged, sources = self._process_urls(urls, make=make, model=model, year=year)
        if not merged:
            return None

        return self._builder.build(
            make=make,
            model=model,
            year=year,
            cleaned_data=merged,
            sources=sources,
            images=images or [],
        )

    def scrape_by_image(
        self,
        image: Union[str, Path, Image.Image],
    ) -> Optional[dict[str, Any]]:
        """Identify vehicle from image via Google Lens then scrape."""

        logger.info("Scraping by image via Google Lens...")
        lens_result = self._lens.get_vehicle_info(image)

        if not lens_result or not lens_result.get("urls"):
            logger.warning("Google Lens returned no results.")
            return None

        title      = lens_result.get("title", "") or ""
        thumbnails = lens_result.get("thumbnails", [])
        make, model, year = self._parse_title(title)

        # Combine Lens URLs + Search URLs
        lens_urls   = lens_result.get("urls", [])
        search_urls = self._search.search_vehicle(
            make or "Unknown",
            model or title or "Unknown",
            year,
            num_results=4,
        ) if make else []

        all_urls = list(dict.fromkeys(search_urls + lens_urls))
        merged, sources = self._process_urls(
            all_urls,
            make=make or "",
            model=model or title or "",
            year=year,
        )
        if not merged:
            return None

        return self._builder.build(
            make=make or "Unknown",
            model=model or title or "Unknown",
            year=year,
            cleaned_data=merged,
            sources=sources,
            images=thumbnails[:5],
        )

    @staticmethod
    def _parse_title(title: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        if not title:
            return None, None, None

        m = re.match(r"(\d{4})\s+([A-Za-z\-]+)\s+(.+)", title.strip())
        if m:
            return m.group(2), m.group(3), m.group(1)

        m = re.match(r"([A-Za-z\-]+)\s+(.+?)\s+(\d{4})", title.strip())
        if m:
            return m.group(1), m.group(2), m.group(3)

        parts = title.strip().split(" ", 1)
        if len(parts) == 2:
            return parts[0], parts[1], None

        return None, title, None

    # ----------------------------------------------------------
    # Public — Scrape Brand Overview (make only)
    # ----------------------------------------------------------

    def scrape_brand_overview(
        self,
        make: str,
        year: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Scrape general brand overview when no model/year given.

        Returns a document with general info about the brand lineup,
        available models, price ranges, and common specs.

        Parameters
        ----------
        make : str   e.g. "BMW"
        year : str   e.g. "2024" (optional)

        Returns
        -------
        dict | None
            MongoDB-ready brand overview document.
        """

        logger.info("Scraping brand overview: %s %s", year or "", make)

        urls = self._search.search_brand_overview(
            make=make,
            year=year,
            num_results=6,
        )

        if not urls:
            logger.warning("No URLs found for brand: %s", make)
            return None

        merged, sources = self._process_urls(urls, make=make, model="", year=year)

        if not merged:
            return None

        return self._builder.build(
            make=make,
            model="",          # No specific model
            year=year,
            cleaned_data=merged,
            sources=sources,
            images=[],
        )