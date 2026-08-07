"""
RAG Pipeline
============
End-to-end pipeline: retrieve → build context → build prompt → generate response.

Responsibilities:
- Coordinate all RAG components in sequence.
- Apply conversation memory to prompts.
- Return confidence-scored RAGContext objects.
- Provide a single entry point for all Q&A flows.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from rag.retriever import Retriever
from rag.context_builder import ContextBuilder
from rag.prompt_builder import PromptBuilder
from rag.response_generator import ResponseGenerator, GeneratedResponse
from rag.rag_manager import RAGContext

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    The main pipeline used by VehicleService and CompareService.
    """

    def __init__(self) -> None:
        self._retriever = Retriever()
        self._context_builder = ContextBuilder()
        self._prompt_builder = PromptBuilder()
        self._response_generator = ResponseGenerator()

    async def retrieve_and_generate(
        self,
        question: str,
        vehicle_context: Optional[str],
        session_context: Dict[str, Any],
        language: str,
        top_k: int = 10,
    ) -> RAGContext:
        """
        Full RAG pipeline:
        1. Retrieve relevant documents from FAISS.
        2. Build context string.
        3. Build prompt with memory.
        4. Generate response via Groq.
        5. Return RAGContext with confidence score.
        """
        search_query = (
            f"{vehicle_context} {question}" if vehicle_context else question
        )

        # Step 1: Retrieve
        documents = await self._retriever.retrieve(
            query=search_query, top_k=top_k
        )

        # Step 2: Build context
        context_str = self._context_builder.build(
            documents=documents,
            vehicle_name=vehicle_context,
        )

        # Step 3: Build prompt
        conversation_history = session_context.get("recent_turns", [])
        prompt = self._prompt_builder.build_rag_prompt(
            question=question,
            context=context_str,
            vehicle_name=vehicle_context,
            conversation_history=conversation_history,
            language=language,
        )

        # Step 4: Generate
        generated: GeneratedResponse = await self._response_generator.generate(
            prompt=prompt,
            language=language,
        )

        sources = [
            doc.metadata.get("source_url", "knowledge base")
            for doc in documents[:5]
            if doc.metadata.get("source_url")
        ]

        return RAGContext(
            answer=generated.answer,
            confidence=generated.confidence,
            language=generated.language,
            sources=sources,
            structured_data=generated.structured_data,
        )
