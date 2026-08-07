"""
Ranking Engine
==============
Post-generation ranking, validation, and evidence synthesis.

Responsibilities:
- Re-rank RAG answers by source quality and confidence.
- Validate answers through Guardrails.
- Synthesize multi-source evidence for disagreement flows.
- Detect and explain source conflicts.
- Return final RankedAnswer objects.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ranking.guardrails import GuardrailsService
from rag.rag_manager import RAGContext
from rag.prompt_builder import PromptBuilder
from rag.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)


@dataclass
class RankedAnswer:
    answer: str
    confidence: float
    language: str
    sources: List[str] = field(default_factory=list)
    conflict_detected: bool = False
    conflict_explanation: Optional[str] = None


class RankingEngine:

    def __init__(self) -> None:
        self._guardrails = GuardrailsService()
        self._prompt_builder = PromptBuilder()
        self._response_generator = ResponseGenerator()

    async def rank_answer(self, rag_context: RAGContext) -> RankedAnswer:
        guard = await self._guardrails.validate(
            answer=rag_context.answer,
            confidence=rag_context.confidence,
        )

        if not guard.passed:
            logger.warning("Guardrail failed: %s", guard.issue)
            return RankedAnswer(
                answer=rag_context.answer,
                confidence=max(0.0, rag_context.confidence - 0.20),
                language=rag_context.language,
                sources=rag_context.sources,
            )

        boosted_confidence = min(1.0, rag_context.confidence * 1.05)

        return RankedAnswer(
            answer=rag_context.answer,
            confidence=boosted_confidence,
            language=rag_context.language,
            sources=rag_context.sources,
        )

    async def synthesize_evidence(
        self,
        original_question: str,
        disputed_answer: str,
        user_claim: Optional[str],
        evidence: List[Dict[str, Any]],
        language: str,
    ) -> RankedAnswer:
        prompt = self._prompt_builder.build_evidence_synthesis_prompt(
            original_question=original_question,
            disputed_answer=disputed_answer,
            user_claim=user_claim,
            evidence=evidence,
            language=language,
        )

        generated = await self._response_generator.generate(
            prompt=prompt, language=language
        )

        sources = list({e.get("source", "unknown") for e in evidence})
        conflict = generated.conflict_detected
        conflict_explanation: Optional[str] = None

        if conflict:
            conflict_explanation = self._extract_conflict_explanation(generated.answer)

        return RankedAnswer(
            answer=generated.answer,
            confidence=generated.confidence,
            language=generated.language,
            sources=sources,
            conflict_detected=conflict,
            conflict_explanation=conflict_explanation,
        )

    @staticmethod
    def _extract_conflict_explanation(answer: str) -> Optional[str]:
        lines = answer.split("\n")
        for line in lines:
            if "conflict" in line.lower() or "disagree" in line.lower() or "تعارض" in line:
                return line.strip()
        return None
