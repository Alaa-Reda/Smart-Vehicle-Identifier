"""
Image Routes
============
Registers all /api/v1/image endpoints with the FastAPI application.
"""
from controllers.image_controller import router as image_router

__all__ = ["image_router"]
