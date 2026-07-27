"""
Main FastAPI Application

This file starts the backend server
and registers all API routes.
"""

# Import FastAPI
from fastapi import FastAPI

# Import prediction router
from backend.routes.predict import router as predict_router

# Create FastAPI application
app = FastAPI(
    title="Visual Question Answering API",
    description="Backend for Qwen3-VL Visual Question Answering",
    version="1.0.0"
)

# Register routes
app.include_router(predict_router)

# Home endpoint
@app.get("/")
def home():
    """
    Test endpoint.
    """

    return {
        "message": "Visual Question Answering API is running!"
    }