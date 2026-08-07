"""
Chat Controller
===============
Handles all text-based conversational Q&A requests.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from services.vehicle_service import VehicleService
from services.search_service import SearchService
from ranking.moderation import ModerationService
from ranking.intent_classifier import IntentClassifier
from ranking.query_router import QueryRouter
from memory.session_memory import SessionMemory
from rag.rag_manager import RAGManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(default=None)
    vehicle_context: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default=None)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question must not be blank.")
        return v.strip()


class DisagreementRequest(BaseModel):
    session_id: str = Field(...)
    original_question: str = Field(...)
    disputed_answer: str = Field(...)
    user_claim: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# Dependency Injection
# ---------------------------------------------------------------------------

def get_vehicle_service() -> VehicleService:
    return VehicleService()

def get_search_service() -> SearchService:
    return SearchService()

def get_moderation() -> ModerationService:
    return ModerationService()

def get_intent_classifier() -> IntentClassifier:
    return IntentClassifier()

def get_query_router() -> QueryRouter:
    return QueryRouter()

def get_session_memory() -> SessionMemory:
    return SessionMemory()

def get_rag_manager() -> RAGManager:
    return RAGManager()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/ask", summary="Ask a question about a vehicle", status_code=status.HTTP_200_OK)
async def ask_question(
    body: ChatRequest,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
    moderation: ModerationService = Depends(get_moderation),
    intent_classifier: IntentClassifier = Depends(get_intent_classifier),
    query_router: QueryRouter = Depends(get_query_router),
    session_memory: SessionMemory = Depends(get_session_memory),
    rag_manager: RAGManager = Depends(get_rag_manager),
) -> JSONResponse:
    moderation_result = await moderation.check(body.question)
    if not moderation_result.is_safe:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "moderation_failed", "message": moderation_result.reason},
        )

    intent = await intent_classifier.classify(body.question)
    route = await query_router.route(
        question=body.question,
        intent=intent,
        vehicle_context=body.vehicle_context,
        session_id=body.session_id,
    )

    try:
        result = await vehicle_service.answer_question(
            question=body.question,
            intent=intent,
            route=route,
            session_id=body.session_id,
            vehicle_context=body.vehicle_context,
            language=body.language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error answering question")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error.")

    return JSONResponse(content=result)


@router.post("/disagree", summary="Re-evaluate a disputed answer", status_code=status.HTTP_200_OK)
async def handle_disagreement(
    body: DisagreementRequest,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> JSONResponse:
    try:
        result = await vehicle_service.handle_disagreement(
            session_id=body.session_id,
            original_question=body.original_question,
            disputed_answer=body.disputed_answer,
            user_claim=body.user_claim,
            language=body.language,
        )
    except Exception as exc:
        logger.exception("Disagreement handling failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Re-evaluation failed.")

    return JSONResponse(content=result)


@router.get("/session/{session_id}/summary", summary="Get session summary", status_code=status.HTTP_200_OK)
async def get_session_summary(
    session_id: str,
    session_memory: SessionMemory = Depends(get_session_memory),
) -> JSONResponse:
    try:
        summary = await session_memory.get_summary(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve summary.")

    if summary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found.")

    return JSONResponse(content=summary)


@router.delete("/session/{session_id}", summary="Clear a session", status_code=status.HTTP_200_OK)
async def clear_session(
    session_id: str,
    session_memory: SessionMemory = Depends(get_session_memory),
) -> JSONResponse:
    try:
        await session_memory.clear(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not clear session.")

    return JSONResponse(content={"status": "cleared", "session_id": session_id})
