"""
Chat Routes
===========
Registers all /api/v1/chat endpoints with the FastAPI application.
"""
from controllers.chat_controller import router as chat_router

__all__ = ["chat_router"]
