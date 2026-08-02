r"""
===========================================================

Global asset loader for the Smart Vehicle Identifier frontend.

Responsibilities
----------------
- Load external CSS files
- Load external JavaScript files
- Inject HTML snippets
- Cache static assets
- Fail gracefully if assets are unavailable

This module intentionally contains no styling rules.
All CSS should live inside the assets directory.

Author
------
Smart Vehicle Identifier Team
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import streamlit as st

from config.settings import CSS_DIR, JS_DIR


# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------


@lru_cache(maxsize=None)
def _read_text_file(path: Path) -> str:
    """
    Read a UTF-8 text file.

    Parameters
    ----------
    path:
        Path to the asset.

    Returns
    -------
    str
        File contents.
    """

    return path.read_text(encoding="utf-8")


def _inject_css(css: str) -> None:
    """
    Inject CSS into the application.
    """

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def _inject_javascript(js: str) -> None:
    """
    Inject JavaScript into the page.
    """

    st.components.v1.html(
        f"""
<script>
{js}
</script>
""",
        height=0,
        width=0,
    )


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def load_css(filename: str) -> None:
    """
    Load a stylesheet from assets/css.
    """

    path = CSS_DIR / filename

    try:
        _inject_css(_read_text_file(path))

    except FileNotFoundError:
        st.warning(f"Missing stylesheet: {filename}")

    except Exception as exc:
        st.error(f"Failed to load stylesheet '{filename}': {exc}")


def load_javascript(filename: str) -> None:
    """
    Load a JavaScript file from assets/js.
    """

    path = JS_DIR / filename

    try:
        _inject_javascript(_read_text_file(path))

    except FileNotFoundError:
        pass

    except Exception as exc:
        st.error(f"Failed to load JavaScript '{filename}': {exc}")


def load_global_assets() -> None:
    """
    Load all global frontend assets.
    """

    css_files = (
        "theme.css",
    )

    for stylesheet in css_files:
        load_css(stylesheet)

    load_javascript("app.js")