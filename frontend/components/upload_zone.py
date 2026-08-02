"""
===========================================================
Smart Vehicle Identifier
Component: Upload Zone
===========================================================

Professional image upload component.

Features
--------
✓ Drag & Drop
✓ File Validation
✓ Image Preview
✓ Remove Image
✓ Session Integration
✓ Reusable API
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import streamlit as st
from PIL import Image

from utils.session import get, set


# ==========================================================
# Configuration
# ==========================================================

SUPPORTED_FORMATS = ("png", "jpg", "jpeg", "webp")

MAX_IMAGE_SIZE_MB = 10


# ==========================================================
# Data Model
# ==========================================================

@dataclass(frozen=True, slots=True)
class UploadedVehicleImage:
    """Uploaded vehicle image."""

    image: Image.Image
    filename: str
    file_size: int
    width: int
    height: int
    format: str


# ==========================================================
# Validation
# ==========================================================

def _validate(uploaded_file) -> str | None:
    """Validate uploaded image."""

    if uploaded_file is None:
        return None

    size_mb = uploaded_file.size / (1024 * 1024)

    if size_mb > MAX_IMAGE_SIZE_MB:
        return (
            f"Image exceeds maximum size "
            f"({MAX_IMAGE_SIZE_MB} MB)."
        )

    return None


# ==========================================================
# Convert
# ==========================================================

def _to_model(uploaded_file) -> UploadedVehicleImage:
    """Convert Streamlit upload to UploadedVehicleImage."""

    pil_image = Image.open(uploaded_file)

    image_format = pil_image.format or "Unknown"

    image = pil_image.convert("RGB")

    width, height = image.size

    return UploadedVehicleImage(
        image=image,
        filename=uploaded_file.name,
        file_size=uploaded_file.size,
        width=width,
        height=height,
        format=image_format,
    )


# ==========================================================
# Preview
# ==========================================================

def _preview(data: UploadedVehicleImage) -> None:
    """Render image preview."""

    st.image(
        data.image,
        use_container_width=True,
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Width", data.width)
    c2.metric("Height", data.height)
    c3.metric(
        "Size",
        f"{data.file_size / 1024:.1f} KB",
    )


# ==========================================================
# Public Render
# ==========================================================

def render() -> UploadedVehicleImage | None:
    """
    Render upload component.

    Returns
    -------
    UploadedVehicleImage | None
    """

    uploaded = st.file_uploader(
        label="Upload Vehicle Image",
        type=SUPPORTED_FORMATS,
        accept_multiple_files=False,
        help="Supported: PNG, JPG, JPEG, WEBP",
    )

    if uploaded is None:
        set("uploaded_image", None)
        return None

    error = _validate(uploaded)

    if error:
        st.error(error)
        return None

    image_data = _to_model(uploaded)

    set("uploaded_image", image_data)

    _preview(image_data)

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🗑 Remove",
            use_container_width=True,
            key="remove_uploaded_image",
        ):
            set("uploaded_image", None)
            st.rerun()

    with col2:
        st.success("Image Ready")

    return image_data


# ==========================================================
# Helpers
# ==========================================================

def current() -> UploadedVehicleImage | None:
    """Return the current uploaded image."""

    return get("uploaded_image")


def has_image() -> bool:
    """Check whether an image is currently available."""

    return current() is not None


def image_bytes() -> bytes | None:
    """Return the uploaded image as JPEG bytes."""

    img = current()

    if img is None:
        return None

    with BytesIO() as buffer:
        img.image.save(buffer, format="JPEG")
        return buffer.getvalue()