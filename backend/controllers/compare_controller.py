"""
Compare Controller
==================
Handles vehicle comparison requests.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from services.compare_service import CompareService
from ranking.moderation import ModerationService
from memory.comparison_memory import ComparisonMemory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/compare", tags=["Compare"])


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class TextCompareRequest(BaseModel):
    vehicles: List[str] = Field(..., min_length=2, max_length=5)
    aspect: Optional[str] = Field(default=None)
    session_id: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default=None)

    @field_validator("vehicles")
    @classmethod
    def validate_vehicle_names(cls, v: List[str]) -> List[str]:
        cleaned = [name.strip() for name in v if name.strip()]
        if len(cleaned) < 2:
            raise ValueError("At least 2 non-empty vehicle names are required.")
        if len(set(n.lower() for n in cleaned)) < 2:
            raise ValueError("Vehicles must be distinct.")
        return cleaned


# ---------------------------------------------------------------------------
# Dependency Injection
# ---------------------------------------------------------------------------

def get_compare_service() -> CompareService:
    return CompareService()

def get_moderation() -> ModerationService:
    return ModerationService()

def get_comparison_memory() -> ComparisonMemory:
    return ComparisonMemory()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/text", summary="Compare vehicles by name", status_code=status.HTTP_200_OK)
async def compare_by_text(
    body: TextCompareRequest,
    compare_service: CompareService = Depends(get_compare_service),
    moderation: ModerationService = Depends(get_moderation),
) -> JSONResponse:
    combined = " vs ".join(body.vehicles)
    mod = await moderation.check(combined)
    if not mod.is_safe:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "moderation_failed", "message": mod.reason},
        )

    try:
        result = await compare_service.compare_by_names(
            vehicles=body.vehicles,
            aspect=body.aspect,
            session_id=body.session_id,
            language=body.language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception:
        logger.exception("Text comparison failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comparison failed.")

    return JSONResponse(content=result)


@router.post("/images", summary="Compare vehicles from images", status_code=status.HTTP_200_OK)
async def compare_by_images(
    files: List[UploadFile] = File(...),
    aspect: Optional[str] = Form(default=None),
    session_id: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None),
    compare_service: CompareService = Depends(get_compare_service),
) -> JSONResponse:
    if len(files) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least 2 images required.")
    if len(files) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 5 images allowed.")

    _ALLOWED = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    images = []
    for f in files:
        if f.content_type not in _ALLOWED:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"Unsupported type in '{f.filename}'.")
        try:
            data = await f.read()
            images.append((data, f.filename or "upload.jpg"))
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not read '{f.filename}'.")

    try:
        result = await compare_service.compare_by_images(
            images=images, aspect=aspect, session_id=session_id, language=language
        )
    except Exception:
        logger.exception("Image comparison failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comparison failed.")

    return JSONResponse(content=result)


@router.get("/history/{session_id}", summary="Get comparison history", status_code=status.HTTP_200_OK)
async def get_comparison_history(
    session_id: str,
    limit: int = 10,
    comparison_memory: ComparisonMemory = Depends(get_comparison_memory),
) -> JSONResponse:
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be 1–50.")
    try:
        comparisons = await comparison_memory.get_by_session(session_id=session_id, limit=limit)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve history.")

    return JSONResponse(content={"session_id": session_id, "comparisons": comparisons})


@router.delete("/{comparison_id}", summary="Delete a comparison", status_code=status.HTTP_200_OK)
async def delete_comparison(
    comparison_id: str,
    comparison_memory: ComparisonMemory = Depends(get_comparison_memory),
) -> JSONResponse:
    try:
        deleted = await comparison_memory.delete(comparison_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete comparison.")

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comparison '{comparison_id}' not found.")

    return JSONResponse(content={"status": "deleted", "comparison_id": comparison_id})
