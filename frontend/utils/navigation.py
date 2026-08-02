"""
=====================================================

Central navigation manager for the Smart Vehicle Identifier frontend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from utils.session import get


# ==========================================================
# Page Definition
# ==========================================================

@dataclass(frozen=True, slots=True)
class Page:
    """
    Represents a navigable page.
    """

    title: str
    icon: str
    renderer: Callable[[], None]


# ==========================================================
# Helpers
# ==========================================================

def _pages() -> dict[str, Page]:
    """
    Build the page registry lazily to avoid circular imports.
    """

    from pages.analysis import render as render_analysis
    from pages.chat import render as render_chat
    from pages.home import render as render_home

    return {
        "Home": Page(
            title="Home",
            icon="🏠",
            renderer=render_home,
        ),
        "Analysis": Page(
            title="Vehicle Analysis",
            icon="🚗",
            renderer=render_analysis,
        ),
        "Chat": Page(
            title="AI Assistant",
            icon="🤖",
            renderer=render_chat,
        ),
    }


# ==========================================================
# Public API
# ==========================================================

def available_pages() -> dict[str, Page]:
    """
    Return all registered pages.
    """

    return _pages()


def current_page() -> Page:
    """
    Return the currently selected page.
    """

    pages = _pages()
    page_name = get("current_page", "Home")

    return pages.get(page_name, pages["Home"])


def render_navigation() -> None:
    """
    Render the current page.
    """

    current_page().renderer()