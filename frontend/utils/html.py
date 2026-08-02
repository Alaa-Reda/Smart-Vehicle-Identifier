"""
===========================================================
Smart Vehicle Identifier
HTML Rendering Helper
===========================================================

Streamlit's markdown renderer follows CommonMark rules. When a
raw HTML snippet contains blank lines and indentation (used for
readability in the source), Markdown can split it into separate
blocks and treat the indented lines as a literal code block
instead of HTML - causing tags to appear as raw text on the page.

This module normalizes HTML strings (removes blank lines and
per-line indentation) before rendering, so nested <div> markup
always renders correctly regardless of how it was formatted in
the source.
"""

from __future__ import annotations

import streamlit as st


def clean_html(html: str) -> str:
    """
    Strip blank lines and leading whitespace from every line.

    This keeps the HTML structure but removes the formatting
    that Streamlit's Markdown parser misreads as an indented
    code block.
    """

    lines = [line.strip() for line in html.strip().splitlines()]

    return "\n".join(line for line in lines if line)


def render_html(html: str) -> None:
    """Render a raw HTML snippet safely."""

    st.markdown(clean_html(html), unsafe_allow_html=True)
