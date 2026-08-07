"""Small presentational card components shared across pages."""

import textwrap

import streamlit as st


def stat_card(value: str, label: str) -> None:
    st.markdown(
        textwrap.dedent(f"""\
        <div class="vv-card vv-stat-card">
            <div class="vv-stat-value">{value}</div>
            <div class="vv-stat-label">{label}</div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def feature_card(title: str, description: str) -> None:
    st.markdown(
        textwrap.dedent(f"""\
        <div class="vv-card">
            <h4 style="margin-top:0;">{title}</h4>
            <p class="vv-text-secondary" style="margin-bottom:0;">{description}</p>
        </div>
        """),
        unsafe_allow_html=True,
    )


def confidence_badge(score: float) -> str:
    if score >= 60:
        cls = "vv-badge-success"
    elif score >= 30:
        cls = "vv-badge-warning"
    else:
        cls = "vv-badge-danger"
    return f'<span class="vv-badge {cls}">{score:.1f}% Confidence</span>'


def source_card(name: str, url: str, updated: str, reliability: str) -> None:
    st.markdown(
        textwrap.dedent(f"""\
        <div class="vv-card-flat" style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <strong>{name}</strong><br/>
                <span class="vv-text-secondary" style="font-size:0.82rem;">{url}</span>
            </div>
            <div style="text-align:right;">
                <span class="vv-badge vv-badge-primary">{reliability}</span><br/>
                <span class="vv-text-secondary" style="font-size:0.75rem;">Updated {updated}</span>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )