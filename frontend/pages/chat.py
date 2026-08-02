"""
===========================================================
Smart Vehicle Identifier
Chat Page
===========================================================

Conversational AI assistant for vehicle questions.

Responsibilities
----------------
- Display conversation history (text + optional images)
- Accept text input, an optional image, or both together
- Call the Chat API without blocking the UI thread
- Show a generic "searching" status only when the answer is
  taking a while — never reveals that a web search is used
- Track vehicles mentioned during the conversation
- Export a PDF report of selected (or all) vehicles

No inference / backend logic lives here.
"""

from __future__ import annotations

import threading
import time

import streamlit as st
from PIL import Image

from api.chat_api import chat_api
from utils.pdf_export import build_vehicle_pdf
from utils.session import (
    add_chat_vehicle,
    get,
    get_chat_vehicles,
    set,
)

# ==========================================================
# Configuration
# ==========================================================

# Only reveal a "please wait" status once the response passes
# this delay. A fast, model-only answer never shows it.
SEARCH_STATUS_DELAY_SECONDS = 1.5


# ==========================================================
# Helpers
# ==========================================================

def _ask_with_status(
    question: str,
    image: Image.Image | None,
    conversation_id: str | None,
) -> dict:
    """
    Call the chat API on a background thread.

    If the backend takes longer than SEARCH_STATUS_DELAY_SECONDS
    to respond (e.g. it had to search), show a neutral status
    message. Fast, model-only answers never show anything.
    """

    result: dict = {}
    error: dict = {}

    def worker() -> None:
        try:
            result["data"] = chat_api.ask(question, image, conversation_id)
        except Exception as exc:  # noqa: BLE001
            error["exc"] = exc

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    status = st.empty()
    start = time.time()

    while thread.is_alive():
        if time.time() - start > SEARCH_STATUS_DELAY_SECONDS:
            status.markdown("🔎 جاري البحث في قاعدة البيانات، برجاء الانتظار...")
        time.sleep(0.2)

    thread.join()
    status.empty()

    if "exc" in error:
        raise error["exc"]

    return result.get("data", {})


def _extract_vehicle(response: dict) -> dict | None:
    """Pull vehicle info out of a chat response, if the backend sent any."""

    vehicle = response.get("vehicle")

    if isinstance(vehicle, dict) and vehicle.get("make"):
        return vehicle

    return None


def _render_message(message: dict) -> None:
    """Render a single chat bubble (text and/or image)."""

    with st.chat_message(message["role"]):

        if message.get("image") is not None:
            st.image(message["image"], width=220)

        if message.get("content"):
            st.write(message["content"])


# ==========================================================
# Export Section
# ==========================================================

def _render_export_section() -> None:
    """Let the user download a PDF of vehicles discussed in chat."""

    vehicles = get_chat_vehicles()

    if not vehicles:
        return

    st.divider()
    st.markdown("### 📄 تصدير السيارات التي سألت عنها")

    labels = [
        f"{vehicle.get('make', 'Unknown')} {vehicle.get('model', 'Unknown')}"
        for vehicle in vehicles
    ]

    selected = st.multiselect(
        "اختر سيارات معينة (اتركها فارغة لتصدير كل ما سألت عنه)",
        options=labels,
        key="chat_export_selection",
    )

    vehicles_to_export = (
        [v for v, label in zip(vehicles, labels) if label in selected]
        if selected
        else vehicles
    )

    if st.button(
        "📥 تجهيز تقرير PDF",
        use_container_width=True,
        key="prepare_chat_pdf",
    ):
        try:
            pdf_bytes = build_vehicle_pdf(vehicles_to_export)

        except RuntimeError as exc:
            st.error(str(exc))
            return

        st.download_button(
            "⬇️ حفظ الملف",
            data=pdf_bytes,
            file_name="vehicle_report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="download_chat_pdf",
        )


# ==========================================================
# Public Page
# ==========================================================

def render() -> None:
    """Render the AI Assistant chat page."""

    st.title("🤖 AI Assistant")

    messages = get("chat_messages", [])

    for message in messages:
        _render_message(message)

    with st.expander("📎 إرفاق صورة سيارة (اختياري)"):
        uploaded = st.file_uploader(
            "صورة",
            type=("png", "jpg", "jpeg", "webp"),
            key="chat_image_upload",
            label_visibility="collapsed",
        )

    question = st.chat_input("اسأل عن أي سيارة...")

    if not question:
        _render_export_section()
        return

    image = None

    if uploaded is not None:
        image = Image.open(uploaded).convert("RGB")

    user_message = {"role": "user", "content": question, "image": image}

    messages.append(user_message)
    set("chat_messages", messages)

    _render_message(user_message)

    try:
        response = _ask_with_status(question, image, get("chat_context"))

    except Exception as exc:  # noqa: BLE001
        st.error(f"تعذر التواصل مع المساعد: {exc}")
        return

    set(
        "chat_context",
        response.get("conversation_id", get("chat_context")),
    )

    answer = response.get("answer") or response.get("response") or "..."

    assistant_message = {"role": "assistant", "content": answer, "image": None}

    messages.append(assistant_message)
    set("chat_messages", messages)

    vehicle = _extract_vehicle(response)

    if vehicle is not None:
        add_chat_vehicle(vehicle)

    _render_message(assistant_message)

    _render_export_section()
