"""
Search Service
==============
Unified search layer across MongoDB, FAISS vector store, and the web.

Responsibilities:
- MongoDB full-text search.
- FAISS semantic/vector search.
- Web search via SerpAPI.
- Google Lens image search.
- Hybrid retrieval (combining all sources).
- Result deduplication and re-ranking.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

SERP_API_BASE = "https://serpapi.com/search"
WEB_SCRAPING_API_URL = "http://localhost:8003/scrape"


@dataclass
class SearchResult:
    source: str            # mongodb | faiss | web | google_lens
    content: str
    vehicle_name: Optional[str]
    score: float           # relevance score 0.0 → 1.0
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SearchService:
    """
    Unified search service used by controllers and the RAG pipeline.
    """

    def __init__(self) -> None:
        self._http = httpx.AsyncClient(timeout=30.0)
        self._serp_key = os.environ.get("SERP_API_KEY", "")

    async def hybrid_search(
        self,
        query: str,
        vehicle_context: Optional[str] = None,
        top_k: int = 10,
    ) -> List[SearchResult]:
        """
        Hybrid search: MongoDB + FAISS + Web in parallel.
        Results are merged, deduplicated, and ranked by score.
        """
        import asyncio

        tasks = [
            self.search_mongodb(query=query, vehicle_context=vehicle_context, limit=top_k),
            self.search_faiss(query=query, top_k=top_k),
        ]

        if self._serp_key:
            tasks.append(self.search_web(query=query, vehicle_context=vehicle_context))

        results_groups = await asyncio.gather(*tasks, return_exceptions=True)

        merged: List[SearchResult] = []
        for group in results_groups:
            if isinstance(group, Exception):
                logger.warning("Search source failed: %s", group)
                continue
            merged.extend(group)

        return self._deduplicate_and_rank(merged, top_k=top_k)

    async def search_mongodb(
        self,
        query: str,
        vehicle_context: Optional[str] = None,
        limit: int = 10,
    ) -> List[SearchResult]:
        """
        Full-text search over MongoDB vehicle collection.
        """
        try:
            from memory.vehicle_memory import VehicleMemory
            vm = VehicleMemory()
            results = await vm.search_knowledge(
                vehicle_name=vehicle_context, query=query
            )
            return [
                SearchResult(
                    source="mongodb",
                    content=r.get("raw_context", ""),
                    vehicle_name=r.get("vehicle_name"),
                    score=r.get("score", 0.5),
                    metadata=r,
                )
                for r in results[:limit]
            ]
        except Exception as exc:
            logger.warning("MongoDB search failed: %s", exc)
            return []

    async def search_faiss(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[SearchResult]:
        """
        Semantic vector search over FAISS index.
        """
        try:
            from rag.retriever import Retriever
            retriever = Retriever()
            docs = await retriever.retrieve(query=query, top_k=top_k)
            return [
                SearchResult(
                    source="faiss",
                    content=doc.content,
                    vehicle_name=doc.metadata.get("vehicle_name"),
                    score=doc.score,
                    metadata=doc.metadata,
                )
                for doc in docs
            ]
        except Exception as exc:
            logger.warning("FAISS search failed: %s", exc)
            return []

    async def search_web(
        self,
        query: str,
        vehicle_context: Optional[str] = None,
        num_results: int = 5,
    ) -> List[SearchResult]:
        """
        Web search via SerpAPI.
        """
        if not self._serp_key:
            logger.warning("SERP_API_KEY not set — web search disabled")
            return []

        search_query = f"{vehicle_context} {query}" if vehicle_context else query

        try:
            response = await self._http.get(
                SERP_API_BASE,
                params={
                    "q": search_query,
                    "api_key": self._serp_key,
                    "num": num_results,
                    "engine": "google",
                },
                timeout=20.0,
            )
            response.raise_for_status()
            data = response.json()
            organic = data.get("organic_results", [])

            return [
                SearchResult(
                    source="web",
                    content=item.get("snippet", ""),
                    vehicle_name=vehicle_context,
                    score=0.6,
                    url=item.get("link"),
                    metadata={"title": item.get("title", "")},
                )
                for item in organic[:num_results]
            ]
        except Exception as exc:
            logger.warning("SerpAPI search failed: %s", exc)
            return []

    async def search_google_lens(
        self,
        image_bytes: bytes,
        filename: str,
    ) -> List[SearchResult]:
        """
        Image-based search via Google Lens (SerpAPI).
        """
        if not self._serp_key:
            logger.warning("SERP_API_KEY not set — Google Lens disabled")
            return []

        try:
            import base64
            encoded = base64.b64encode(image_bytes).decode("utf-8")
            response = await self._http.post(
                "http://localhost:8002/lens",
                json={"image_base64": encoded, "filename": filename},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            return [
                SearchResult(
                    source="google_lens",
                    content=r.get("title", ""),
                    vehicle_name=r.get("vehicle_name"),
                    score=r.get("confidence", 0.5),
                    url=r.get("url"),
                )
                for r in results
            ]
        except Exception as exc:
            logger.warning("Google Lens search failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_and_rank(
        results: List[SearchResult], top_k: int
    ) -> List[SearchResult]:
        seen_contents: set[str] = set()
        unique: List[SearchResult] = []
        for r in results:
            key = r.content[:200].strip().lower()
            if key and key not in seen_contents:
                seen_contents.add(key)
                unique.append(r)

        unique.sort(key=lambda x: x.score, reverse=True)
        return unique[:top_k]
