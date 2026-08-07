"""
Context Builder
===============
Assembles a structured context string from retrieved documents.

Responsibilities:
- Filter irrelevant documents by score threshold.
- Deduplicate overlapping content.
- Prioritize high-confidence, recent, trusted sources.
- Format context for injection into Groq prompts.
- Respect token budget limits.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from rag.retriever import RetrievedDocument

logger = logging.getLogger(__name__)

MIN_SCORE_THRESHOLD = 0.30
MAX_CONTEXT_CHARS = 8000        # ~2000 tokens


class ContextBuilder:
    """
    Builds a clean, deduplicated context string from retrieved documents.
    """

    def build(
        self,
        documents: List[RetrievedDocument],
        vehicle_name: Optional[str] = None,
    ) -> str:
        if not documents:
            return ""

        filtered = [d for d in documents if d.score >= MIN_SCORE_THRESHOLD]
        filtered.sort(key=lambda d: d.score, reverse=True)
        deduplicated = self._deduplicate(filtered)

        parts: List[str] = []
        total_chars = 0

        if vehicle_name:
            parts.append(f"Vehicle: {vehicle_name}\n")
            total_chars += len(parts[-1])

        for doc in deduplicated:
            source = doc.metadata.get("source_url", "knowledge base")
            entry = f"[Source: {source}]\n{doc.content.strip()}\n"
            if total_chars + len(entry) > MAX_CONTEXT_CHARS:
                break
            parts.append(entry)
            total_chars += len(entry)

        return "\n".join(parts).strip()

    @staticmethod
    def _deduplicate(
        documents: List[RetrievedDocument],
    ) -> List[RetrievedDocument]:
        seen: set[str] = set()
        result: List[RetrievedDocument] = []
        for doc in documents:
            key = doc.content[:150].strip().lower()
            if key not in seen:
                seen.add(key)
                result.append(doc)
        return result
