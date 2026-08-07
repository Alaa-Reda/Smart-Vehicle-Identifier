"""
Top navigation bar.

IMPORTANT STREAMLIT LIMITATION (this is what was broken before):
Every st.markdown(), st.button(), st.columns(), etc. call renders as its
own top-level DOM node ("element-container"). Opening an HTML tag like
<div class="vv-navbar"> in one st.markdown() call and only closing it in a
*later*, separate call does NOT nest the widgets rendered in between —
the browser auto-closes the dangling <div> right after that one fragment
is parsed. So the old code's logo <div> and the "</div>" written after
the buttons were never actually wrapping anything: the logo sat in its
own little box, and the nav/lang/theme buttons rendered as bare, unstyled
native Streamlit buttons underneath — which is exactly the broken look
in the screenshot.

Fix: put the logo AND all the nav/lang/theme buttons inside the *same*
st.columns(...) call, so they are genuine siblings inside one real
Streamlit "row" (div[data-testid="stHorizontalBlock"]). Then style that
whole row from the outside using a CSS marker + adjacent-sibling rule
(see the ".vv-navbar-marker + div[data-testid='stHorizontalBlock']"
block in assets/css/theme.css) instead of relying on hand-written HTML
tags to wrap real widgets, which never works in Streamlit.

Call render_navbar(active="nav_home") at the top of every page.
"""

import streamlit as st
import streamlit.components.v1 as components
from utils.theme import toggle_theme
from utils.i18n import t, toggle_lang

NAV_ITEMS = [
    ("nav_home", "app.py"),
    ("nav_detect", "pages/1_Detect.py"),
    ("nav_chat", "pages/4_Chat.py"),
    ("nav_features", "pages/5_Features.py"),
    ("nav_developers", "pages/6_Developers.py"),
    ("nav_history", "pages/10_History.py"),
    ("nav_about", "pages/9_About.py"),
]


def render_navbar(active: str = "nav_home") -> None:
    st.markdown('<div class="vv-navbar-wrap" id="vv-navbar-wrap">', unsafe_allow_html=True)

    # This marker is the hook the CSS uses to find *only* this row of
    # columns (see theme.css). It must sit immediately before the
    # st.columns() call below — nothing else in between.
    st.markdown('<span class="vv-navbar-marker"></span>', unsafe_allow_html=True)

    # logo | 7 nav links | lang toggle | theme toggle
    cols = st.columns([1.6] + [1] * len(NAV_ITEMS) + [0.55, 0.55], gap="small")

    with cols[0]:
        st.markdown(
            f"""<div class="vv-logo">
<div class="vv-logo-icon">🚗</div>
<div class="vv-logo-text">
<div class="vv-logo-title">{t('brand_name')}</div>
<div class="vv-logo-subtitle">{t('brand_suffix')}</div>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    for i, (key, target) in enumerate(NAV_ITEMS):
        with cols[i + 1]:
            label = t(key)
            if key == active:
                st.markdown(f'<div class="vv-nav-active">{label}</div>', unsafe_allow_html=True)
            else:
                if st.button(label, key=f"nav_{key}", use_container_width=True):
                    st.switch_page(target)

    with cols[-2]:
        lang_label = "AR" if st.session_state.get("lang", "en") == "en" else "EN"
        if st.button(lang_label, key="nav_lang_toggle", use_container_width=True):
            toggle_lang()
            st.rerun()

    with cols[-1]:
        # Icon-only toggle (language-agnostic): shows the mode you'll
        # switch *to*, same convention as the mockup's moon icon.
        theme_icon = "🌙" if st.session_state.get("theme", "light") == "light" else "☀️"
        if st.button(theme_icon, key="nav_theme_toggle", use_container_width=True):
            toggle_theme()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Scroll-driven show/hide behaviour, executed inside a real iframe so
    # the <script> actually runs (see utils/theme.py for why).
    components.html(
        """
        <script>
            (function() {
                const doc = window.parent.document;
                if (doc.__vvNavScrollBound) { return; }
                doc.__vvNavScrollBound = true;

                const candidates = [
                    doc.querySelector('[data-testid="stAppViewContainer"]'),
                    doc.querySelector('section.main'),
                    doc.defaultView,
                ].filter(Boolean);

                let lastY = 0;

                function getY(el) {
                    return el === doc.defaultView ? (el.scrollY || 0) : (el.scrollTop || 0);
                }

                candidates.forEach(function(el) {
                    el.addEventListener('scroll', function() {
                        const wrap = doc.getElementById('vv-navbar-wrap');
                        if (!wrap) { return; }
                        const currentY = getY(el);

                        if (currentY > lastY && currentY > 80) {
                            wrap.classList.add('vv-nav-hidden');
                        } else {
                            wrap.classList.remove('vv-nav-hidden');
                        }
                        lastY = currentY;
                    }, { passive: true });
                });
            })();
        </script>
        """,
        height=0,
        width=0,
    )