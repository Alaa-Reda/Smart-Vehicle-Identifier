"""
Qwen3-VL Inference

This file is responsible for sending
the image and question to the model
and returning the generated answer.
"""

import torch

# Import loaded model and processor
from models.qwen.loader import model, processor

# Import project settings
from backend.config import MAX_NEW_TOKENS


def generate_answer(image, question):
    """
    Generate an answer from the Qwen3-VL model.

    Args:
        image : PIL Image
        question : User question

    Returns:
        Generated answer as text
    """

    # Create chat message
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image
                },
                {
                    "type": "text",
                    "text": question
                }
            ]
        }
    ]

    # Convert messages into model format
    prompt = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Prepare inputs
    inputs = processor(
        text=[prompt],
        images=[image],
        return_tensors="pt"
    ).to(model.device)

    # Generate prediction
    with torch.no_grad():

        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS
        )

    # Remove prompt tokens
    generated_ids = output[:, inputs.input_ids.shape[1]:]

    # Decode output
    answer = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]

    return answer