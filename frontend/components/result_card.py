"""
===========================================================
Smart Vehicle Identifier
Component: Result Card
===========================================================

Displays AI vehicle classification results.

Responsibilities
----------------
- Show prediction
- Show confidence
- Display metadata
- Display top predictions
- Export result
- Trigger comparison

No inference logic lives here.
"""

from __future__ import annotations

import json
from dataclasses import asdict

import streamlit as st

from models.vehicle import Prediction, VehicleResult
from utils.html import render_html


# ==========================================================
# Helpers
# ==========================================================

def _progress(value: float) -> None:
    """Render a normalized progress bar."""

    st.progress(
        max(0.0, min(value, 1.0))
    )


def _badge(confidence: float) -> str:
    """Return a confidence badge."""

    if confidence >= 0.95:
        return "🟢 Excellent"

    if confidence >= 0.85:
        return "🟢 High"

    if confidence >= 0.70:
        return "🟡 Medium"

    return "🔴 Low"


# ==========================================================
# Prediction Table
# ==========================================================

def _render_predictions(
    predictions: list[Prediction],
) -> None:
    """Render the prediction list."""

    if not predictions:
        return

    st.markdown("### Top Predictions")

    for item in predictions:

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(item.label)

        with col2:
            st.write(f"{item.confidence:.1%}")

        st.progress(item.confidence)


# ==========================================================
# Main Renderer
# ==========================================================

def render(result: VehicleResult) -> None:
    """Render the vehicle analysis result."""

    render_html(
        """
        <div class="svi-card">
            <h2>🚗 Analysis Result</h2>
        </div>
        """
    )

    left, right = st.columns([2, 1])

    with left:

        st.subheader(
            f"{result.make} {result.model}"
        )

        if result.year:
            st.caption(str(result.year))

        if result.description:
            st.write(result.description)

    with right:

        st.metric(
            "Confidence",
            f"{result.confidence:.2%}",
        )

        st.write(_badge(result.confidence))

        _progress(result.confidence)

    st.divider()

    _render_predictions(result.predictions)

    st.divider()

    export_json = json.dumps(
        asdict(result),
        indent=4,
        ensure_ascii=False,
    )

    c1, c2 = st.columns(2)

    with c1:

        st.download_button(
            "📥 Export JSON",
            data=export_json,
            file_name="vehicle_result.json",
            mime="application/json",
            use_container_width=True,
        )

    with c2:

        st.button(
            "⚖️ Compare Vehicle",
            use_container_width=True,
            key="compare_vehicle",
        )
