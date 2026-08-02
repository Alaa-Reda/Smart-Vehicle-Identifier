"""
===========================================================
Vision SDK Configuration — Groq Backend
===========================================================
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# Groq API
# ==========================================================

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()

# Vision model on Groq — supports images + text
MODEL_NAME: str = os.getenv(
    "MODEL_NAME",
    "qwen/qwen3.6-27b",   # Default: Groq vision model
).strip()

# ==========================================================
# Generation Configuration
# ==========================================================

MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P: float = float(os.getenv("TOP_P", "0.9"))

STREAM: bool = os.getenv("STREAM", "False").lower() == "true"

# ==========================================================
# Network
# ==========================================================

TIMEOUT: int = int(os.getenv("TIMEOUT", "120"))
RETRIES: int = int(os.getenv("RETRIES", "3"))

# ==========================================================
# Provider (fixed to groq — replaces HuggingFace providers)
# ==========================================================

PROVIDER: str = "groq"