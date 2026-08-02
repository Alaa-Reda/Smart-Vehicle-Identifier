"""
HTML Parser

Parses raw HTML into structured sections using BeautifulSoup.
Removes scripts, styles, and navigation noise.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

# ==========================================================
# Tags to remove (noise)
# ==========================================================

REMOVE_TAGS = [
    "script", "style", "noscript", "iframe",
    "nav", "footer", "header", "aside",
    "form", "button", "input", "select",
    "svg", "canvas", "ads", "advertisement",
]


# ==========================================================
# Parser
# ==========================================================

class HTMLParser:
    """
    Parses raw HTML into structured content sections.
    """

    def __init__(self, html: str, url: str = "") -> None:

        self.url = url
        self._soup = BeautifulSoup(html, "html.parser")
        self._clean()

    # ----------------------------------------------------------
    # Cleaning
    # ----------------------------------------------------------

    def _clean(self) -> None:
        """Remove noise tags from the parsed tree."""

        for tag in self._soup(REMOVE_TAGS):
            tag.decompose()

    # ----------------------------------------------------------
    # Extraction
    # ----------------------------------------------------------

    def get_title(self) -> str:
        """Return page title."""

        tag = self._soup.find("title")
        return tag.get_text(strip=True) if tag else ""

    def get_headings(self) -> list[str]:
        """Return all h1–h3 heading texts."""

        headings = []
        for tag in self._soup.find_all(["h1", "h2", "h3"]):
            text = tag.get_text(strip=True)
            if text:
                headings.append(text)
        return headings

    def get_paragraphs(self) -> list[str]:
        """Return all paragraph texts."""

        paragraphs = []
        for tag in self._soup.find_all("p"):
            text = tag.get_text(strip=True)
            if len(text) > 30:  # Skip short/empty paragraphs
                paragraphs.append(text)
        return paragraphs

    def get_tables(self) -> list[dict[str, str]]:
        """
        Extract tables as list of key-value dicts.
        Useful for spec tables.
        """

        tables = []

        for table in self._soup.find_all("table"):
            data: dict[str, str] = {}

            for row in table.find_all("tr"):
                cells = row.find_all(["th", "td"])

                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        data[key] = value

            if data:
                tables.append(data)

        return tables

    def get_lists(self) -> list[list[str]]:
        """Extract all unordered/ordered lists."""

        result = []

        for ul in self._soup.find_all(["ul", "ol"]):
            items = [
                li.get_text(strip=True)
                for li in ul.find_all("li")
                if li.get_text(strip=True)
            ]
            if items:
                result.append(items)

        return result

    def get_meta_description(self) -> str:
        """Return meta description content."""

        tag = self._soup.find("meta", attrs={"name": "description"})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return ""

    def get_all_text(self) -> str:
        """Return all visible text from the page."""

        return self._soup.get_text(separator=" ", strip=True)

    # ----------------------------------------------------------
    # Full parse result
    # ----------------------------------------------------------

    def parse(self) -> dict[str, Any]:
        """
        Return all parsed sections as a single dict.

        Returns
        -------
        dict with keys:
            url, title, meta_description,
            headings, paragraphs, tables, lists, full_text
        """

        return {
            "url":              self.url,
            "title":            self.get_title(),
            "meta_description": self.get_meta_description(),
            "headings":         self.get_headings(),
            "paragraphs":       self.get_paragraphs(),
            "tables":           self.get_tables(),
            "lists":            self.get_lists(),
            "full_text":        self.get_all_text(),
        }