"""
===========================================================
Vehicle Scraper — Streamlit Test UI
===========================================================

Run:
    streamlit run streamlit_test.py
"""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

# ----------------------------------------------------------
# Project root
# ----------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ----------------------------------------------------------
# Page config — must be first Streamlit call
# ----------------------------------------------------------
st.set_page_config(
    page_title="Vehicle Scraper",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------
# CSS — dark automotive theme
# ----------------------------------------------------------
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {
    --bg:        #0d0f14;
    --surface:   #151821;
    --border:    #252a38;
    --accent:    #3b82f6;
    --accent-lo: #1e3a5f;
    --green:     #22c55e;
    --red:       #ef4444;
    --amber:     #f59e0b;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --mono:      'JetBrains Mono', monospace;
  }

  html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
  }

  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stSidebar"] { background: var(--surface) !important; }

  /* Hide Streamlit branding */
  #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

  /* ---- Hero ---- */
  .hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
  }
  .hero h1 {
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text);
    margin: 0;
  }
  .hero h1 span { color: var(--accent); }
  .hero p {
    color: var(--muted);
    font-size: 0.95rem;
    margin: 0.5rem 0 0;
  }

  /* ---- Mode toggle tabs ---- */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--muted);
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
    font-weight: 500;
    font-size: 0.9rem;
  }
  .stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #fff !important;
  }
  .stTabs [data-baseweb="tab-border"] { display: none; }

  /* ---- Inputs ---- */
  .stTextInput > div > div > input,
  .stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-lo) !important;
  }

  /* ---- Buttons ---- */
  .stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: opacity 0.15s;
    width: 100%;
  }
  .stButton > button:hover { opacity: 0.85; }
  .stButton > button:disabled { opacity: 0.4 !important; }

  /* ---- Upload box ---- */
  [data-testid="stFileUploader"] {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 1rem;
  }
  [data-testid="stFileUploader"]:hover { border-color: var(--accent); }

  /* ---- Pipeline step card ---- */
  .step-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    position: relative;
  }
  .step-card.running  { border-color: var(--accent); }
  .step-card.success  { border-color: var(--green); }
  .step-card.warning  { border-color: var(--amber); }
  .step-card.error    { border-color: var(--red); }

  .step-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-weight: 600;
    font-size: 0.95rem;
  }
  .step-icon { font-size: 1.1rem; }
  .step-body {
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: var(--muted);
    font-family: var(--mono);
    line-height: 1.6;
  }

  /* ---- Result grid ---- */
  .spec-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
    margin-top: 0.5rem;
  }
  .spec-cell {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 1rem;
  }
  .spec-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin-bottom: 0.25rem;
  }
  .spec-value {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
  }

  /* ---- Feature tags ---- */
  .tag {
    display: inline-block;
    background: var(--accent-lo);
    color: var(--accent);
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 0.15rem;
  }

  /* ---- Source links ---- */
  .source-link {
    display: block;
    color: var(--accent);
    font-size: 0.8rem;
    font-family: var(--mono);
    text-decoration: none;
    padding: 0.2rem 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .source-link:hover { text-decoration: underline; }

  /* ---- Divider ---- */
  hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

  /* Progress bar */
  .stProgress > div > div > div { background: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# Logging to session buffer
# ----------------------------------------------------------
class SessionLogHandler(logging.Handler):
    def emit(self, record):
        if "scraper_logs" not in st.session_state:
            st.session_state.scraper_logs = []
        st.session_state.scraper_logs.append(
            f"[{record.levelname}] {record.name}: {record.getMessage()}"
        )

_handler = SessionLogHandler()
_handler.setLevel(logging.INFO)
logging.getLogger("web_scraping").addHandler(_handler)


# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------

def fmt_json(obj: dict) -> str:
    def _default(o):
        return o.isoformat() if isinstance(o, datetime) else str(o)
    return json.dumps(obj, indent=2, ensure_ascii=False, default=_default)


def spec_grid(doc: dict) -> str:
    fields = [
        ("make", "Make"), ("model", "Model"), ("year", "Year"),
        ("body_type", "Body Type"), ("engine", "Engine"),
        ("horsepower", "Horsepower"), ("torque", "Torque"),
        ("transmission", "Transmission"), ("fuel_economy", "Fuel Economy"),
        ("fuel_type", "Fuel Type"), ("drive", "Drive"),
        ("price", "Price"), ("cylinders", "Cylinders"),
    ]
    cells = ""
    for key, label in fields:
        val = doc.get(key)
        if val:
            cells += f"""
            <div class="spec-cell">
              <div class="spec-label">{label}</div>
              <div class="spec-value">{val}</div>
            </div>"""
    return f'<div class="spec-grid">{cells}</div>'


BLOCKED = {
    "facebook.com","instagram.com","tiktok.com",
    "youtube.com","twitter.com","pinterest.com",
    "reddit.com","tumblr.com","snapchat.com",
}


# ----------------------------------------------------------
# Pipeline runner
# ----------------------------------------------------------

def run_pipeline_by_name(make_in: str, model_in: str, year_in: str | None,
                         steps_ph, progress_ph):
    """Search by name → scrape → extract → build document."""

    from web_scraping.search       import VehicleSearchClient
    from web_scraping.requests     import HTTPClient
    from web_scraping.playwright   import BrowserSession
    from web_scraping.parser       import HTMLParser
    from web_scraping.extractor    import VehicleExtractor
    from web_scraping.cleaner      import DataCleaner
    from web_scraping.json_builder import VehicleDocumentBuilder

    results = {}
    total_steps = 4

    def render_step(idx, icon, label, state, body=""):
        state_class = {"running": "running", "done": "success",
                       "warn": "warning", "error": "error"}.get(state, "")
        return f"""
        <div class="step-card {state_class}">
          <div class="step-header">
            <span class="step-icon">{icon}</span>
            <span>Step {idx} — {label}</span>
          </div>
          {"<div class='step-body'>" + body + "</div>" if body else ""}
        </div>"""

    def update(cards):
        steps_ph.markdown("".join(cards), unsafe_allow_html=True)

    cards = []

    # ── Step 1: Google Search ──────────────────────────────
    progress_ph.progress(1 / total_steps)
    cards.append(render_step(1, "🔍", "Google Search", "running",
                              f"Searching for: {year_in or ''} {make_in} {model_in}…"))
    update(cards)

    try:
        searcher = VehicleSearchClient()
        urls = searcher.search_vehicle(make_in, model_in, year_in, num_results=5)
        urls = [u for u in urls if not any(d in u for d in BLOCKED)]

        if urls:
            url_lines = "<br>".join(f"• {u[:80]}" for u in urls[:5])
            cards[-1] = render_step(1, "✅", "Google Search", "done",
                                     f"Found {len(urls)} URLs<br>{url_lines}")
        else:
            cards[-1] = render_step(1, "⚠️", "Google Search", "warn",
                                     "No results — check SERPAPI_KEY in .env")
            update(cards)
            return None
        update(cards)

    except Exception as e:
        cards[-1] = render_step(1, "❌", "Google Search", "error", str(e))
        update(cards)
        return None

    # ── Step 2: Scrape pages ───────────────────────────────
    progress_ph.progress(2 / total_steps)
    cards.append(render_step(2, "🌐", "Scraping Pages", "running",
                              f"Downloading {len(urls[:5])} pages…"))
    update(cards)

    http = HTTPClient()
    parsed_pages = []

    for url in urls[:5]:
        html = http.get(url)
        if not html or len(html) < 3000:
            try:
                with BrowserSession(headless=True) as browser:
                    html = browser.get_page(url, scroll=True, delay=1.5)
            except Exception:
                continue
        if html:
            parsed = HTMLParser(html, url=url).parse()
            parsed_pages.append(parsed)

    body2 = f"Scraped {len(parsed_pages)} / {len(urls[:5])} pages successfully"
    cards[-1] = render_step(2, "✅" if parsed_pages else "❌",
                             "Scraping Pages",
                             "done" if parsed_pages else "error", body2)
    update(cards)

    if not parsed_pages:
        return None

    # ── Step 3: Extract & Clean ────────────────────────────
    progress_ph.progress(3 / total_steps)
    cards.append(render_step(3, "⚙️", "Extract & Clean", "running",
                              "Extracting vehicle specs from pages…"))
    update(cards)

    cleaner = DataCleaner()
    cleaned_pages = []
    all_fields = set()

    for parsed in parsed_pages:
        extracted = VehicleExtractor(parsed).extract()
        cleaned   = cleaner.clean(extracted)
        filled    = {k for k, v in cleaned.items() if v not in (None, {}, [], "")}
        all_fields.update(filled)
        cleaned_pages.append(cleaned)

    useful = [f for f in all_fields if f not in ("source_url", "page_title")]
    body3 = f"Fields found across pages: {', '.join(sorted(useful)) or 'none'}"
    cards[-1] = render_step(3, "✅", "Extract & Clean", "done", body3)
    update(cards)

    # ── Step 4: Build Document ─────────────────────────────
    progress_ph.progress(4 / total_steps)
    cards.append(render_step(4, "📄", "Build Document", "running",
                              "Merging pages → building MongoDB document…"))
    update(cards)

    builder  = VehicleDocumentBuilder()
    merged   = builder.merge_pages(cleaned_pages)
    document = builder.build(
        make=make_in, model=model_in, year=year_in,
        cleaned_data=merged, sources=urls[:5],
    )

    body4 = f"Document built — {len(document)} fields | {len(document.get('features', []))} features"
    cards[-1] = render_step(4, "✅", "Build Document", "done", body4)
    update(cards)
    progress_ph.progress(1.0)

    return document


def run_pipeline_by_image(pil_image: Image.Image,
                           steps_ph, progress_ph):
    """Google Lens → parse title → search → scrape → extract → build."""

    from web_scraping.google_lens  import GoogleLensClient
    from web_scraping.search       import VehicleSearchClient
    from web_scraping.requests     import HTTPClient
    from web_scraping.playwright   import BrowserSession
    from web_scraping.parser       import HTMLParser
    from web_scraping.extractor    import VehicleExtractor
    from web_scraping.cleaner      import DataCleaner
    from web_scraping.json_builder import VehicleDocumentBuilder
    from web_scraping.scraper      import VehicleScraper

    total_steps = 5

    def render_step(idx, icon, label, state, body=""):
        state_class = {"running": "running", "done": "success",
                       "warn": "warning", "error": "error"}.get(state, "")
        return f"""
        <div class="step-card {state_class}">
          <div class="step-header">
            <span class="step-icon">{icon}</span>
            <span>Step {idx} — {label}</span>
          </div>
          {"<div class='step-body'>" + body + "</div>" if body else ""}
        </div>"""

    def update(cards):
        steps_ph.markdown("".join(cards), unsafe_allow_html=True)

    cards = []

    # ── Step 1: Google Lens ────────────────────────────────
    progress_ph.progress(1 / total_steps)
    cards.append(render_step(1, "🔎", "Google Lens", "running",
                              "Uploading image → running visual search…"))
    update(cards)

    try:
        lens   = GoogleLensClient()
        result = lens.get_vehicle_info(pil_image)
    except ValueError as e:
        cards[-1] = render_step(1, "❌", "Google Lens", "error", str(e))
        update(cards)
        return None

    title   = result.get("title") or ""
    matches = result.get("visual_matches", [])
    lens_urls = result.get("urls", [])

    if title:
        top3 = "<br>".join(f"• {m['title'][:70]}" for m in matches[:3])
        cards[-1] = render_step(1, "✅", "Google Lens", "done",
                                 f"<b>Identified:</b> {title}<br>"
                                 f"{len(matches)} visual matches<br>{top3}")
    else:
        cards[-1] = render_step(1, "⚠️", "Google Lens", "warn",
                                 f"No title found. {len(matches)} visual matches returned.")
    update(cards)

    # ── Step 2: Parse Title ────────────────────────────────
    progress_ph.progress(2 / total_steps)
    scraper_util = VehicleScraper.__new__(VehicleScraper)
    make, model, year = scraper_util._parse_title(title)

    if make or model:
        body2 = f"make={make!r}  model={model!r}  year={year!r}"
        cards.append(render_step(2, "✅", "Parse Vehicle Name", "done", body2))
    else:
        cards.append(render_step(2, "⚠️", "Parse Vehicle Name", "warn",
                                  f"Could not parse make/model from: {title!r}"))
    update(cards)

    if not make and not model:
        return None

    # ── Step 3: Google Search ──────────────────────────────
    progress_ph.progress(3 / total_steps)
    cards.append(render_step(3, "🔍", "Google Search", "running",
                              f"Searching for: {year or ''} {make} {model}…"))
    update(cards)

    try:
        searcher     = VehicleSearchClient()
        search_urls  = searcher.search_vehicle(make or "", model or "", year, num_results=5)
        all_urls     = list(dict.fromkeys(search_urls + lens_urls))
        all_urls     = [u for u in all_urls if not any(d in u for d in BLOCKED)][:6]

        url_lines = "<br>".join(f"• {u[:80]}" for u in all_urls[:4])
        cards[-1] = render_step(3, "✅", "Google Search", "done",
                                 f"{len(all_urls)} URLs total<br>{url_lines}")
        update(cards)
    except Exception as e:
        cards[-1] = render_step(3, "❌", "Google Search", "error", str(e))
        update(cards)
        return None

    # ── Step 4: Scrape pages ───────────────────────────────
    progress_ph.progress(4 / total_steps)
    cards.append(render_step(4, "🌐", "Scraping Pages", "running",
                              f"Downloading {len(all_urls)} pages…"))
    update(cards)

    http = HTTPClient()
    parsed_pages = []

    for url in all_urls[:5]:
        html = http.get(url)
        if not html or len(html) < 3000:
            try:
                with BrowserSession(headless=True) as browser:
                    html = browser.get_page(url, scroll=True, delay=1.5)
            except Exception:
                continue
        if html:
            parsed = HTMLParser(html, url=url).parse()
            parsed_pages.append(parsed)

    body4 = f"Scraped {len(parsed_pages)} pages"
    cards[-1] = render_step(4, "✅" if parsed_pages else "❌",
                             "Scraping Pages",
                             "done" if parsed_pages else "error", body4)
    update(cards)

    if not parsed_pages:
        return None

    # ── Step 5: Extract, Clean & Build ────────────────────
    progress_ph.progress(5 / total_steps)
    cards.append(render_step(5, "📄", "Extract & Build Document", "running",
                              "Extracting specs → merging → building document…"))
    update(cards)

    cleaner       = DataCleaner()
    cleaned_pages = []

    for parsed in parsed_pages:
        extracted = VehicleExtractor(parsed).extract()
        cleaned   = cleaner.clean(extracted)
        cleaned_pages.append(cleaned)

    builder  = VehicleDocumentBuilder()
    merged   = builder.merge_pages(cleaned_pages)
    document = builder.build(
        make=make or "Unknown",
        model=model or title or "Unknown",
        year=year,
        cleaned_data=merged,
        sources=all_urls,
    )

    body5 = f"Document built — {len(document)} fields | {len(document.get('features', []))} features"
    cards[-1] = render_step(5, "✅", "Extract & Build Document", "done", body5)
    update(cards)
    progress_ph.progress(1.0)

    return document


# ----------------------------------------------------------
# Render result
# ----------------------------------------------------------
def render_result(doc: dict):
    st.markdown("---")
    st.markdown("### 📋 Vehicle Document")

    # Spec grid
    grid_html = spec_grid(doc)
    if grid_html.strip() != '<div class="spec-grid"></div>':
        st.markdown(grid_html, unsafe_allow_html=True)
    else:
        st.info("No specs extracted from the scraped pages.")

    col1, col2 = st.columns(2)

    # Description
    with col1:
        if doc.get("description"):
            st.markdown("**Description**")
            st.markdown(
                f'<div style="background:#151821;border:1px solid #252a38;border-radius:10px;'
                f'padding:1rem;font-size:0.85rem;color:#94a3b8;line-height:1.6;">'
                f'{doc["description"][:600]}{"…" if len(doc.get("description",""))>600 else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Dimensions
    with col2:
        dims = doc.get("dimensions", {})
        if dims:
            st.markdown("**Dimensions**")
            dim_html = "".join(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:0.3rem 0;border-bottom:1px solid #252a38;font-size:0.85rem;">'
                f'<span style="color:#64748b">{k}</span>'
                f'<span style="color:#e2e8f0;font-family:monospace">{v}</span></div>'
                for k, v in list(dims.items())[:8]
            )
            st.markdown(
                f'<div style="background:#151821;border:1px solid #252a38;'
                f'border-radius:10px;padding:1rem">{dim_html}</div>',
                unsafe_allow_html=True,
            )

    # Features
    features = doc.get("features", [])
    if features:
        st.markdown("**Features**")
        tags = "".join(f'<span class="tag">{f}</span>' for f in features[:30])
        st.markdown(tags, unsafe_allow_html=True)

    # Sources
    sources = doc.get("sources", [])
    if sources:
        st.markdown("**Sources**")
        links = "".join(
            f'<a class="source-link" href="{u}" target="_blank">{u}</a>'
            for u in sources
        )
        st.markdown(
            f'<div style="background:#151821;border:1px solid #252a38;'
            f'border-radius:10px;padding:0.75rem 1rem">{links}</div>',
            unsafe_allow_html=True,
        )

    # Raw JSON expander
    with st.expander("📦 Raw JSON Document"):
        st.code(fmt_json(doc), language="json")


# ----------------------------------------------------------
# Main UI
# ----------------------------------------------------------

st.markdown("""
<div class="hero">
  <h1>🚗 Vehicle <span>Scraper</span></h1>
  <p>Search by name or upload an image — pipeline runs live</p>
</div>
""", unsafe_allow_html=True)

tab_name, tab_image = st.tabs(["🔤  Search by Name", "📷  Search by Image"])


# ═══════════════════════════════════════════════════════════
# TAB 1 — Search by name
# ═══════════════════════════════════════════════════════════
with tab_name:
    st.markdown("<br>", unsafe_allow_html=True)

    col_make, col_model, col_year = st.columns([2, 3, 1])
    with col_make:
        make_input  = st.text_input("Make", placeholder="e.g. Mercedes-Benz",
                                     label_visibility="visible")
    with col_model:
        model_input = st.text_input("Model", placeholder="e.g. C300",
                                     label_visibility="visible")
    with col_year:
        year_input  = st.text_input("Year", placeholder="2019",
                                     label_visibility="visible")

    run_name = st.button("🔍  Search", key="btn_name",
                          disabled=not (make_input.strip() or model_input.strip()))

    if run_name:
        st.session_state.scraper_logs = []
        st.markdown("---")
        st.markdown("### ⚙️ Pipeline")

        progress_ph = st.progress(0)
        steps_ph    = st.empty()

        doc = run_pipeline_by_name(
            make_in  = make_input.strip(),
            model_in = model_input.strip(),
            year_in  = year_input.strip() or None,
            steps_ph = steps_ph,
            progress_ph = progress_ph,
        )

        if doc:
            render_result(doc)
        else:
            st.error("Pipeline completed but no document was produced. "
                     "Check SERPAPI_KEY in your .env file.")

        with st.expander("🪵 Internal Logs"):
            logs = st.session_state.get("scraper_logs", [])
            st.code("\n".join(logs) if logs else "(no logs)", language="text")


# ═══════════════════════════════════════════════════════════
# TAB 2 — Search by image
# ═══════════════════════════════════════════════════════════
with tab_image:
    st.markdown("<br>", unsafe_allow_html=True)

    col_upload, col_preview = st.columns([2, 1])

    with col_upload:
        uploaded = st.file_uploader(
            "Drop a vehicle photo here",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

    with col_preview:
        if uploaded:
            img = Image.open(uploaded).convert("RGB")
            st.image(img, caption="Uploaded image", use_container_width=True)

    run_image = st.button("🔎  Identify & Scrape", key="btn_image",
                           disabled=uploaded is None)

    if run_image and uploaded:
        st.session_state.scraper_logs = []
        img = Image.open(uploaded).convert("RGB")

        st.markdown("---")
        st.markdown("### ⚙️ Pipeline")

        progress_ph = st.progress(0)
        steps_ph    = st.empty()

        doc = run_pipeline_by_image(
            pil_image   = img,
            steps_ph    = steps_ph,
            progress_ph = progress_ph,
        )

        if doc:
            render_result(doc)
        else:
            st.error("Could not identify or scrape this vehicle. "
                     "Make sure SERPAPI_KEY (and optionally IMGBB_API_KEY) "
                     "are set in your .env file.")

        with st.expander("🪵 Internal Logs"):
            logs = st.session_state.get("scraper_logs", [])
            st.code("\n".join(logs) if logs else "(no logs)", language="text")
       # python -m streamlit run tests/Test_scraper.py
       