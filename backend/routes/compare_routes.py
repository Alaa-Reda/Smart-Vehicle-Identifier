"""
Compare Routes
==============
Registers all /api/v1/compare endpoints with the FastAPI application.
"""
from controllers.compare_controller import router as compare_router

__all__ = ["compare_router"]
