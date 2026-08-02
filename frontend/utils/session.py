r"""
=========================

Centralized session state management for the Smart Vehicle Identifier frontend.

This module is the single source of truth for Streamlit session state.
It initializes all required keys and provides helper functions for
safe access and updates.

Responsibilities
----------------
- Initialize session state
- Store application state
- Manage chat history
- Manage vehicles mentioned during chat
- Manage current analysis
- Track navigation
- Reset session sections
- Provide typed helper functions

Author
------
Smart Vehicle Identifier Team
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import streamlit as st

from models.vehicle import VehicleResult


# ---------------------------------------------------------------------
# Default Session Values
# ---------------------------------------------------------------------

DEFAULT_SESSION: dict[str, Any] = {
    # Navigation
    "current_page": "Home",
    "previous_page": None,

    # Theme
    "theme": "dark",

    # Upload
    "uploaded_image": None,

    # Analysis
    "analysis_result": None,
    "analysis_status": "idle",
    "analysis_history": [],

    # Chat
    "chat_messages": [],
    "chat_context": None,
    "chat_vehicles": [],

    # Comparison
    "comparison_left": None,
    "comparison_right": None,
    "comparison_result": None,

    # Dashboard
    "dashboard_metrics": {},

    # UI
    "loading": False,
    "notifications": [],

    # Settings
    "api_connected": False,
    "model_ready": False,
}


# ---------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------

def initialize_session() -> None:
    """
    Initialize every required session variable.

    Safe to call multiple times.
    """

    for key, value in DEFAULT_SESSION.items():
        st.session_state.setdefault(key, deepcopy(value))


# ---------------------------------------------------------------------
# Generic Helpers
# ---------------------------------------------------------------------

def get(key: str, default: Any = None) -> Any:
    """Return a session value."""

    return st.session_state.get(key, default)


def set(key: str, value: Any) -> None:
    """Store a session value."""

    st.session_state[key] = value


def exists(key: str) -> bool:
    """Check whether a session key exists."""

    return key in st.session_state


# ---------------------------------------------------------------------
# Chat Helpers
# ---------------------------------------------------------------------

def add_chat_message(role: str, content: str) -> None:
    """Append a chat message."""

    st.session_state["chat_messages"].append(
        {
            "role": role,
            "content": content,
        }
    )


def clear_chat() -> None:
    """Remove all chat messages and any tracked vehicles."""

    st.session_state["chat_messages"] = []
    st.session_state["chat_context"] = None
    st.session_state["chat_vehicles"] = []


def add_chat_vehicle(vehicle: dict[str, Any]) -> None:
    """
    Track a vehicle mentioned during the chat conversation.

    Deduplicates by make + model so the same vehicle isn't
    listed twice for PDF export.
    """

    vehicles: list[dict[str, Any]] = st.session_state.get(
        "chat_vehicles", []
    )

    key = f"{vehicle.get('make', '')} {vehicle.get('model', '')}".strip().lower()

    if not key:
        return

    already_tracked = any(
        f"{item.get('make', '')} {item.get('model', '')}".strip().lower() == key
        for item in vehicles
    )

    if not already_tracked:
        vehicles.append(vehicle)

    st.session_state["chat_vehicles"] = vehicles


def get_chat_vehicles() -> list[dict[str, Any]]:
    """Return the vehicles mentioned so far in the chat conversation."""

    return st.session_state.get("chat_vehicles", [])


# ---------------------------------------------------------------------
# Analysis Helpers
# ---------------------------------------------------------------------

def set_analysis(result: VehicleResult) -> None:
    """Store the latest analysis result."""

    st.session_state["analysis_result"] = result
    st.session_state["analysis_status"] = "completed"


def clear_analysis() -> None:
    """Reset the current analysis."""

    st.session_state["analysis_result"] = None
    st.session_state["analysis_status"] = "idle"
    st.session_state["uploaded_image"] = None


# ---------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------

def navigate(page: str) -> None:
    """Change the active page."""

    st.session_state["previous_page"] = st.session_state["current_page"]
    st.session_state["current_page"] = page


# ---------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------

def push_notification(
    message: str,
    level: str = "info",
) -> None:
    """Add a notification."""

    st.session_state["notifications"].append(
        {
            "message": message,
            "level": level,
        }
    )


def clear_notifications() -> None:
    """Remove all notifications."""

    st.session_state["notifications"].clear()


# ---------------------------------------------------------------------
# Full Reset
# ---------------------------------------------------------------------

def reset_application() -> None:
    """
    Reset the frontend state.

    Useful for "New Analysis" actions.
    """

    st.session_state.clear()
    initialize_session()