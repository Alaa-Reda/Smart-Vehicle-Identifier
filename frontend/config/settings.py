"""
===========================================================

Global application configuration.

This module centralizes all frontend configuration used throughout the
Smart Vehicle Identifier application.

Responsibilities
----------------
- Application metadata
- Backend configuration
- UI defaults
- Upload configuration
- Feature flags
- File system paths
- Environment variable loading

No other module should hardcode these values.

Author
------
Smart Vehicle Identifier Team
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------

BASE_DIR: Path = Path(__file__).resolve().parents[1]

ASSETS_DIR: Path = BASE_DIR / "assets"
CSS_DIR: Path = ASSETS_DIR / "css"
JS_DIR: Path = ASSETS_DIR / "js"
IMAGES_DIR: Path = ASSETS_DIR / "images"
ICONS_DIR: Path = ASSETS_DIR / "icons"
ANIMATIONS_DIR: Path = ASSETS_DIR / "animations"


# ---------------------------------------------------------------------
# Configuration Dataclass
# ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AppSettings:
    """
    Immutable application configuration.
    """

    # -------------------------------------------------------------
    # Application
    # -------------------------------------------------------------

    APP_NAME: str = "Smart Vehicle Identifier"
    APP_VERSION: str = "1.0.0"
    COMPANY: str = "Smart Vehicle Identifier"

    PAGE_ICON: str = "🚗"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "collapsed"

    # -------------------------------------------------------------
    # Backend
    # -------------------------------------------------------------

    API_BASE_URL: str = field(
        default_factory=lambda: os.getenv(
            "SVI_API_URL",
            "http://127.0.0.1:8000",
        )
    )

    REQUEST_TIMEOUT: int = 120

    # -------------------------------------------------------------
    # Upload
    # -------------------------------------------------------------

    MAX_UPLOAD_MB: int = 20

    SUPPORTED_IMAGE_TYPES: tuple[str, ...] = (
        "png",
        "jpg",
        "jpeg",
        "webp",
    )

    # -------------------------------------------------------------
    # Theme
    # -------------------------------------------------------------

    PRIMARY_COLOR: str = "#2563EB"
    SECONDARY_COLOR: str = "#60A5FA"
    ACCENT_COLOR: str = "#22D3EE"

    SUCCESS_COLOR: str = "#22C55E"
    WARNING_COLOR: str = "#F59E0B"
    ERROR_COLOR: str = "#EF4444"

    BACKGROUND: str = "#0B0F19"
    SURFACE: str = "#111827"
    CARD: str = "#1A2235"

    # -------------------------------------------------------------
    # Animation
    # -------------------------------------------------------------

    ENABLE_ANIMATIONS: bool = True
    ENABLE_PARTICLES: bool = True
    ENABLE_GLASS_EFFECT: bool = True

    # -------------------------------------------------------------
    # Feature Flags
    # -------------------------------------------------------------

    ENABLE_HISTORY: bool = True
    ENABLE_DASHBOARD: bool = True
    ENABLE_CHAT: bool = True
    ENABLE_COMPARISON: bool = True
    ENABLE_EXPORT: bool = True

    # -------------------------------------------------------------
    # Cache
    # -------------------------------------------------------------

    CACHE_TTL_SECONDS: int = 3600

    # -------------------------------------------------------------
    # Development
    # -------------------------------------------------------------

    DEBUG: bool = field(
        default_factory=lambda: os.getenv(
            "SVI_DEBUG",
            "false",
        ).lower() == "true"
    )

    LOG_LEVEL: str = field(
        default_factory=lambda: os.getenv(
            "SVI_LOG_LEVEL",
            "INFO",
        )
    )

    # -------------------------------------------------------------
    # Branding
    # -------------------------------------------------------------

    COPYRIGHT: str = (
        "© 2026 Smart Vehicle Identifier. All rights reserved."
    )


# ---------------------------------------------------------------------
# Export Singleton
# ---------------------------------------------------------------------

settings = AppSettings()