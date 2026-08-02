"""
===========================================================
Smart Vehicle Identifier
Analysis Page
===========================================================

Vehicle image analysis workflow.

Responsibilities
----------------
- Display uploaded image
- Trigger AI inference
- Show loading state
- Display classification result
- Save analysis to session

No backend implementation lives here.
"""

from __future__ import annotations

import streamlit as st

from components.result_card import render as render_result
from components.upload_zone import (
    current,
    render as render_upload,
)
from services.analysis_service import analysis_service
from utils.session import get, set


# ==========================================================
# Helpers
# ==========================================================

def _analyze(image):
    """Run AI analysis."""

    with st.spinner("Analyzing vehicle..."):
        return analysis_service.analyze(image.image)


# ==========================================================
# Public Page
# ==========================================================

def render() -> None:
    """Render the vehicle analysis page."""

    st.title("🚗 Vehicle Analysis")

    image = current()

    if image is None:

        st.info(
            "Upload a vehicle image to begin."
        )

        render_upload()
        return

    st.image(
        image.image,
        use_container_width=True,
    )

    st.write("")

    if st.button(
        "🚀 Analyze Vehicle",
        type="primary",
        use_container_width=True,
        key="analyze_vehicle",
    ):

        try:

            result = _analyze(image)

            set("analysis_result", result)

            st.success(
                "Analysis completed successfully."
            )

            render_result(result)

        except Exception as exc:

            st.error(
                f"Analysis failed: {exc}"
            )

            return

    previous = get("analysis_result")

    if previous is not None:

        st.write("")

        render_result(previous)