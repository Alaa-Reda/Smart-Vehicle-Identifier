"""
Load Qwen3-VL model and processor once.

This file is responsible for loading the AI model
only one time when the backend starts.
"""

import torch

from transformers import (
    AutoProcessor,
    Qwen3VLForConditionalGeneration,
    BitsAndBytesConfig
)

# Import project settings
from backend.config import MODEL_NAME


# ---------------------------------
# Quantization Configuration
# ---------------------------------

# Use 4-bit quantization to reduce GPU memory usage
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
   bnb_4bit_compute_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)


# ---------------------------------
# Load Processor
# ---------------------------------

print("Loading Processor...")

processor = AutoProcessor.from_pretrained(MODEL_NAME)


# ---------------------------------
# Load Model
# ---------------------------------

print("Loading Qwen3-VL Model...")

model = Qwen3VLForConditionalGeneration.from_pretrained(
    MODEL_NAME,
    quantization_config=quantization_config,
    device_map="auto"
)

# Set model to inference mode
model.eval()

print("Model Loaded Successfully.")