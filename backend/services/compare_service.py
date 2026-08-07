"""
Compare Service
===============
Business logic for vehicle-to-vehicle comparison.

Responsibilities:
- Retrieve structured data for each vehicle from RAG/MongoDB.
- Trigger web scraping for missing or stale vehicle data.
- Build structured comparison tables across key attributes.
- Generate narrative comparison via Groq.
- Re-rank and validate comparison quality.
- Persist results to ComparisonMemory.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import httpx

from rag.rag_manager import RAGManager
from rag.pipeline import RAGPipeline
from rag.prompt_builder import PromptBuilder
from ranking.ranking_engine import RankingEngine
from memory.comparison_memory import ComparisonMemory
from memory.vehicle_memory import VehicleMemory

logger = logging.getLogger(__name__)

GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_TEXT_MODEL = "qwen/qwen3-32b"
WEB_SCRAPING_API_URL = "http://localhost:8003/scrape"

_COMPARISON_ATTRIBUTES = [
    "make", "model", "year", "engine", "horsepower", "torque",
    "transmission", "fuel_type", "fuel_efficiency", "price_range",
    "seating_capacity", "cargo_space", "safety_rating", "features",
    "dimensions", "weight", "drivetrain",
]


@dataclass
class VehicleData:
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    source: str = "unknown"
    raw_context: str = ""


@dataclass
class ComparisonResult:
    vehicles: List[str]
    attribute_table: Dict[str, Dict[str, Any]]
    narrative: str
    confidence: float
    language: str
    sources: List[str]
    aspect: Optional[str] = None
    conflict_notes: List[str] = field(default_factory=list)


class CompareService:
    """
    Orchestrates all vehicle comparison flows.
    """

    def __init__(self) -> None:
        self._rag = RAGManager()
        self._rag_pipeline = RAGPipeline()
        self._prompt_builder = PromptBuilder()
        self._ranking = RankingEngine()
        self._comparison_memory = ComparisonMemory()
        self._vehicle_memory = VehicleMemory()
        self._http = httpx.AsyncClient(timeout=90.0)

    async def compare_by_names(
        self,
        vehicles: List[str],
        aspect: Optional[str],
        session_id: Optional[str],
        language: Optional[str],
    ) -> Dict[str, Any]:
        detected_language = language or "auto"

        # Retrieve data for all vehicles in parallel
        vehicle_data_list = await asyncio.gather(
            *[self._fetch_vehicle_data(name, detected_language) for name in vehicles],
            return_exceptions=False,
        )

        comparison = await self._build_comparison(
            vehicle_data_list=list(vehicle_data_list),
            aspect=aspect,
            language=detected_language,
        )

        if session_id:
            await self._comparison_memory.save(
                session_id=session_id,
                comparison=self._serialize_comparison(comparison),
            )

        return self._serialize_comparison(comparison)

    async def compare_by_images(
        self,
        images: List[Tuple[bytes, str]],
        aspect: Optional[str],
        session_id: Optional[str],
        language: Optional[str],
    ) -> Dict[str, Any]:
        from vehicle_service import VehicleService

        vehicle_service = VehicleService()
        detected_language = language or "auto"

        # Identify each vehicle from its image
        identification_tasks = [
            vehicle_service.identify_vehicle(
                image_bytes=img_bytes,
                filename=filename,
                session_id=session_id,
                language=detected_language,
            )
            for img_bytes, filename in images
        ]
        identifications = await asyncio.gather(*identification_tasks)

        vehicle_names = [
            ident.get("vehicle_name") or f"Vehicle {i + 1}"
            for i, ident in enumerate(identifications)
        ]

        return await self.compare_by_names(
            vehicles=vehicle_names,
            aspect=aspect,
            session_id=session_id,
            language=detected_language,
        )

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    async def _fetch_vehicle_data(
        self, vehicle_name: str, language: str
    ) -> VehicleData:
        # Try MongoDB cache first
        cached = await self._vehicle_memory.get_by_name(vehicle_name=vehicle_name, limit=1)
        if cached:
            return VehicleData(
                name=vehicle_name,
                attributes=cached[0].get("attributes", {}),
                confidence=cached[0].get("confidence", 0.7),
                source="mongodb",
                raw_context=cached[0].get("raw_context", ""),
            )

        # Try RAG retrieval
        rag_result = await self._rag_pipeline.retrieve_and_generate(
            question=f"Provide detailed specifications for {vehicle_name}",
            vehicle_context=vehicle_name,
            session_context={},
            language=language,
        )

        if rag_result.confidence >= 0.60:
            return VehicleData(
                name=vehicle_name,
                attributes=rag_result.structured_data or {},
                confidence=rag_result.confidence,
                source="rag",
                raw_context=rag_result.answer,
            )

        # Fall back to web scraping
        await self._scrape_and_ingest(vehicle_name)
        rag_result2 = await self._rag_pipeline.retrieve_and_generate(
            question=f"Provide detailed specifications for {vehicle_name}",
            vehicle_context=vehicle_name,
            session_context={},
            language=language,
        )

        return VehicleData(
            name=vehicle_name,
            attributes=rag_result2.structured_data or {},
            confidence=rag_result2.confidence,
            source="web+rag",
            raw_context=rag_result2.answer,
        )

    async def _build_comparison(
        self,
        vehicle_data_list: List[VehicleData],
        aspect: Optional[str],
        language: str,
    ) -> ComparisonResult:
        # Build attribute table
        attribute_table: Dict[str, Dict[str, Any]] = {}
        attrs_to_compare = (
            [aspect] if aspect else _COMPARISON_ATTRIBUTES
        )

        for attr in attrs_to_compare:
            attribute_table[attr] = {}
            for vd in vehicle_data_list:
                attribute_table[attr][vd.name] = vd.attributes.get(attr, "N/A")

        # Generate narrative via Groq
        prompt = self._prompt_builder.build_comparison_prompt(
            vehicles=[vd.name for vd in vehicle_data_list],
            attribute_table=attribute_table,
            aspect=aspect,
            language=language,
        )
        narrative = await self._call_groq_text(prompt, language)

        min_confidence = min(vd.confidence for vd in vehicle_data_list)
        sources = list({vd.source for vd in vehicle_data_list})

        return ComparisonResult(
            vehicles=[vd.name for vd in vehicle_data_list],
            attribute_table=attribute_table,
            narrative=narrative,
            confidence=min_confidence,
            language=language,
            sources=sources,
            aspect=aspect,
        )

    async def _call_groq_text(self, prompt: str, language: str) -> str:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            logger.error("GROQ_API_KEY not set")
            return ""

        lang_instruction = (
            "Respond in Arabic." if language.startswith("ar")
            else "Respond in English."
        )

        try:
            response = await self._http.post(
                f"{GROQ_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_TEXT_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                f"You are an expert automotive comparison analyst. {lang_instruction} "
                                "Be structured, factual, and concise. Never hallucinate specifications."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2048,
                },
                timeout=45.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.error("Groq text call failed during comparison: %s", exc)
            return ""

    async def _scrape_and_ingest(self, vehicle_name: str) -> None:
        try:
            response = await self._http.post(
                WEB_SCRAPING_API_URL,
                json={"vehicle_name": vehicle_name},
                timeout=90.0,
            )
            response.raise_for_status()
            scraped_data = response.json()
            await self._rag.ingest_scraped_data(
                vehicle_name=vehicle_name,
                documents=scraped_data.get("documents", []),
            )
        except Exception as exc:
            logger.warning("Web scraping for '%s' failed: %s", vehicle_name, exc)

    def _serialize_comparison(self, result: ComparisonResult) -> Dict[str, Any]:
        return {
            "vehicles": result.vehicles,
            "aspect": result.aspect,
            "attribute_table": result.attribute_table,
            "narrative": result.narrative,
            "confidence": round(result.confidence, 4),
            "language": result.language,
            "sources": result.sources,
            "conflict_notes": result.conflict_notes,
        }
