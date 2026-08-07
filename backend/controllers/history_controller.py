"""
History Controller
==================
Handles conversation history operations.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from memory.session_memory import SessionMemory
from memory.vehicle_memory import VehicleMemory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/history", tags=["History"])


def get_session_memory() -> SessionMemory:
    return SessionMemory()

def get_vehicle_memory() -> VehicleMemory:
    return VehicleMemory()


@router.get("/session/{session_id}", summary="Get session history", status_code=status.HTTP_200_OK)
async def get_session_history(
    session_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session_memory: SessionMemory = Depends(get_session_memory),
) -> JSONResponse:
    try:
        history = await session_memory.get_history(session_id=session_id, page=page, page_size=page_size)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve history.")

    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found.")

    return JSONResponse(content=history)


@router.get("/session/{session_id}/vehicles", summary="List vehicles in session", status_code=status.HTTP_200_OK)
async def get_session_vehicles(
    session_id: str,
    vehicle_memory: VehicleMemory = Depends(get_vehicle_memory),
) -> JSONResponse:
    try:
        vehicles = await vehicle_memory.get_by_session(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve vehicles.")

    return JSONResponse(content={"session_id": session_id, "vehicles": vehicles, "count": len(vehicles)})


@router.get("/search", summary="Search history by keyword", status_code=status.HTTP_200_OK)
async def search_history(
    q: str = Query(..., min_length=1, max_length=500),
    session_id: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    session_memory: SessionMemory = Depends(get_session_memory),
) -> JSONResponse:
    try:
        results = await session_memory.search(keyword=q.strip(), session_id=session_id, limit=limit)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed.")

    return JSONResponse(content={"query": q, "results": results, "count": len(results)})


@router.get("/vehicle/{vehicle_name}", summary="Get history for a vehicle", status_code=status.HTTP_200_OK)
async def get_vehicle_history(
    vehicle_name: str,
    limit: int = Query(default=20, ge=1, le=100),
    vehicle_memory: VehicleMemory = Depends(get_vehicle_memory),
) -> JSONResponse:
    try:
        results = await vehicle_memory.get_by_name(vehicle_name=vehicle_name, limit=limit)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve vehicle history.")

    return JSONResponse(content={"vehicle": vehicle_name, "history": results, "count": len(results)})


@router.delete("/session/{session_id}", summary="Delete session history", status_code=status.HTTP_200_OK)
async def delete_session_history(
    session_id: str,
    session_memory: SessionMemory = Depends(get_session_memory),
) -> JSONResponse:
    try:
        deleted_count = await session_memory.delete_session(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete history.")

    return JSONResponse(content={"status": "deleted", "session_id": session_id, "messages_deleted": deleted_count})


@router.delete("/message/{message_id}", summary="Delete a single message", status_code=status.HTTP_200_OK)
async def delete_message(
    message_id: str,
    session_memory: SessionMemory = Depends(get_session_memory),
) -> JSONResponse:
    try:
        deleted = await session_memory.delete_message(message_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete message.")

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Message '{message_id}' not found.")

    return JSONResponse(content={"status": "deleted", "message_id": message_id})


@router.get("/export/{session_id}", summary="Export session as JSON", status_code=status.HTTP_200_OK)
async def export_session_history(
    session_id: str,
    session_memory: SessionMemory = Depends(get_session_memory),
) -> JSONResponse:
    try:
        export_data = await session_memory.export_session(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Export failed.")

    if export_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found.")

    return JSONResponse(content=export_data)
