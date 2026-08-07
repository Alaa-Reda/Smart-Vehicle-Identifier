"""
Query Router
============
Decides which subsystem should handle a given query.

Routes:
- RAG_ONLY       → Answer directly from vector store
- GROQ_DIRECT    → Send straight to Groq with no retrieval
- WEB_FIRST      → Scrape web first, then RAG
- HYBRID         → RAG + Web in parallel
- COMPARISON     → Route to CompareService
- GOOGLE_LENS    → Route to Google Lens
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from ranking.intent_classifier import Intent


class Route(str, Enum):
    RAG_ONLY = "rag_only"
    GROQ_DIRECT = "groq_direct"
    WEB_FIRST = "web_first"
    HYBRID = "hybrid"
    COMPARISON = "comparison"
    GOOGLE_LENS = "google_lens"


class QueryRouter:

    async def route(
        self,
        question: str,
        intent: Intent,
        vehicle_context: Optional[str],
        session_id: Optional[str],
    ) -> Route:
        if intent == Intent.COMPARE_VEHICLES:
            return Route.COMPARISON

        if intent == Intent.IDENTIFY_VEHICLE and not vehicle_context:
            return Route.GOOGLE_LENS

        if intent in {Intent.GET_PRICE, Intent.GET_SPECS, Intent.GET_FEATURES}:
            # These change frequently — prefer fresh web data
            return Route.WEB_FIRST if vehicle_context else Route.HYBRID

        if intent == Intent.DISAGREEMENT:
            return Route.HYBRID

        if intent == Intent.OFF_TOPIC:
            return Route.GROQ_DIRECT

        # Default: try RAG first
        return Route.RAG_ONLY
