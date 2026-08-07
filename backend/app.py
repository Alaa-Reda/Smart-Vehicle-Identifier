"""
Smart Vehicle Identifier — Backend Entry Point

Run:
    cd D:/Smart-Vehicle-Identifier/backend
    python run.py
"""

from __future__ import annotations

import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# sys.path is already set by run.py before this module is imported.
# This guard ensures direct `python app.py` also works.
_BACKEND_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
for _p in [
    _BACKEND_DIR,
    _PROJECT_ROOT,
    os.path.join(_PROJECT_ROOT, "data"),
    os.path.join(_PROJECT_ROOT, "models"),
    os.path.join(_PROJECT_ROOT, "web_scraping"),
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dotenv import load_dotenv
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from controllers.chat_controller import router as chat_router
from controllers.compare_controller import router as compare_router
from controllers.history_controller import router as history_router
from controllers.image_controller import router as image_router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("smart_vehicle_identifier")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting Smart Vehicle Identifier backend...")

    # MongoDB
    try:
        from database.mongodb.mongodb import MongoDBManager
        MongoDBManager().connect()
        logger.info("MongoDB connected.")
    except Exception as exc:
        logger.warning("MongoDB unavailable: %s", exc)

    # FAISS
    try:
        from database.faiss.vector_store import VectorStore
        VectorStore()
        logger.info("FAISS vector store initialized.")
    except Exception as exc:
        logger.warning("FAISS unavailable (NumPy fallback active): %s", exc)

    # ── Pre-warm heavy singletons so first request is fast ───────────────
    # CarClassifier loads a 344-layer ConvNext model (~55s on CPU)
    # GoogleLensClient and VehicleScraper are lightweight but we init them here
    # so __init__ never blocks a request.
    try:
        import asyncio
        from services.vehicle_service import _get_classifier, _get_scraper, _get_lens_client
        logger.info("Pre-warming CarClassifier (this takes ~5-60s on CPU)...")
        await asyncio.get_event_loop().run_in_executor(None, _get_classifier)
        _get_scraper()
        _get_lens_client()
        logger.info("All singletons ready — first request will be fast.")
    except Exception as exc:
        logger.warning("Singleton warmup failed (will load on first request): %s", exc)

    yield

    logger.info("Shutting down...")
    try:
        from database.mongodb.mongodb import MongoDBManager
        MongoDBManager().disconnect()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# App Factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Vehicle Identifier API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    allowed_origins = os.environ.get(
        "ALLOWED_ORIGINS", "http://localhost:8501,http://localhost:3000"
    ).split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def timing(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}s"
        return response

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_server_error", "detail": "An unexpected error occurred."},
        )

    app.include_router(image_router)
    app.include_router(chat_router)
    app.include_router(compare_router)
    app.include_router(history_router)

    @app.get("/health", tags=["System"])
    async def health():
        mongo_ok = False
        try:
            from database.mongodb.mongodb import MongoDBManager
            mongo_ok = MongoDBManager().health_check()
        except Exception:
            pass

        return {
            "status": "ok",
            "version": "1.0.0",
            "services": {
                "mongodb": "connected" if mongo_ok else "unavailable",
                "groq": "configured" if os.environ.get("GROQ_API_KEY") else "missing_key",
                "serp": "configured" if os.environ.get("SERP_API_KEY") else "missing_key",
            },
        }

    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Smart Vehicle Identifier API — visit /docs"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=os.environ.get("ENV", "production") == "development",
        log_level="info",
    )