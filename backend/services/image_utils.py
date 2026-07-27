"""
Image Utilities

This file contains helper functions
for loading and preparing images.
"""

from PIL import Image
import os

# Import allowed image extensions from project settings
from backend.config import ALLOWED_EXTENSIONS


def is_allowed_file(filename):
    """
    Check if uploaded file has a valid image extension.
    """

    extension = filename.rsplit(".", 1)[-1].lower()

    return extension in ALLOWED_EXTENSIONS


def load_image(image_path):
    """
    Load image and convert it to RGB.
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError("Image not found.")

    image = Image.open(image_path)

    image = image.convert("RGB")

    return image