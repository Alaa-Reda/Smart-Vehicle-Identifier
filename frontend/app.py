"""
Smart Vehicle Identifier
========================

Application Entry Point

This module is the composition root of the frontend.

Responsibilities
----------------
- Configure Streamlit
- Bootstrap application
- Initialize session state
- Load theme
- Load global CSS / JavaScript
- Initialize navigation
- Render the active page
- Handle fatal startup errors

The application intentionally contains almost no business logic.
All functionality is delegated to dedicated modules.

Author:
    Smart Vehicle Identifier Team

License:
    MIT
"""

from __future__ import annotations

import logging

import streamlit as st

from config.settings import settings
from utils.css import load_global_assets
from utils.session import initialize_session
from utils.theme import configure_theme

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Streamlit Configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state=settings.SIDEBAR_STATE,
)

# ---------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------


def bootstrap() -> None:
    """
    Initialize application requirements before rendering pages.
    """

    configure_theme()

    initialize_session()

    try:
        load_global_assets()
    except Exception:
        LOGGER.exception("Failed to load global assets")


# ---------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------


def main() -> None:
    """
    Main application entry point.
    """

    bootstrap()

    # Lazy imports to avoid circular imports
    from components.navigation import render as render_navigation
    from utils.navigation import current_page

    render_navigation()

    page = current_page()

    if page is None:
        st.error("No page selected.")
        return

    page.renderer()


# ---------------------------------------------------------------------
# Error Boundary
# ---------------------------------------------------------------------

try:
    main()

except Exception:
    LOGGER.exception("Application startup failed")

    st.error(
        """
        ### 🚨 Application Startup Failed

        The frontend encountered an unexpected error during initialization.

        Please restart the application.

        If the issue persists, review the application logs.
        """
    )

    st.stop()