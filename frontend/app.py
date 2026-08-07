import textwrap
from pathlib import Path

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from components.cards import stat_card, feature_card

st.set_page_config(
    page_title="Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css()
render_navbar(active="nav_home")

APP_DIR = Path(__file__).parent
IMG_DIR = APP_DIR / "img"

# ── Hero ──────────────────────────────────────────────────────────────────
hero_left, hero_right = st.columns([0.9, 1.1], gap="medium")

with hero_left:
    st.markdown(
        textwrap.dedent(f"""\
        <div class="hero-badge">✨ {t("hero_badge")}</div>
        <div class="hero-title">
            {t("hero_title_1")}<br><span>{t("hero_title_2")}</span>
        </div>
        <div class="hero-description">{t("hero_subtitle")}</div>
        """),
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🚗 " + t("start_detection"), type="primary", use_container_width=True):
            st.switch_page("pages/1_Detect.py")
    with c2:
        if st.button(t("learn_more"), use_container_width=True):
            st.switch_page("pages/5_Features.py")
    with c3:
        if st.button("👥 " + t("nav_developers"), use_container_width=True):
            st.switch_page("pages/6_Developers.py")

    st.markdown(
        textwrap.dedent("""\
        <div class="hero-users">
            <div class="hero-users-number">
                <strong>20+</strong><br>
                <span>Happy Users</span>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

with hero_right:
    st.markdown('<div class="hero-image">', unsafe_allow_html=True)
    st.image(str(IMG_DIR / "page_1.png"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── How it works ─────────────────────────────────────────────────────────
st.markdown(f"### {t('how_it_works')}")
c1, c2, c3, c4 = st.columns(4)
with c1:
    feature_card(t("feat_detect_title"), t("feat_detect_desc"))
with c2:
    feature_card(t("feat_process_title"), t("feat_process_desc"))
with c3:
    feature_card(t("feat_extract_title"), t("feat_extract_desc"))
with c4:
    feature_card(t("feat_results_title"), t("feat_results_desc"))

st.write("")

# ── Stats ─────────────────────────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)
with s1:
    stat_card("98%+", t("stat_accuracy"))
with s2:
    stat_card("100K+", t("stat_images"))
with s3:
    stat_card("100%", t("stat_ai_powered"))
with s4:
    stat_card("24/7", t("stat_support"))