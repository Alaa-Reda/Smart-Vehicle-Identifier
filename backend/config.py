"""
Project Configuration
---------------------
This file contains all project settings in one place.
Any file that needs these settings can import them.
"""

import torch

# ==========================
# Model Configuration
# ==========================

# Hugging Face model name
MODEL_NAME = "Qwen/Qwen3-VL-8B-Instruct"

# ==========================
# Device Configuration
# ==========================

# Use GPU if available, otherwise CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ==========================
# Generation Configuration
# ==========================

# Maximum number of generated tokens
MAX_NEW_TOKENS = 100

# Generation randomness
TEMPERATURE = 0.7

# ==========================
# Image Configuration
# ==========================

# Supported image formats
ALLOWED_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png"
]

# ==========================
# Upload Configuration
# ==========================

# Folder where uploaded images will be stored
UPLOAD_FOLDER = "uploads"