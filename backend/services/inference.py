"""
Inference Service

This service connects the API with the Qwen model.
"""

# Load image helper
from backend.services.image_utils import load_image

# Import model inference function
from models.qwen.inference import generate_answer


def predict(image_path, question):
    """
    Generate an answer for an image and a question.

    Args:
        image_path (str): Path to the uploaded image.
        question (str): User question.

    Returns:
        str: Model answer.
    """

    # Load image
    image = load_image(image_path)

    # Ask the model
    answer = generate_answer(image, question)

    return answer