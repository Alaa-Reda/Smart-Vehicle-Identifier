"""
===========================================================
Smart Vehicle Identifier
Home Page
===========================================================

Landing page for the application.

Responsibilities
----------------
- Welcome screen
- Quick statistics
- Image upload shortcut
- Quick actions
- Backend status

Contains no business logic.
"""

from __future__ import annotations

import streamlit as st

from api.vehicle_api import vehicle_api
from components.stat_card import StatCard, render_grid
from components.upload_zone import render as render_upload
from utils.html import render_html
from utils.session import navigate


# ==========================================================
# Helpers
# ==========================================================

def _backend_status() -> tuple[str, str]:
    """
    Returns
    -------
    (label, status)
    """

    if vehicle_api.health():
        return "Backend Online", "success"

    return "Backend Offline", "danger"


# ==========================================================
# Hero
# ==========================================================

def _hero() -> None:
    """Render the hero section."""

    render_html(
        """
        <div class="svi-card svi-hero">
            <h1>🚘 Smart Vehicle Identifier</h1>
            <p>
                Analyze vehicle images, identify the make and model,
                compare vehicles, and interact with an AI assistant
                powered by Vision-Language Models.
            </p>
        </div>
        """
    )


# ==========================================================
# Statistics
# ==========================================================

def _statistics() -> None:
    """Render dashboard statistics."""

    status_label, status = _backend_status()

    cards = [

        StatCard(
            title="AI Models",
            value="2",
            icon="🤖",
            subtitle="ConvNeXt + Qwen3-VL",
        ),

        StatCard(
            title="Backend",
            value=status_label,
            icon="🖥",
            subtitle="FastAPI Service",
            status=status,
        ),

        StatCard(
            title="Supported Formats",
            value="PNG / JPG",
            icon="🖼",
            subtitle="Vehicle Images",
        ),

        StatCard(
            title="Inference",
            value="< 1 sec",
            icon="⚡",
            subtitle="Average Response",
        ),
    ]

    render_grid(cards, columns=4)


# ==========================================================
# Upload Section
# ==========================================================

def _upload() -> None:
    """Render upload section."""

    image = render_upload()

    if image is not None:

        st.success(
            "Image uploaded successfully. "
            "Open the Analysis page to start inference."
        )


# ==========================================================
# Quick Actions
# ==========================================================

def _quick_actions() -> None:
    """Render quick action buttons."""

    st.markdown("## Quick Actions")

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "🚗 Vehicle Analysis",
            use_container_width=True,
            key="home_analysis",
        ):
            navigate("Analysis")
            st.rerun()

    with c2:

        if st.button(
            "🤖 AI Assistant",
            use_container_width=True,
            key="home_chat",
        ):
            navigate("Chat")
            st.rerun()

    with c3:

        if st.button(
            "📊 Dashboard",
            use_container_width=True,
            key="home_dashboard",
        ):
            navigate("Dashboard")
            st.rerun()


# ==========================================================
# Public Page
# ==========================================================

def render() -> None:
    """
    Render the Home page.
    """

    _hero()

    st.write("")

    _statistics()

    st.write("")

    _upload()

    st.write("")

    _quick_actions()
