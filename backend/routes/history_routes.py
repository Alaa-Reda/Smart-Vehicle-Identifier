"""
History Routes
==============
Registers all /api/v1/history endpoints with the FastAPI application.
"""
from controllers.history_controller import router as history_router

__all__ = ["history_router"]
