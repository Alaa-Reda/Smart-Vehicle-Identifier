"""
===========================================================
Smart Vehicle Identifier
Component: Statistic Card
===========================================================

Reusable premium statistic card.

Examples
--------
✓ Total Analyses
✓ Accuracy
✓ Active Models
✓ API Latency
✓ Images Processed
✓ Confidence Score
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import streamlit as st

from utils.html import render_html


# ==========================================================
# Data Model
# ==========================================================

@dataclass(frozen=True, slots=True)
class StatCard:
    """Statistic card model."""

    title: str
    value: str | int | float

    icon: str = "📊"
    subtitle: str = ""

    delta: str | None = None

    status: Literal[
        "success",
        "warning",
        "danger",
        "info",
    ] = "info"

    help: str | None = None


# ==========================================================
# Status Mapping
# ==========================================================

_STATUS_CLASS = {
    "success": "svi-success",
    "warning": "svi-warning",
    "danger": "svi-danger",
    "info": "svi-info",
}


# ==========================================================
# Render
# ==========================================================

def render(card: StatCard) -> None:
    """Render a premium statistic card."""

    badge = ""

    if card.delta:
        badge = (
            f'<span class="svi-badge {_STATUS_CLASS[card.status]}">'
            f"{card.delta}</span>"
        )

    render_html(
        f"""
        <div class="svi-card svi-hover-rise">
            <div class="svi-space-between">
                <div>
                    <div style="font-size:15px;color:var(--text-muted);margin-bottom:10px;">
                        {card.title}
                    </div>
                    <div class="svi-metric-value">{card.value}</div>
                    <div style="margin-top:10px;color:var(--text-secondary);">
                        {card.subtitle}
                    </div>
                </div>
                <div style="font-size:42px;">{card.icon}</div>
            </div>
            <div style="margin-top:18px;">{badge}</div>
        </div>
        """
    )


# ==========================================================
# Grid Renderer
# ==========================================================

def render_grid(
    cards: list[StatCard],
    columns: int = 4,
) -> None:
    """Render multiple statistic cards."""

    if not cards:
        return

    columns = max(1, min(columns, len(cards)))

    cols = st.columns(columns)

    for index, card in enumerate(cards):
        with cols[index % columns]:
            render(card)
