"""
===========================================================
Smart Vehicle Identifier
Component: Navigation
===========================================================

Professional navigation system for the application.

Responsibilities
----------------
- Sidebar navigation
- Active page highlighting
- Logo section
- AI status indicator
- User information
- Navigation callbacks
- Session synchronization

This component contains NO business logic.
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from utils.html import render_html
from utils.session import get, navigate


# ===========================================================
# Navigation Item
# ===========================================================

@dataclass(frozen=True, slots=True)
class NavigationItem:
    title: str
    icon: str
    page: str
    description: str = ""


# ===========================================================
# Navigation Definition
# ===========================================================

# أضف الصفحات الجديدة هنا بعد تنفيذها فعليًا
NAV_ITEMS: tuple[NavigationItem, ...] = (
    NavigationItem(
        title="Home",
        icon="🏠",
        page="Home",
        description="Application overview",
    ),
    NavigationItem(
        title="Vehicle Analysis",
        icon="🚗",
        page="Analysis",
        description="Analyze vehicle images",
    ),
    NavigationItem(
        title="AI Assistant",
        icon="🤖",
        page="Chat",
        description="Chat with the vehicle assistant",
    ),
)


# ===========================================================
# Logo
# ===========================================================

def render_logo() -> None:
    """Render application logo."""

    render_html(
        """
        <div class="svi-navbar">
            <div class="svi-navbar-logo">
                <div class="svi-navbar-icon">🚘</div>
                <div>
                    <div class="svi-navbar-title">Smart Vehicle Identifier</div>
                    <div class="svi-navbar-subtitle">AI Vehicle Intelligence Platform</div>
                </div>
            </div>
            <div class="svi-navbar-status">
                <span class="svi-status-dot"></span>
                AI Online
            </div>
        </div>
        """
    )


# ===========================================================
# User Card
# ===========================================================

def render_user_card() -> None:
    """Render user information."""

    st.markdown("### 👤 User")

    render_html(
        """
        <div class="svi-card">
            <h3 style="margin-bottom:10px;">Guest</h3>
            <p>Local Session</p>
        </div>
        """
    )


# ===========================================================
# Sidebar
# ===========================================================

def render_sidebar() -> None:
    """Render sidebar."""

    current_page = get("current_page", "Home")

    with st.sidebar:

        st.markdown("# 🚘")
        st.markdown("## Smart Vehicle")
        st.caption("AI Powered")

        st.divider()

        for item in NAV_ITEMS:

            clicked = st.button(
                f"{item.icon} {item.title}",
                key=f"sidebar_{item.page}",
                use_container_width=True,
                type="primary" if current_page == item.page else "secondary",
            )

            if clicked and current_page != item.page:
                navigate(item.page)
                st.rerun()

        st.divider()

        render_user_card()

        st.divider()

        st.caption("Version 1.0.0")


# ===========================================================
# Public API
# ===========================================================

def render() -> None:
    """Render navigation."""

    render_sidebar()
    render_logo()


# ===========================================================
# Helpers
# ===========================================================

def available_pages() -> list[str]:
    """Return page names."""

    return [item.page for item in NAV_ITEMS]


def find_page(page: str) -> NavigationItem | None:
    """Find page."""

    return next((item for item in NAV_ITEMS if item.page == page), None)
