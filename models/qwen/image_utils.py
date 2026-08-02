from __future__ import annotations

import base64
import io
import mimetypes
from pathlib import Path
from typing import Any

from PIL import Image


class ImageProcessor:
    """
    Image processing utilities for Qwen3-VL.
    """

    SUPPORTED_FORMATS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
    }

    MAX_IMAGE_SIZE = 20 * 1024 * 1024

    @staticmethod
    def is_url(value: str) -> bool:
        return value.startswith(("http://", "https://"))

    @staticmethod
    def is_base64(value: str) -> bool:
        return value.startswith("data:image/")

    @classmethod
    def validate_path(cls, image: str | Path) -> Path:
        image = Path(image)

        if not image.exists():
            raise FileNotFoundError(image)

        if image.suffix.lower() not in cls.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {image.suffix}"
            )

        if image.stat().st_size > cls.MAX_IMAGE_SIZE:
            raise ValueError(
                "Image exceeds maximum allowed size."
            )

        return image

    @classmethod
    def image_to_base64(cls, image: str | Path) -> str:
        image = cls.validate_path(image)

        mime = mimetypes.guess_type(image)[0] or "image/jpeg"

        with open(image, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()

        return f"data:{mime};base64,{encoded}"

    @classmethod
    def pil_to_base64(cls, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        encoded = base64.b64encode(
            buffer.getvalue()
        ).decode()

        return f"data:image/png;base64,{encoded}"

    @classmethod
    def prepare_image(cls, image: Any) -> str:
        """
        Convert any supported image input into a format
        accepted by the Hugging Face Inference API.
        """

        if image is None:
            return ""

        # URL
        if isinstance(image, str) and cls.is_url(image):
            return image

        # Already Base64
        if isinstance(image, str) and cls.is_base64(image):
            return image

        # Local file
        if isinstance(image, (str, Path)):
            return cls.image_to_base64(image)

        # PIL Image
        if isinstance(image, Image.Image):
            return cls.pil_to_base64(image)

        raise TypeError(
            f"Unsupported image type: {type(image)}"
        )