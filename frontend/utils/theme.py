"""
=======================

Theme configuration utilities.

This module is responsible for configuring the visual identity of the
Smart Vehicle Identifier frontend.

It injects global CSS variables into the application while keeping the
actual component styling inside external CSS files.

Responsibilities
----------------
- Inject design tokens
- Configure global fonts
- Configure color variables
- Configure spacing variables
- Configure border radius variables
- Prepare CSS variables for the styling layer

Author
------
Smart Vehicle Identifier Team
"""

from __future__ import annotations

from functools import lru_cache

import streamlit as st
from config.settings import settings


@lru_cache(maxsize=1)
def _css_variables() -> str:
    """
    Build the global CSS variable block.

    Returns
    -------
    str
        CSS variables used throughout the application.
    """

    return f"""
<style>

:root {{

    /* -------------------------------------------------- */
    /* Brand Colors                                        */
    /* -------------------------------------------------- */

    --color-primary: {settings.PRIMARY_COLOR};
    --color-secondary: {settings.SECONDARY_COLOR};
    --color-accent: {settings.ACCENT_COLOR};

    --color-success: {settings.SUCCESS_COLOR};
    --color-warning: {settings.WARNING_COLOR};
    --color-danger: {settings.ERROR_COLOR};

    /* -------------------------------------------------- */
    /* Backgrounds                                         */
    /* -------------------------------------------------- */

    --background: {settings.BACKGROUND};
    --surface: {settings.SURFACE};
    --card: {settings.CARD};

    /* -------------------------------------------------- */
    /* Typography                                          */
    /* -------------------------------------------------- */

    --text-primary: #FFFFFF;
    --text-secondary: #D1D5DB;
    --text-muted: #9CA3AF;

    /* -------------------------------------------------- */
    /* Radius                                              */
    /* -------------------------------------------------- */

    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 24px;
    --radius-xl: 32px;

    /* -------------------------------------------------- */
    /* Spacing                                             */
    /* -------------------------------------------------- */

    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 24px;
    --space-6: 32px;
    --space-7: 48px;
    --space-8: 64px;

    /* -------------------------------------------------- */
    /* Shadows                                             */
    /* -------------------------------------------------- */

    --shadow-sm: 0 2px 8px rgba(0,0,0,.20);
    --shadow-md: 0 8px 24px rgba(0,0,0,.25);
    --shadow-lg: 0 20px 60px rgba(0,0,0,.35);
    --shadow-glow: 0 0 30px rgba(37,99,235,.30);

}}

html,
body,
[class*="css"] {{
    font-family:
        "Inter",
        "Segoe UI",
        sans-serif;
}}

</style>
"""


@lru_cache(maxsize=1)
def _font_import() -> str:
    """
    Return Google Font import.
    """

    return """
<link rel="preconnect" href="https://fonts.googleapis.com">

<link rel="preconnect"
href="https://fonts.gstatic.com"
crossorigin>

<link href="https://fonts.googleapis.com/css2?
family=Inter:wght@300;400;500;600;700;800&
display=swap"
rel="stylesheet">
"""


def configure_theme() -> None:
    """
    Configure the global application theme.

    This function is intentionally lightweight and may be safely called
    multiple times.
    """

    st.markdown(
        _font_import(),
        unsafe_allow_html=True,
    )

    st.markdown(
        _css_variables(),
        unsafe_allow_html=True,
    )