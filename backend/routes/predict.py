"""
Prediction API

This file contains the API endpoint
used to answer questions about images.
"""

import os
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.config import UPLOAD_FOLDER
from backend.services.image_utils import is_allowed_file
from backend.services.inference import predict

# Create router
router = APIRouter()


@router.post("/predict")
async def predict_image(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Receive image and question,
    then return model prediction.
    """

    # Check image format
    if not is_allowed_file(image.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format."
        )

    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Create unique filename
    filename = f"{uuid.uuid4()}_{image.filename}"

    image_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    # Save uploaded image
    with open(image_path, "wb") as file:
        file.write(await image.read())

    # Run model inference
    answer = predict(image_path, question)

    # Return JSON response
    return {
        "question": question,
        "answer": answer
    }