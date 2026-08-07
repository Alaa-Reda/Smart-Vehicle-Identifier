"""
Image Controller
================
Handles vehicle image upload requests.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from services.vehicle_service import VehicleService
from ranking.moderation import ModerationService
from ranking.intent_classifier import IntentClassifier
from memory.session_memory import SessionMemory
from memory.vehicle_memory import VehicleMemory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/image", tags=["Image"])

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp"}


# ---------------------------------------------------------------------------
# Dependency Injection
# ---------------------------------------------------------------------------

def get_vehicle_service() -> VehicleService:
    return VehicleService()

def get_moderation_service() -> ModerationService:
    return ModerationService()

def get_intent_classifier() -> IntentClassifier:
    return IntentClassifier()

def get_session_memory() -> SessionMemory:
    return SessionMemory()

def get_vehicle_memory() -> VehicleMemory:
    return VehicleMemory()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_image(file: UploadFile) -> None:
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type '{file.content_type}'. Allowed: jpeg, png, webp.",
        )

def _validate_question(question: str) -> None:
    if not question.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question must not be empty.")
    if len(question.strip()) > 2000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question too long (max 2000 chars).")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/identify", summary="Identify a vehicle from an image", status_code=status.HTTP_200_OK)
async def identify_vehicle(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> JSONResponse:
    _validate_image(file)
    try:
        image_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read uploaded file.")

    try:
        result = await vehicle_service.identify_vehicle(
            image_bytes=image_bytes,
            filename=file.filename or "upload.jpg",
            session_id=session_id,
            language=language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception:
        logger.exception("Vehicle identification error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Identification failed.")

    return JSONResponse(content=result)


@router.post("/identify-with-question", summary="Identify vehicle + answer a question", status_code=status.HTTP_200_OK)
async def identify_vehicle_with_question(
    file: UploadFile = File(...),
    question: str = Form(...),
    session_id: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
    moderation: ModerationService = Depends(get_moderation_service),
    intent_classifier: IntentClassifier = Depends(get_intent_classifier),
) -> JSONResponse:
    _validate_image(file)
    _validate_question(question)

    moderation_result = await moderation.check(question)
    if not moderation_result.is_safe:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "moderation_failed", "message": moderation_result.reason},
        )

    try:
        image_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read uploaded file.")

    intent = await intent_classifier.classify(question)

    try:
        result = await vehicle_service.identify_with_question(
            image_bytes=image_bytes,
            filename=file.filename or "upload.jpg",
            question=question,
            intent=intent,
            session_id=session_id,
            language=language,
        )
    except Exception:
        logger.exception("Identify with question error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Processing failed.")

    return JSONResponse(content=result)


@router.post("/google-lens", summary="Identify unknown vehicle via Google Lens", status_code=status.HTTP_200_OK)
async def identify_via_google_lens(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> JSONResponse:
    _validate_image(file)
    try:
        image_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read uploaded file.")

    try:
        result = await vehicle_service.identify_via_google_lens(
            image_bytes=image_bytes,
            filename=file.filename or "upload.jpg",
            session_id=session_id,
            language=language,
        )
    except Exception:
        logger.exception("Google Lens error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google Lens failed.")

    return JSONResponse(content=result)
