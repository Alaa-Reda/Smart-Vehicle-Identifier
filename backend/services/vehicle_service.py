"""
Vehicle Service
===============
Core business logic for the Smart Vehicle Identifier.

Responsibilities:
- Orchestrate the full identification pipeline (ConvNext → Groq → RAG → Web Scraping).
- Handle image + question dual-input flows.
- Handle text-only Q&A flows.
- Handle disagreement re-evaluation flows.
- Detect and apply language automatically.
- Never expose pipeline internals to controllers.
"""

from __future__ import annotations

import asyncio
import base64
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from rag.rag_manager import RAGManager
from rag.pipeline import RAGPipeline
from ranking.ranking_engine import RankingEngine
from ranking.intent_classifier import IntentClassifier, Intent
from ranking.query_router import QueryRouter, Route
from ranking.guardrails import GuardrailsService
from memory.session_memory import SessionMemory
from memory.vehicle_memory import VehicleMemory
from models.qwen.config import MODEL_NAME
from models.car_classification_model.car import CarClassifier
from web_scraping.scraper import VehicleScraper
from web_scraping.google_lens import GoogleLensClient   # Task 1: direct integration
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level Singletons — loaded ONCE at startup, reused across requests
# ---------------------------------------------------------------------------
# CarClassifier takes ~55 seconds to load on CPU — must never be re-created per request
_CLASSIFIER_SINGLETON: Optional["CarClassifier"] = None
_SCRAPER_SINGLETON: Optional["VehicleScraper"] = None
_LENS_CLIENT_SINGLETON: Optional["GoogleLensClient"] = None


def _get_classifier() -> Optional["CarClassifier"]:
    global _CLASSIFIER_SINGLETON
    if _CLASSIFIER_SINGLETON is None:
        try:
            _CLASSIFIER_SINGLETON = CarClassifier()
            logger.info("CarClassifier singleton created.")
        except Exception as exc:
            logger.error("Failed to create CarClassifier singleton: %s", exc)
    return _CLASSIFIER_SINGLETON


def _get_scraper() -> "VehicleScraper":
    global _SCRAPER_SINGLETON
    if _SCRAPER_SINGLETON is None:
        _SCRAPER_SINGLETON = VehicleScraper()
        logger.info("VehicleScraper singleton created.")
    return _SCRAPER_SINGLETON


def _get_lens_client() -> Optional["GoogleLensClient"]:
    global _LENS_CLIENT_SINGLETON
    if _LENS_CLIENT_SINGLETON is None:
        try:
            _LENS_CLIENT_SINGLETON = GoogleLensClient()
            logger.info("GoogleLensClient singleton created.")
        except ValueError:
            logger.warning("GoogleLensClient: SERPAPI_KEY not set — Google Lens disabled.")
    return _LENS_CLIENT_SINGLETON

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.80   # ConvNext minimum
GROQ_CONFIDENCE_THRESHOLD = 0.75             # Groq self-assessed confidence
RAG_CONFIDENCE_THRESHOLD = 0.90              # RAG minimum before skipping web scrape
GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_VISION_MODEL = MODEL_NAME
GROQ_TEXT_MODEL = "qwen/qwen3-32b"

# Task 5: Caching policy (days)
PRICE_CACHE_DAYS  = 5    # price expires after 5 days
SPECS_CACHE_DAYS  = 60   # specs expire after 60 days

# ---------------------------------------------------------------------------
# Internal Data Structures
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    vehicle_name: str
    confidence: float
    top_predictions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GroqVisionResult:
    answer: str
    confidence: float
    language: str
    sources_used: List[str] = field(default_factory=list)
    needs_web_search: bool = False


@dataclass
class PipelineResult:
    answer: str
    vehicle_name: Optional[str]
    confidence: float
    language: str
    source: str                                   # rag | groq | web | google_lens | fallback
    sources_cited: List[str] = field(default_factory=list)
    web_scraped: bool = False
    classification_confidence: Optional[float] = None
    session_id: Optional[str] = None


# ---------------------------------------------------------------------------
# VehicleService
# ---------------------------------------------------------------------------

class VehicleService:
    """
    Orchestrates the complete vehicle identification, Q&A, and comparison
    pipelines. Controllers call only this service — never sub-services directly.
    """

    def __init__(self) -> None:
        # Singletons — heavy models loaded once at module import, reused across all requests
        self.classifier   = _get_classifier()
        self.scraper      = _get_scraper()
        self._lens_client = _get_lens_client()
        # Lightweight services
        self._rag          = RAGManager()
        self._rag_pipeline = RAGPipeline()
        self._ranking      = RankingEngine()
        self._intent       = IntentClassifier()
        self._router       = QueryRouter()
        self._guardrails   = GuardrailsService()
        self._session_memory = SessionMemory()
        self._vehicle_memory = VehicleMemory()
        self._http = httpx.AsyncClient(timeout=60.0)

    def _parse_vehicle_name(self, vehicle_name: str):
        """
        Converts:
        FIAT_500_Abarth_2012
        ->
        ("FIAT", "500 Abarth", "2012")
        """

        parts = vehicle_name.replace("_", " ").split()

        year = None
        if parts and parts[-1].isdigit():
            year = parts.pop()

        make = parts[0]
        model = " ".join(parts[1:])

        return make, model, year

    # ------------------------------------------------------------------
    # Public: Image Identification
    # ------------------------------------------------------------------

    async def identify_vehicle(
        self,
        image_bytes: bytes,
        filename: str,
        session_id: Optional[str],
        language: Optional[str],
    ) -> Dict[str, Any]:
        """
        Full image-only identification pipeline.

        Flow:
        ConvNext → (confidence ≥ 0.80) → Groq Vision
                 → (Groq confident) → RAG context → Final answer
                 → (Groq uncertain) → Web Scraping → RAG update → Re-rank
                 → (confidence < 0.80) → Groq Vision direct
                                       → (still uncertain) → Google Lens
        """
        classification = await self._classify_image(image_bytes, filename)
        # Sanitize: ignore Swagger placeholder "string", detect from context
        detected_language = _sanitize_language(language)

        if classification.confidence >= CLASSIFICATION_CONFIDENCE_THRESHOLD:
            result = await self._pipeline_high_confidence(
                image_bytes=image_bytes,
                vehicle_name=classification.vehicle_name,
                classification=classification,
                question=None,
                session_id=session_id,
                language=detected_language,
            )
        else:
            result = await self._pipeline_low_confidence(
                image_bytes=image_bytes,
                filename=filename,
                question=None,
                session_id=session_id,
                language=detected_language,
            )

        await self._persist_result(result, session_id)
        return self._serialize_result(result)

    async def identify_with_question(
        self,
        image_bytes: bytes,
        filename: str,
        question: str,
        intent: Intent,
        session_id: Optional[str],
        language: Optional[str],
    ) -> Dict[str, Any]:
        """
        Image + Question pipeline.

        Classifies the vehicle first, then routes the question through
        the appropriate handler based on intent and confidence.
        """
        classification = await self._classify_image(image_bytes, filename)
        # Sanitize language; auto-detect from question text if not explicit
        detected_language = _sanitize_language(language, hint_text=question)

        if classification.confidence >= CLASSIFICATION_CONFIDENCE_THRESHOLD:
            result = await self._pipeline_high_confidence(
                image_bytes=image_bytes,
                vehicle_name=classification.vehicle_name,
                classification=classification,
                question=question,
                session_id=session_id,
                language=detected_language,
            )
        else:
            result = await self._pipeline_low_confidence(
                image_bytes=image_bytes,
                filename=filename,
                question=question,
                session_id=session_id,
                language=detected_language,
            )

        await self._persist_result(result, session_id)
        return self._serialize_result(result)

    async def identify_via_google_lens(
        self,
        image_bytes: bytes,
        filename: str,
        session_id: Optional[str],
        language: Optional[str],
    ) -> Dict[str, Any]:
        """
        Direct Google Lens identification (explicit route from controller).
        """
        vehicle_name = await self._run_google_lens(image_bytes, filename)
        detected_language = language or "auto"

        if vehicle_name:
            result = await self._pipeline_from_vehicle_name(
                vehicle_name=vehicle_name,
                question=None,
                session_id=session_id,
                language=detected_language,
                source="google_lens",
            )
        else:
            result = PipelineResult(
                answer=self._fallback_message(detected_language),
                vehicle_name=None,
                confidence=0.0,
                language=detected_language,
                source="fallback",
            )

        await self._persist_result(result, session_id)
        return self._serialize_result(result)

    # ------------------------------------------------------------------
    # Public: Text Q&A
    # ------------------------------------------------------------------

    async def answer_question(
        self,
        question: str,
        intent: Intent,
        route: Route,
        session_id: Optional[str],
        vehicle_context: Optional[str],
        language: Optional[str],
    ) -> Dict[str, Any]:
        """
        Text-only Q&A pipeline.

        Routing order:
        1. RAG (if confidence ≥ threshold) → return directly.
        2. Web Scraping → update RAG → re-retrieve.
        3. Direct Groq generation with whatever context is available.
        """
        session_ctx = await self._session_memory.get_context(session_id) if session_id else {}
        detected_language = language or "auto"

        # Step 1: RAG attempt
        rag_result = await self._rag_pipeline.retrieve_and_generate(
            question=question,
            vehicle_context=vehicle_context or session_ctx.get("last_vehicle"),
            session_context=session_ctx,
            language=detected_language,
        )

        if rag_result.confidence >= RAG_CONFIDENCE_THRESHOLD:
            ranked = await self._ranking.rank_answer(rag_result)
            result = PipelineResult(
                answer=ranked.answer,
                vehicle_name=vehicle_context or session_ctx.get("last_vehicle"),
                confidence=ranked.confidence,
                language=ranked.language,
                source="rag",
                sources_cited=ranked.sources,
            )
        else:
            # Step 2: Web scrape for more context
            if vehicle_context or session_ctx.get("last_vehicle"):
                vehicle_name = vehicle_context or session_ctx.get("last_vehicle")
                await self._scrape_and_ingest(vehicle_name)

            # Step 3: Re-retrieve from updated RAG
            rag_result2 = await self._rag_pipeline.retrieve_and_generate(
                question=question,
                vehicle_context=vehicle_context or session_ctx.get("last_vehicle"),
                session_context=session_ctx,
                language=detected_language,
            )
            ranked = await self._ranking.rank_answer(rag_result2)
            result = PipelineResult(
                answer=ranked.answer if ranked.confidence >= 0.50 else self._fallback_message(detected_language),
                vehicle_name=vehicle_context or session_ctx.get("last_vehicle"),
                confidence=ranked.confidence,
                language=ranked.language,
                source="web+rag" if ranked.confidence >= 0.50 else "fallback",
                sources_cited=ranked.sources,
                web_scraped=True,
            )

        await self._session_memory.add_turn(
            session_id=session_id,
            user_message=question,
            assistant_message=result.answer,
            metadata={
                "source": result.source,
                "confidence": result.confidence,
                "language": result.language,
            },
        )
        return self._serialize_result(result)

    async def handle_disagreement(
        self,
        session_id: str,
        original_question: str,
        disputed_answer: str,
        user_claim: Optional[str],
        language: Optional[str],
    ) -> Dict[str, Any]:
        """
        Disagreement re-evaluation pipeline.

        1. Pull session and vehicle context.
        2. Search internal RAG knowledge.
        3. Search MongoDB.
        4. If uncertain → Web Scrape.
        5. Compare evidence.
        6. Return evidence-backed answer; if sources conflict, explain conflict.
        """
        detected_language = language or "auto"
        session_ctx = await self._session_memory.get_context(session_id)
        vehicle_name = session_ctx.get("last_vehicle")

        evidence_sources: List[Dict[str, Any]] = []

        # Internal RAG search
        rag_result = await self._rag_pipeline.retrieve_and_generate(
            question=original_question,
            vehicle_context=vehicle_name,
            session_context=session_ctx,
            language=detected_language,
        )
        if rag_result.confidence > 0.3:
            evidence_sources.append({
                "source": "rag",
                "answer": rag_result.answer,
                "confidence": rag_result.confidence,
            })

        # MongoDB search
        mongo_results = await self._vehicle_memory.search_knowledge(
            vehicle_name=vehicle_name, query=original_question
        )
        if mongo_results:
            evidence_sources.extend(mongo_results)

        # Web scrape if still uncertain
        if not evidence_sources or max(e["confidence"] for e in evidence_sources) < 0.70:
            if vehicle_name:
                await self._scrape_and_ingest(vehicle_name)
                rag_result2 = await self._rag_pipeline.retrieve_and_generate(
                    question=original_question,
                    vehicle_context=vehicle_name,
                    session_context=session_ctx,
                    language=detected_language,
                )
                evidence_sources.append({
                    "source": "web+rag",
                    "answer": rag_result2.answer,
                    "confidence": rag_result2.confidence,
                })

        final_answer = await self._ranking.synthesize_evidence(
            original_question=original_question,
            disputed_answer=disputed_answer,
            user_claim=user_claim,
            evidence=evidence_sources,
            language=detected_language,
        )

        return {
            "status": "re_evaluated",
            "answer": final_answer.answer,
            "confidence": final_answer.confidence,
            "language": final_answer.language,
            "sources": final_answer.sources,
            "conflict_detected": final_answer.conflict_detected,
            "conflict_explanation": final_answer.conflict_explanation,
        }

    # ------------------------------------------------------------------
    # Private: Pipeline Branches
    # ------------------------------------------------------------------

    async def _pipeline_high_confidence(
        self,
        image_bytes: bytes,
        vehicle_name: str,
        classification: ClassificationResult,
        question: Optional[str],
        session_id: Optional[str],
        language: str,
    ) -> PipelineResult:
        # ── Task 2: Check MongoDB first ──────────────────────────────────
        mongo_hit = await self._get_mongo_vehicle(vehicle_name)

        if mongo_hit and _has_usable_specs(mongo_hit):
            logger.info("Mongo hit: %s", vehicle_name)
            price_stale = self._is_price_stale(mongo_hit)
            force_price = question and any(
                kw in question.lower() for kw in
                ["latest price", "current price", "check price", "أحدث سعر", "السعر الحالي"]
            )

            if price_stale or force_price:
                logger.info("Price cache expired — running price-only scraper for: %s", vehicle_name)
                price_data = await self._scrape_price_only(vehicle_name)
                if price_data and price_data.get("price"):
                    await self._vehicle_memory.update_price(vehicle_name, price_data)
                    mongo_hit.update(price_data)
                    logger.info("Price updated in Mongo for: %s → %s", vehicle_name, price_data.get("price"))
            else:
                logger.info("Price cache valid for: %s", vehicle_name)

            answer = self._build_answer_from_mongo(mongo_hit, question, language)
            return PipelineResult(
                answer=answer,
                vehicle_name=vehicle_name,
                confidence=0.92,
                language=language,
                source="mongodb",
                classification_confidence=classification.confidence,
            )

        if mongo_hit and not _has_usable_specs(mongo_hit):
            logger.info(
                "Mongo doc for '%s' exists but has no usable specs — treating as miss and re-scraping.",
                vehicle_name,
            )

        # ── Mongo miss (or spec-less shell doc) → Groq Vision then decide on scraping ─
        logger.info("Mongo miss — calling Groq Vision for: %s", vehicle_name)
        groq_result = await self._call_groq_vision(
            image_bytes=image_bytes,
            vehicle_name=vehicle_name,
            question=question,
            language=language,
        )

        if groq_result.confidence >= GROQ_CONFIDENCE_THRESHOLD and not groq_result.needs_web_search:
            rag_context = await self._rag.enrich_with_context(
                vehicle_name=vehicle_name,
                raw_answer=groq_result.answer,
                language=language,
            )
            ranked = await self._ranking.rank_answer(rag_context)
            return PipelineResult(
                answer=ranked.answer,
                vehicle_name=vehicle_name,
                confidence=ranked.confidence,
                language=ranked.language,
                source="groq+rag",
                sources_cited=ranked.sources,
                classification_confidence=classification.confidence,
            )

        # Groq uncertain → full web scrape → save Mongo + FAISS
        logger.info("Running full scraper for: %s", vehicle_name)
        await self._scrape_and_ingest(vehicle_name)
        rag_result = await self._rag_pipeline.retrieve_and_generate(
            question=question or f"Tell me about the {vehicle_name}",
            vehicle_context=vehicle_name,
            session_context={},
            language=language,
        )
        ranked = await self._ranking.rank_answer(rag_result)
        return PipelineResult(
            answer=ranked.answer,
            vehicle_name=vehicle_name,
            confidence=ranked.confidence,
            language=ranked.language,
            source="groq+web+rag",
            sources_cited=ranked.sources,
            web_scraped=True,
            classification_confidence=classification.confidence,
        )

    async def _pipeline_low_confidence(
        self,
        image_bytes: bytes,
        filename: str,
        question: Optional[str],
        session_id: Optional[str],
        language: str,
    ) -> PipelineResult:
        # ── Task 3: Try Groq Vision directly ─────────────────────────────
        logger.info("Classification failed — trying Groq Vision directly.")
        groq_result = await self._call_groq_vision(
            image_bytes=image_bytes,
            vehicle_name=None,
            question=question,
            language=language,
        )

        if groq_result.confidence >= GROQ_CONFIDENCE_THRESHOLD:
            logger.info("Groq identified vehicle (low-conf path).")
            # Fix 3: _call_groq_vision now returns extracted vehicle name in sources_used[0]
            groq_vehicle = (
                groq_result.sources_used[0] if groq_result.sources_used
                else _extract_vehicle_name_from_text(groq_result.answer)
            )
            if groq_vehicle:
                logger.info("Groq extracted vehicle name: %s — checking Mongo.", groq_vehicle)
                return await self._pipeline_from_vehicle_name(
                    vehicle_name=groq_vehicle,
                    question=question,
                    session_id=session_id,
                    language=groq_result.language,
                    source="groq_vision",
                )
            return PipelineResult(
                answer=groq_result.answer,
                vehicle_name=None,
                confidence=groq_result.confidence,
                language=groq_result.language,
                source="groq_vision",
            )

        # ── Task 4: Fall back to Google Lens ─────────────────────────────
        logger.info("Groq failed — trying Google Lens.")
        vehicle_name = await self._run_google_lens(image_bytes, filename)
        if vehicle_name:
            logger.info("Google Lens identified vehicle: %s", vehicle_name)
            return await self._pipeline_from_vehicle_name(
                vehicle_name=vehicle_name,
                question=question,
                session_id=session_id,
                language=language,
                source="google_lens+web+rag",
            )

        logger.warning("All identification methods failed.")
        return PipelineResult(
            answer=self._fallback_message(language),
            vehicle_name=None,
            confidence=0.0,
            language=language,
            source="fallback",
        )

    async def _pipeline_from_vehicle_name(
        self,
        vehicle_name: str,
        question: Optional[str],
        session_id: Optional[str],
        language: str,
        source: str,
    ) -> PipelineResult:
        # ── Check Mongo first (Tasks 2/3/4 shared logic) ─────────────────
        mongo_hit = await self._get_mongo_vehicle(vehicle_name)

        if mongo_hit and _has_usable_specs(mongo_hit):
            logger.info("Mongo hit: %s", vehicle_name)
            price_stale = self._is_price_stale(mongo_hit)
            force_price = question and any(
                kw in question.lower() for kw in
                ["latest price", "current price", "check price", "أحدث سعر", "السعر الحالي"]
            )
            if price_stale or force_price:
                logger.info("Price cache expired — running price-only scraper for: %s", vehicle_name)
                price_data = await self._scrape_price_only(vehicle_name)
                if price_data and price_data.get("price"):
                    await self._vehicle_memory.update_price(vehicle_name, price_data)
                    mongo_hit.update(price_data)
            else:
                logger.info("Price cache valid for: %s", vehicle_name)

            answer = self._build_answer_from_mongo(mongo_hit, question, language)
            return PipelineResult(
                answer=answer,
                vehicle_name=vehicle_name,
                confidence=0.90,
                language=language,
                source=f"{source}+mongodb",
            )

        if mongo_hit and not _has_usable_specs(mongo_hit):
            logger.info(
                "Mongo doc for '%s' exists but has no usable specs — treating as miss and re-scraping.",
                vehicle_name,
            )

        # ── Mongo miss (or spec-less shell doc) → Full Web Scraping → save Mongo + FAISS ──
        logger.info("Mongo miss — running full scraper for: %s", vehicle_name)
        await self._scrape_and_ingest(vehicle_name)

        # Read back from Mongo to build a clean structured answer
        mongo_fresh = await self._get_mongo_vehicle(vehicle_name)
        if mongo_fresh and _has_usable_specs(mongo_fresh):
            logger.info("Using freshly scraped Mongo doc for answer: %s", vehicle_name)
            answer = self._build_answer_from_mongo(mongo_fresh, question, language)
            return PipelineResult(
                answer=answer,
                vehicle_name=vehicle_name,
                confidence=0.88,
                language=language,
                source=f"{source}+web",
                sources_cited=mongo_fresh.get("sources", [])[:3],
                web_scraped=True,
            )

        # Fallback to RAG if Mongo still empty (scraping may have failed validation)
        rag_result = await self._rag_pipeline.retrieve_and_generate(
            question=question or f"Tell me about the {vehicle_name}",
            vehicle_context=vehicle_name,
            session_context={},
            language=language,
        )
        ranked = await self._ranking.rank_answer(rag_result)
        return PipelineResult(
            answer=ranked.answer,
            vehicle_name=vehicle_name,
            confidence=ranked.confidence,
            language=ranked.language,
            source=source,
            sources_cited=ranked.sources,
            web_scraped=True,
        )

    # ------------------------------------------------------------------
    # Private: Sub-System Calls
    # ------------------------------------------------------------------

    async def _classify_image(
        self,
        image_bytes: bytes,
        filename: str,
    ) -> ClassificationResult:
        try:
            from io import BytesIO
            from PIL import Image

            image = Image.open(BytesIO(image_bytes)).convert("RGB")

            predictions = self.classifier.predict(image, top_k=5)

            top1 = predictions[0]

            return ClassificationResult(
                vehicle_name=top1.label,
                confidence=float(top1.score),
                top_predictions=[p.to_dict() for p in predictions],
            )

        except Exception as exc:
            logger.exception("Local classification failed: %s", exc)

            return ClassificationResult(
                vehicle_name="unknown",
                confidence=0.0,
                top_predictions=[],
            )

    async def _call_groq_vision(
        self,
        image_bytes: bytes,
        vehicle_name: Optional[str],
        question: Optional[str],
        language: str,
    ) -> GroqVisionResult:
        import os

        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            logger.error("GROQ_API_KEY not configured")
            return GroqVisionResult(
                answer="", confidence=0.0, language=language, needs_web_search=True
            )

        # Fix 2: detect language from the actual question text, not the form field value.
        # If the frontend sends "string" (Swagger default) or None, auto-detect from question.
        effective_language = language
        if not language or language in ("string", "auto", ""):
            effective_language = _detect_language(question or "", "en")

        encoded = base64.b64encode(image_bytes).decode("utf-8")
        system_prompt = _build_groq_system_prompt(effective_language)
        user_content = _build_groq_user_content(
            image_b64=encoded,
            vehicle_name=vehicle_name,
            question=question,
            language=effective_language,
        )

        payload = {
            "model": GROQ_VISION_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.2,
            "max_tokens": 2048,
        }

        try:
            response = await self._http.post(
                f"{GROQ_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=45.0,
            )
            response.raise_for_status()
            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]

            # Fix 1: strip <think> blocks and internal markers before returning.
            content = _strip_think_and_markers(raw_content)

            confidence = _extract_confidence_from_response(raw_content)  # markers still present here
            needs_web = _detect_uncertainty(raw_content)

            # Fix 2: detect language from the cleaned answer, fallback to question language.
            detected_lang = _detect_language(content, effective_language)

            # Fix 3: extract vehicle_name from the answer so downstream pipeline
            # can do Mongo lookup and price scraping even on the groq_vision path.
            extracted_name = vehicle_name or _extract_vehicle_name_from_text(content)

            return GroqVisionResult(
                answer=content,
                confidence=confidence,
                language=detected_lang,
                needs_web_search=needs_web,
                sources_used=[extracted_name] if extracted_name else [],
            )
        except Exception as exc:
            logger.error("Groq Vision API call failed: %s", exc)
            return GroqVisionResult(
                answer="", confidence=0.0, language=effective_language, needs_web_search=True
            )

    async def _run_google_lens(
        self, image_bytes: bytes, filename: str
    ) -> Optional[str]:
        # Task 1: Call GoogleLensClient directly — no microservice needed.
        if self._lens_client is None:
            logger.warning("Google Lens skipped: SERPAPI_KEY not configured.")
            return None
        try:
            from PIL import Image
            from io import BytesIO

            pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._lens_client.get_vehicle_info, pil_image
            )
            title = result.get("title") or ""
            if title:
                # Clean the raw Lens title before using it as vehicle_name
                clean = _clean_lens_title(title)
                if clean and _is_vehicle_name_valid(clean):
                    logger.info("Google Lens identified vehicle: %s (raw: %s)", clean, title)
                    return clean
                logger.warning(
                    "Google Lens title rejected as non-vehicle: %r (cleaned: %r)", title, clean
                )
            logger.warning("Google Lens returned no usable title (raw: %r).", title)
            return None
        except Exception as exc:
            logger.warning("Google Lens failed: %s", exc)
            return None

    async def _scrape_and_ingest(self, vehicle_name: str) -> None:

        try:
            make, model, year = self._parse_vehicle_name(vehicle_name)

            logger.info("Running full scraper: %s | %s | %s", make, model, year)

            scraped_data = await asyncio.to_thread(
                self.scraper.scrape_by_name,
                make,
                model,
                year
            )

            if not scraped_data:
                logger.warning("No scraped data returned for: %s", vehicle_name)
                return

            # ── Validate data before saving — reject corrupted entries ──────
            if not _is_scraped_data_valid(scraped_data):
                logger.warning(
                    "Scraped data for '%s' failed validation — skipping ingest "
                    "(corrupted values detected: hp=%s, fuel_economy=%s, description=%s)",
                    vehicle_name,
                    scraped_data.get("horsepower"),
                    scraped_data.get("fuel_economy"),
                    str(scraped_data.get("description", ""))[:50],
                )
                return

            logger.info("Saving to Mongo + FAISS: %s", vehicle_name)

            # Save to MongoDB via VehicleMemory
            await self._vehicle_memory.upsert(
                vehicle_name=vehicle_name,
                session_id=None,
                confidence=0.85,
                source="web_scraping",
                attributes=scraped_data,
                raw_context=str(scraped_data.get("description", "")),
            )

            await self._rag.ingest_scraped_data(
                vehicle_name=vehicle_name,
                documents=[scraped_data],
            )

            logger.info("Scrape and ingest completed for: %s", vehicle_name)

        except Exception as exc:
            logger.exception("_scrape_and_ingest failed for '%s': %s", vehicle_name, exc)
    # ------------------------------------------------------------------
    # Private: MongoDB + Cache Helpers (Tasks 2, 5, 6, 7)
    # ------------------------------------------------------------------

    async def _get_mongo_vehicle(self, vehicle_name: str) -> Optional[Dict[str, Any]]:
        """Return the MongoDB document for a vehicle, or None if not found."""
        try:
            results = await self._vehicle_memory.get_by_name(vehicle_name=vehicle_name, limit=1)
            return results[0] if results else None
        except Exception as exc:
            logger.warning("Mongo lookup failed for '%s': %s", vehicle_name, exc)
            return None

    @staticmethod
    def _is_price_stale(mongo_doc: Dict[str, Any]) -> bool:
        """Return True if price was not updated within PRICE_CACHE_DAYS."""
        from datetime import datetime, timezone, timedelta
        price_updated_at = mongo_doc.get("price_updated_at")
        if not price_updated_at:
            return True   # never set → treat as stale
        try:
            if isinstance(price_updated_at, str):
                ts = datetime.fromisoformat(price_updated_at)
            else:
                ts = price_updated_at
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - ts) > timedelta(days=PRICE_CACHE_DAYS)
        except Exception:
            return True

    async def _scrape_price_only(self, vehicle_name: str) -> Optional[Dict[str, Any]]:
        """
        Task 7 Mode 2: scrape ONLY price data for an existing vehicle.
        Returns dict with keys: price, avg_price, msrp, dealer_price, currency, sources
        """
        try:
            make, model, year = self._parse_vehicle_name(vehicle_name)
            logger.info("Price-only scrape: %s %s %s", make, model, year)

            loop = asyncio.get_event_loop()

            # Use price-specific search to get trusted URLs + snippets
            price_results = await loop.run_in_executor(
                None,
                lambda: self.scraper._search.search_vehicle_price(make, model, year, num_results=6),
            )

            if not price_results:
                logger.warning("Price search returned no results for: %s", vehicle_name)
                return None

            # Extract price info from snippets (fast — no page fetch needed)
            prices: list[str] = []
            sources: list[Dict[str, str]] = []

            for r in price_results:
                snippet = r.get("snippet", "")
                extracted = _extract_price_from_snippet(snippet)
                if extracted:
                    prices.append(extracted)
                sources.append({"url": r["link"], "title": r["title"], "domain": r["domain"]})

            # Also do a full scrape of the top price-domain URL for accuracy
            top_price_url = next(
                (r["link"] for r in price_results if r.get("is_price_domain")), None
            )
            scraped_price_doc = None
            if top_price_url:
                try:
                    scraped_price_doc = await loop.run_in_executor(
                        None,
                        lambda: self.scraper._process_url(top_price_url),
                    )
                except Exception as exc:
                    logger.warning("Price page scrape failed for %s: %s", top_price_url, exc)

            result: Dict[str, Any] = {"sources": sources}

            if scraped_price_doc:
                result["price"]        = scraped_price_doc.get("price") or (prices[0] if prices else None)
                result["msrp"]         = scraped_price_doc.get("msrp")
                result["dealer_price"] = scraped_price_doc.get("dealer_price")
                result["currency"]     = scraped_price_doc.get("currency", "USD")
            elif prices:
                result["price"]    = prices[0]
                result["currency"] = "USD"

            # Average market price from all snippets
            if len(prices) > 1:
                result["average_market_price"] = prices[0]  # best available

            if result.get("price"):
                logger.info("Price-only scrape result: %s (sources: %d)", result["price"], len(sources))
                return result

            logger.warning("Price-only scrape returned no price for: %s", vehicle_name)
            return None
        except Exception as exc:
            logger.warning("Price-only scrape failed for '%s': %s", vehicle_name, exc)
            return None

    @staticmethod
    def _build_answer_from_mongo(
        mongo_doc: Dict[str, Any],
        question: Optional[str],
        language: str,
    ) -> str:
        """
        Build a professionally structured vehicle information response
        from a MongoDB document — matching the required output format.
        """
        from datetime import datetime, timezone

        # ── Header ──────────────────────────────────────────────────────
        make  = mongo_doc.get("make", "")
        model = mongo_doc.get("model", "")
        year  = mongo_doc.get("year", "")
        name  = f"{year} {make} {model}".strip() if year else f"{make} {model}".strip()
        name  = name or mongo_doc.get("vehicle_name", "Unknown Vehicle")

        is_arabic = language and language.startswith("ar")
        sep = "================================"

        lines: list[str] = [f"🚗 **{name.upper()}**", sep, ""]

        # ── Basic Information ────────────────────────────────────────────
        section = "المعلومات الأساسية" if is_arabic else "Basic Information"
        lines.append(f"### {section}")
        basic = [
            ("Make", "الماركة",       make),
            ("Model", "الموديل",      model),
            ("Year", "السنة",         year),
            ("Generation", "الجيل",   mongo_doc.get("generation")),
            ("Trim", "الفئة",         mongo_doc.get("trim")),
            ("Body Type", "النوع",    mongo_doc.get("body_type")),
        ]
        for en, ar, val in basic:
            if val:
                label = ar if is_arabic else en
                lines.append(f"- **{label}:** {val}")
        lines.append("")

        # ── Specifications ───────────────────────────────────────────────
        section = "المواصفات التقنية" if is_arabic else "Specifications"
        lines.append(f"### {section}")
        specs = [
            ("Engine", "المحرك",              mongo_doc.get("engine")),
            ("Engine Code", "كود المحرك",     mongo_doc.get("engine_code")),
            ("Displacement", "سعة المحرك",    mongo_doc.get("displacement")),
            ("Horsepower", "القوة",            mongo_doc.get("horsepower")),
            ("Torque", "العزم",                mongo_doc.get("torque")),
            ("Cylinders", "الأسطوانات",       mongo_doc.get("cylinders")),
            ("Transmission", "ناقل الحركة",   mongo_doc.get("transmission")),
            ("Drive Type", "الدفع",            mongo_doc.get("drive") or mongo_doc.get("drive_type")),
            ("Fuel Type", "نوع الوقود",        mongo_doc.get("fuel_type")),
            ("Fuel Economy", "استهلاك الوقود", mongo_doc.get("fuel_economy")),
            ("Weight", "الوزن",                mongo_doc.get("weight")),
            ("Seating", "المقاعد",             mongo_doc.get("seating_capacity") or mongo_doc.get("seats")),
        ]
        for en, ar, val in specs:
            if val:
                label = ar if is_arabic else en
                lines.append(f"- **{label}:** {val}")

        dims = mongo_doc.get("dimensions", {})
        if isinstance(dims, dict) and dims:
            dim_label = "الأبعاد" if is_arabic else "Dimensions"
            lines.append(f"- **{dim_label}:** " + " | ".join(f"{k}: {v}" for k, v in list(dims.items())[:4]))
        lines.append("")

        # ── Description ─────────────────────────────────────────────────
        desc = mongo_doc.get("description", "")
        if desc:
            section = "الوصف" if is_arabic else "Description"
            lines.append(f"### {section}")
            lines.append(str(desc)[:600])
            lines.append("")

        # ── Features ────────────────────────────────────────────────────
        features = mongo_doc.get("features", [])
        if features:
            section = "المميزات" if is_arabic else "Features"
            lines.append(f"### {section}")
            for f in features[:15]:
                lines.append(f"• {f}")
            lines.append("")

        # ── Safety ──────────────────────────────────────────────────────
        safety_fields = [
            ("Safety Rating", "تقييم الأمان",    mongo_doc.get("safety_rating")),
            ("Euro NCAP", "Euro NCAP",            mongo_doc.get("euro_ncap")),
            ("ABS", "ABS",                        mongo_doc.get("abs")),
            ("ESC", "ESC",                        mongo_doc.get("esc")),
            ("Airbags", "الوسائد الهوائية",       mongo_doc.get("airbags")),
        ]
        safety_lines = [(ar if is_arabic else en, val) for en, ar, val in safety_fields if val]
        if safety_lines:
            section = "السلامة" if is_arabic else "Safety"
            lines.append(f"### {section}")
            for label, val in safety_lines:
                lines.append(f"- **{label}:** {val}")
            lines.append("")

        # ── Price ────────────────────────────────────────────────────────
        price          = mongo_doc.get("price")
        msrp           = mongo_doc.get("msrp")
        avg_price      = mongo_doc.get("average_market_price") or mongo_doc.get("avg_price")
        dealer_price   = mongo_doc.get("dealer_price")
        currency       = mongo_doc.get("currency", "USD")
        price_updated  = mongo_doc.get("price_updated_at", "")

        has_price = any([price, msrp, avg_price, dealer_price])
        if has_price:
            section = "السعر" if is_arabic else "Price"
            lines.append(f"### {section}")
            if msrp:
                label = "سعر الوكيل الرسمي" if is_arabic else "MSRP"
                lines.append(f"- **{label}:** {msrp} {currency}")
            if price:
                label = "السعر الحالي" if is_arabic else "Current Price"
                lines.append(f"- **{label}:** {price} {currency}")
            if avg_price:
                label = "متوسط السعر في السوق" if is_arabic else "Average Market Price"
                lines.append(f"- **{label}:** {avg_price} {currency}")
            if dealer_price:
                label = "سعر الوكيل" if is_arabic else "Dealer Price"
                lines.append(f"- **{label}:** {dealer_price} {currency}")

            if price_updated:
                try:
                    from datetime import datetime, timezone
                    ts = datetime.fromisoformat(str(price_updated))
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    days_ago = (datetime.now(timezone.utc) - ts).days
                    age = (
                        f"منذ {days_ago} {'يوم' if days_ago == 1 else 'أيام'}"
                        if is_arabic else
                        f"{days_ago} day{'s' if days_ago != 1 else ''} ago"
                    )
                    last_label = "آخر تحديث" if is_arabic else "Last Updated"
                    lines.append(f"- **{last_label}:** {age}")
                except Exception:
                    pass
            lines.append("")

            # Price refresh hint
            if is_arabic:
                lines.append("> 💡 **تريد أحدث سعر من السوق؟** أرسل: *\"اجيب أحدث سعر\"*")
            else:
                lines.append("> 💡 **Need the latest market price?** Ask: *\"check latest price\"*")
            lines.append("")

        # ── Sources ──────────────────────────────────────────────────────
        sources = mongo_doc.get("sources", [])
        if sources:
            section = "المصادر" if is_arabic else "Sources"
            lines.append(f"### {section}")
            for src in sources[:5]:
                if isinstance(src, dict):
                    url = src.get("url", "")
                    title = src.get("title", "") or src.get("domain", "")
                    if url:
                        label = title or url.split("/")[2] if "//" in url else url
                        lines.append(f"- [{label}]({url})")
                elif isinstance(src, str) and src.startswith("http"):
                    domain = src.split("/")[2] if "//" in src else src
                    lines.append(f"- [{domain}]({src})")
            lines.append("")

        # ── Last Updated timestamps ───────────────────────────────────────
        specs_updated = mongo_doc.get("specs_updated_at", "")
        price_updated = mongo_doc.get("price_updated_at", "")
        if specs_updated or price_updated:
            section = "تواريخ التحديث" if is_arabic else "Last Updated"
            lines.append(f"### {section}")
            if specs_updated:
                label = "تحديث المواصفات" if is_arabic else "Specifications Updated"
                try:
                    d = str(specs_updated)[:10]
                    lines.append(f"- **{label}:** {d}")
                except Exception:
                    pass
            if price_updated:
                label = "تحديث السعر" if is_arabic else "Price Updated"
                try:
                    d = str(price_updated)[:10]
                    lines.append(f"- **{label}:** {d}")
                except Exception:
                    pass

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private: Persistence and Serialization
    # ------------------------------------------------------------------

    async def _persist_result(
        self, result: PipelineResult, session_id: Optional[str]
    ) -> None:
        if result.vehicle_name and result.vehicle_name != "unknown":
            await self._vehicle_memory.upsert(
                vehicle_name=result.vehicle_name,
                session_id=session_id,
                confidence=result.confidence,
                source=result.source,
            )

        if session_id:
            await self._session_memory.set_last_vehicle(
                session_id=session_id,
                vehicle_name=result.vehicle_name,
            )

    def _serialize_result(self, result: PipelineResult) -> Dict[str, Any]:
        return {
            "answer": result.answer,
            "vehicle_name": result.vehicle_name,
            "confidence": round(result.confidence, 4),
            "language": result.language,
            "source": result.source,
            "sources_cited": result.sources_cited,
            "web_scraped": result.web_scraped,
            "classification_confidence": (
                round(result.classification_confidence, 4)
                if result.classification_confidence is not None
                else None
            ),
        }

    def _fallback_message(self, language: str) -> str:
        if language and language.startswith("ar"):
            return (
                "عذراً، لم أتمكن من التعرف على هذه السيارة بدقة كافية. "
                "يُرجى تحميل صورة أوضح أو ذكر اسم السيارة مباشرةً."
            )
        return (
            "I was unable to identify this vehicle with sufficient confidence. "
            "Please upload a clearer image or provide the vehicle name directly."
        )



# ---------------------------------------------------------------------------
# Private: Data Validation
# ---------------------------------------------------------------------------

# Fields that indicate a Mongo document actually contains usable vehicle
# specs, as opposed to a bare bookkeeping shell created by _persist_result()
# (which only ever writes vehicle_name/confidence/source/timestamps).
_SPEC_INDICATOR_FIELDS = (
    "make", "model", "engine", "horsepower", "transmission",
    "body_type", "fuel_type", "description", "features",
)


def _has_usable_specs(mongo_doc: Optional[Dict[str, Any]]) -> bool:
    """
    Return True only if the document has real vehicle specs — not just a
    bookkeeping shell (vehicle_name/confidence/source/timestamps/price with
    nothing else). A doc with only price fields is NOT considered a usable
    "hit" for answering spec questions; the pipeline should keep trying to
    scrape real data instead of treating it as done.
    """
    if not mongo_doc:
        return False
    if any(mongo_doc.get(f) for f in _SPEC_INDICATOR_FIELDS):
        return True
    attrs = mongo_doc.get("attributes") or {}
    return bool(attrs)


def _is_scraped_data_valid(data: Dict[str, Any]) -> bool:
    """
    Reject obviously corrupted scrape results before saving to MongoDB/FAISS.

    Corruption patterns seen in production:
    - horsepower = "500 hp" for a C200 (should be ~204 hp)
    - fuel_economy = "5 mpg" (impossible for any road car)
    - fuel_type = "5" (numeric, not a fuel type)
    - description contains "Access denied" or permission errors
    - make/model is a non-vehicle string (photo title, article title, etc.)
    """
    import re

    description = str(data.get("description", "")).lower()
    # Reject access-denied descriptions
    if any(kw in description for kw in [
        "access denied", "permission", "403 forbidden",
        "subscribe", "sign in to view", "login required",
    ]):
        return False

    # Reject descriptions that are clearly non-vehicle content
    non_vehicle_keywords = [
        "rusty burnt", "war zone", "evacuate", "military",
        "photography", "urbex", "adobe stock", "shutterstock",
        "alamy", "gettyimages", "istockphoto", "pixels",
        "charbonnage", "scholzdigital",
    ]
    if any(kw in description for kw in non_vehicle_keywords):
        return False

    # Reject corrupted numeric specs
    hp_raw = str(data.get("horsepower", "")).lower().replace(",", "")
    hp_match = re.search(r"(\d+)", hp_raw)
    if hp_match:
        hp_val = int(hp_match.group(1))
        if hp_val > 2000 or hp_val < 1:   # no road car has >2000 hp or <1 hp
            return False

    fuel_eco = str(data.get("fuel_economy", "")).strip()
    if fuel_eco and re.match(r"^[1-9]$", fuel_eco):   # "5" alone is not mpg
        return False

    fuel_type = str(data.get("fuel_type", "")).strip()
    if fuel_type and re.match(r"^\d+$", fuel_type):   # "5" is not a fuel type
        return False

    # Must have at least a make or description to be useful
    make = str(data.get("make", "")).strip()
    if not make and not description:
        return False

    return True


def _is_vehicle_name_valid(name: str) -> bool:
    """
    Check if a string from Google Lens / Groq is actually a vehicle name
    and not a photo caption, article title, or place name.

    Returns True only if the name contains a known make or year + model pattern.
    """
    import re

    if not name or len(name) < 3:
        return False

    # Reject if too long (photo captions are usually long)
    if len(name) > 80:
        return False

    # Reject known non-vehicle patterns
    reject_patterns = [
        r"\b(rusty|burnt|destroyed|wreck|junkyard|scrap)\b",
        r"\b(photography|photo|image|stock|shutterstock|alamy|getty)\b",
        r"\b(urbex|charbonnage|renard|scholz)\b",
        r"\b(war|military|ukraine|irpen|russia)\b",
        r"\bafter being\b",
        r"\ba lot of\b",
        r"[|•●–—]{1}",   # photo title separators
    ]
    name_lower = name.lower()
    for pattern in reject_patterns:
        if re.search(pattern, name_lower, re.IGNORECASE):
            return False

    # Accept if it contains a year
    if re.search(r"\b(19|20)\d{2}\b", name):
        return True

    # Accept if it contains a known make
    known_makes = (
        "toyota|honda|bmw|mercedes|ford|chevrolet|audi|volkswagen|vw|"
        "hyundai|kia|nissan|mazda|subaru|jeep|dodge|ram|gmc|cadillac|"
        "lexus|infiniti|acura|volvo|porsche|ferrari|lamborghini|mclaren|"
        "tesla|rivian|lucid|fiat|alfa|peugeot|renault|seat|skoda|opel|"
        "mitsubishi|suzuki|land rover|range rover|jaguar|mini|bentley|"
        "rolls-royce|maserati|genesis|haval|mg|byd|chery|geely|dacia"
    )
    if re.search(rf"\b({known_makes})\b", name_lower):
        return True

    return False


# ---------------------------------------------------------------------------
# Private: Language Sanitization
# ---------------------------------------------------------------------------

def _sanitize_language(language: Optional[str], hint_text: Optional[str] = None) -> str:
    """
    Returns a clean language code ("ar" / "en" / "auto").

    Rejects placeholder values like "string" that come from Swagger UI defaults.
    Falls back to detecting language from hint_text (e.g. the user's question).
    """
    if language and language not in ("string", "auto", ""):
        return language   # explicit clean value — use it
    if hint_text:
        return _detect_language(hint_text, "auto")
    return "auto"


# ---------------------------------------------------------------------------
# Private: Response Cleaning
# ---------------------------------------------------------------------------

def _strip_think_and_markers(content: str) -> str:
    """
    Fix 1: Remove Qwen <think>…</think> blocks and internal pipeline markers
    before the answer is returned to the user.
    """
    import re
    # Remove well-formed <think>...</think> blocks
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)
    # Defensive: if a <think> was opened but truncation meant it never closed,
    # drop everything from the opening tag onward instead of leaking raw
    # reasoning to the user.
    if re.search(r"<think>", content, re.IGNORECASE):
        content = re.split(r"<think>", content, flags=re.IGNORECASE)[0]
    # Remove pipeline markers
    content = re.sub(r"\[CONFIDENCE:\s*[0-9.]+\]", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\[CONFLICT_DETECTED:\s*(YES|NO)\]", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\[NEEDS_WEB_SEARCH\]", "", content, flags=re.IGNORECASE)
    return content.strip()


# ---------------------------------------------------------------------------
# Private: Vehicle Name Extraction from Groq text (English + Arabic)
# ---------------------------------------------------------------------------

_MAKES = (
    "Toyota|Honda|BMW|Mercedes|Mercedes-Benz|Ford|Chevrolet|Audi|Volkswagen|VW|"
    "Hyundai|Kia|Nissan|Mazda|Subaru|Jeep|Dodge|Ram|GMC|Cadillac|Lexus|Infiniti|"
    "Acura|Volvo|Porsche|Ferrari|Lamborghini|McLaren|Tesla|Rivian|Lucid|Fiat|"
    "Alfa Romeo|Peugeot|Renault|Citroën|Seat|Skoda|Opel|Lada|Mitsubishi|Suzuki|"
    "Dacia|Land Rover|Range Rover|Jaguar|Mini|Bentley|Rolls-Royce|Maserati|"
    "Bugatti|Aston Martin|Genesis|Haval|MG|BYD|Chery|Geely"
)

# Arabic make name → English equivalent (compound names must come BEFORE single words)
_AR_MAKES: dict[str, str] = {
    # Compound names first (longer match wins)
    "مرسيدس بنز": "Mercedes-Benz",
    "بي إم دبليو": "BMW",
    "لاند روفر": "Land Rover",
    "رنج روفر": "Range Rover",
    "ألفا روميو": "Alfa Romeo",
    "رولز رويس": "Rolls-Royce",
    # Single names
    "مرسيدس": "Mercedes-Benz",
    "تويوتا": "Toyota",
    "هوندا": "Honda",
    "فورد": "Ford",
    "شيفروليه": "Chevrolet",
    "أودي": "Audi",
    "فولكسواجن": "Volkswagen",
    "هيونداي": "Hyundai",
    "كيا": "Kia",
    "نيسان": "Nissan",
    "مازدا": "Mazda",
    "سوبارو": "Subaru",
    "جيب": "Jeep",
    "لكزس": "Lexus",
    "بورش": "Porsche",
    "فيراري": "Ferrari",
    "لامبورغيني": "Lamborghini",
    "تسلا": "Tesla",
    "فولفو": "Volvo",
    "ميتسوبيشي": "Mitsubishi",
    "سوزوكي": "Suzuki",
    "إنفينيتي": "Infiniti",
    "لينكولن": "Lincoln",
    "شيري": "Chery",
    "هافال": "Haval",
    "بي واي دي": "BYD",
}


def _extract_vehicle_name_from_text(text: str) -> Optional[str]:
    """
    Extract vehicle make+model from Groq answer (English or Arabic).
    Returns clean vehicle name or None.
    """
    import re

    # ── Arabic path: try compound names first (longest match) ────────────
    for ar_make in sorted(_AR_MAKES, key=len, reverse=True):
        if ar_make not in text:
            continue
        en_make = _AR_MAKES[ar_make]

        # Common Arabic model descriptors → English model names
        ar_model_map = {
            "الفئة C": "C-Class",
            "الفئة E": "E-Class",
            "الفئة S": "S-Class",
            "الفئة A": "A-Class",
            "الفئة G": "G-Class",
            "الفئة M": "M-Class",
            "الفئة CLA": "CLA",
            "الفئة GLE": "GLE",
            "الفئة GLC": "GLC",
        }
        model_part = None
        for ar_model, en_model in ar_model_map.items():
            if ar_model in text:
                model_part = en_model
                break

        if not model_part:
            # Look for English model code directly after make (e.g. "مرسيدس X5")
            after_make = text[text.index(ar_make) + len(ar_make):].strip()
            m = re.match(r"([A-Z][A-Z0-9\-]{1,10})", after_make)
            if m:
                model_part = m.group(1)

        year_m = re.search(r"\b(20\d{2}|19\d{2})\b", text)
        year = year_m.group(1) if year_m else ""

        # Build clean English-only result
        parts = [en_make]
        if model_part:
            parts.append(model_part)
        if year:
            parts.append(year)
        return " ".join(parts)

    # ── English path: Year Make Model ────────────────────────────────────
    m = re.search(
        rf"\b(20\d{{2}}|19\d{{2}})\s+({_MAKES})[·\-\s]+([\w][\w\s\-]{{1,25}})",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"{m.group(2)} {m.group(3).strip()} {m.group(1)}".strip()

    # ── English path: Make Model (no year) ───────────────────────────────
    m = re.search(
        rf"\b({_MAKES})\s+([\w][\w\s\-]{{1,25}})",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"{m.group(1)} {m.group(2).strip()}".strip()

    return None


def _clean_lens_title(raw_title: str) -> Optional[str]:
    """
    Clean a Google Lens raw title into a usable vehicle name.

    Examples:
      "2020 Mercedes-Benz C-Class C 200 Auto🔥! | 117,560km Service ..."
      → "Mercedes-Benz C-Class 2020"

      "Toyota Camry XSE 2022 – Full Review"
      → "Toyota Camry 2022"
    """
    import re

    # Remove emoji, pipe sections, and common noise after | or –
    clean = re.split(r"[|–—●•]", raw_title)[0]

    # Remove emojis
    clean = re.sub(
        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
        r"\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
        r"\u2600-\u26FF\u2700-\u27BF]+",
        "", clean,
    )

    # Remove mileage / km patterns
    clean = re.sub(r"\d[\d,]*\s*km\b", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\d[\d,]*\s*miles?\b", "", clean, flags=re.IGNORECASE)

    # Remove "Auto", "Manual", "for sale", "review", "test drive" suffixes
    clean = re.sub(
        r"\b(Auto|Manual|For Sale|Full Review|Test Drive|Review|Used|New|Service)\b.*",
        "", clean, flags=re.IGNORECASE,
    )

    clean = clean.strip(" -!?,.")

    # Now extract make + model + year from the cleaned string
    result = _extract_vehicle_name_from_text(clean)
    if result:
        return result

    # Fallback: if clean string is short and looks like a name, use it
    if 4 < len(clean) < 60:
        return clean

    return None


# ---------------------------------------------------------------------------
# Private: Price Extraction from Search Snippets
# ---------------------------------------------------------------------------

def _extract_price_from_snippet(snippet: str) -> Optional[str]:
    """
    Extract a price string from a Google Search snippet.
    Examples:
      "Starting at $32,900 MSRP"  → "$32,900"
      "Used from £18,500"          → "£18,500"
      "EGP 1,850,000"              → "EGP 1,850,000"
    """
    import re
    patterns = [
        r"(?:starting at\s*)?(\$[\d,]+(?:\.\d{2})?)",       # $32,900
        r"(£[\d,]+(?:\.\d{2})?)",                            # £18,500
        r"(€[\d,]+(?:\.\d{2})?)",                            # €28,000
        r"(EGP\s*[\d,]+)",                                   # EGP 1,850,000
        r"(SAR\s*[\d,]+)",                                   # SAR 85,000
        r"(AED\s*[\d,]+)",                                   # AED 95,000
        r"([\d,]+)\s*(?:USD|EUR|GBP|EGP|SAR|AED)\b",       # 32900 USD
    ]
    for pattern in patterns:
        m = re.search(pattern, snippet, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return None


# ---------------------------------------------------------------------------
# Private Prompt Helpers
# ---------------------------------------------------------------------------

def _build_groq_system_prompt(language: str) -> str:
    lang_instruction = (
        "Respond in Arabic (Egyptian dialect is acceptable)."
        if language and language.startswith("ar")
        else "Respond in English."
        if language and language.startswith("en")
        else (
            "Detect the user's language from their question and respond in the same language. "
            "If the image has no question, respond in English."
        )
    )
    return f"""You are an expert automotive AI assistant specialized in vehicle identification and information.

{lang_instruction}

Rules:
- Identify the exact vehicle make, model, and year when visible.
- Provide structured information: specs, features, price range, engine, safety rating.
- If you are uncertain about the vehicle identity, say so explicitly and include the phrase [NEEDS_WEB_SEARCH].
- Include a self-assessed confidence score at the end of your response in the format: [CONFIDENCE: 0.XX]
- Never hallucinate vehicle specifications. If you do not know something, say so.
- Be concise and factual."""


def _build_groq_user_content(
    image_b64: str,
    vehicle_name: Optional[str],
    question: Optional[str],
    language: str,
) -> list:
    parts = []

    if vehicle_name:
        parts.append({
            "type": "text",
            "text": f"The classification model identified this as: {vehicle_name}. "
                    "Please verify this identification from the image and provide detailed information.",
        })

    parts.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
    })

    if question:
        parts.append({"type": "text", "text": question})
    elif not vehicle_name:
        parts.append({
            "type": "text",
            "text": "Please identify this vehicle and provide comprehensive information about it.",
        })

    return parts


def _extract_confidence_from_response(content: str) -> float:
    import re
    match = re.search(r"\[CONFIDENCE:\s*([0-9.]+)\]", content, re.IGNORECASE)
    if match:
        try:
            return min(1.0, max(0.0, float(match.group(1))))
        except ValueError:
            pass
    return 0.65  # default when not explicitly stated


def _detect_uncertainty(content: str) -> bool:
    uncertainty_markers = [
        "[NEEDS_WEB_SEARCH]",
        "I'm not sure",
        "I cannot identify",
        "unclear",
        "uncertain",
        "لست متأكد",
        "لا أستطيع التعرف",
    ]
    content_lower = content.lower()
    return any(marker.lower() in content_lower for marker in uncertainty_markers)


def _detect_language(content: str, fallback: str) -> str:
    arabic_chars = sum(1 for c in content if "\u0600" <= c <= "\u06ff")
    total_alpha = sum(1 for c in content if c.isalpha())
    if total_alpha > 0 and arabic_chars / total_alpha > 0.3:
        return "ar"
    return fallback if fallback and fallback != "auto" else "en"