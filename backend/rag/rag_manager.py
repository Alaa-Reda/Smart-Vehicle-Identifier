"""
RAG Manager
===========
Top-level orchestrator for the Retrieval-Augmented Generation system.

Responsibilities:
- Coordinate between Retriever, ContextBuilder, PromptBuilder, and ResponseGenerator.
- Manage the vector knowledge base lifecycle.
- Ingest scraped web documents into the vector store and MongoDB.
- Enrich Groq responses with RAG context.
- Provide a clean API to the rest of the backend.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from rag.retriever import Retriever, RetrievedDocument
from rag.context_builder import ContextBuilder
from rag.prompt_builder import PromptBuilder
from rag.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)


class RAGContext:
    """
    Lightweight result object passed between RAG components and the ranking engine.
    """

    def __init__(
        self,
        answer: str,
        confidence: float,
        language: str,
        sources: List[str],
        structured_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.answer = answer
        self.confidence = confidence
        self.language = language
        self.sources = sources
        self.structured_data = structured_data or {}


class RAGManager:
    """
    Facade over the entire RAG subsystem.
    Used by VehicleService, CompareService, and the SearchService.
    """

    def __init__(self) -> None:
        self._retriever = Retriever()
        self._context_builder = ContextBuilder()
        self._prompt_builder = PromptBuilder()
        self._response_generator = ResponseGenerator()

    async def enrich_with_context(
        self,
        vehicle_name: str,
        raw_answer: str,
        language: str,
    ) -> RAGContext:
        """
        Enrich a Groq-generated raw answer with RAG-retrieved context.
        Used when the classification model identified the vehicle and Groq
        already produced an answer, but we want to ground it with stored knowledge.
        """
        docs = await self._retriever.retrieve(
            query=f"vehicle information {vehicle_name}",
            top_k=5,
        )
        context = self._context_builder.build(
            documents=docs,
            vehicle_name=vehicle_name,
        )
        prompt = self._prompt_builder.build_enrichment_prompt(
            raw_answer=raw_answer,
            context=context,
            vehicle_name=vehicle_name,
            language=language,
        )
        result = await self._response_generator.generate(
            prompt=prompt,
            language=language,
        )
        return RAGContext(
            answer=result.answer,
            confidence=result.confidence,
            language=result.language,
            sources=result.sources,
            structured_data=result.structured_data,
        )

    async def ingest_scraped_data(
        self,
        vehicle_name: str,
        documents: List[Dict[str, Any]],
    ) -> int:
        """
        Ingest newly scraped web documents into the vector store and MongoDB.
        Returns the number of documents successfully indexed.
        """
        if not documents:
            return 0

        ingested = 0
        for doc in documents:
            try:
                text = doc.get("content", "") or doc.get("text", "")
                if not text.strip():
                    continue

                metadata = {
                    "vehicle_name": vehicle_name,
                    "source_url": doc.get("url", ""),
                    "source_type": doc.get("source_type", "web"),
                    "title": doc.get("title", ""),
                }

                await self._retriever.add_document(
                    text=text,
                    metadata=metadata,
                )
                ingested += 1
            except Exception as exc:
                logger.warning(
                    "Failed to ingest document for '%s': %s", vehicle_name, exc
                )

        logger.info("Ingested %d/%d documents for '%s'", ingested, len(documents), vehicle_name)
        return ingested

    async def retrieve_relevant_documents(
        self,
        query: str,
        vehicle_context: Optional[str] = None,
        top_k: int = 10,
    ) -> List[RetrievedDocument]:
        """
        Retrieve the most semantically relevant documents for a query.
        Used directly by the pipeline for fine-grained control.
        """
        search_query = (
            f"{vehicle_context} {query}" if vehicle_context else query
        )
        return await self._retriever.retrieve(query=search_query, top_k=top_k)

    async def rebuild_index(self) -> None:
        """
        Rebuild the FAISS index from scratch using all MongoDB vehicle documents.
        Used for maintenance and reindexing after large ingestion batches.
        """
        logger.info("Rebuilding FAISS index from MongoDB...")
        await self._retriever.rebuild_index()
        logger.info("FAISS index rebuild complete.")
