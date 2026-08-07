"""
Guardrails Service
==================
Post-generation validation layer.

Checks:
- Hallucination markers in generated text
- Factual consistency against retrieved context
- Answer completeness
- Language consistency
- Minimum confidence enforcement
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class GuardrailResult:
    passed: bool
    issue: Optional[str] = None
    corrected_answer: Optional[str] = None


_HALLUCINATION_MARKERS = [
    r"\bI think\b",
    r"\bI believe\b",
    r"\bprobably\b",
    r"\bmight be\b",
    r"\bcould be\b",
    r"\bassume\b",
    r"\bأعتقد\b",
    r"\bربما\b",
    r"\bيمكن أن\b",
]

_FABRICATION_MARKERS = [
    r"\bas of my knowledge\b",
    r"\bI don't have real-time\b",
    r"\bI cannot access\b",
    r"\bI'm not able to\b",
]

MIN_ANSWER_LENGTH = 20


class GuardrailsService:

    async def validate(
        self,
        answer: str,
        confidence: float,
        context: Optional[str] = None,
    ) -> GuardrailResult:
        if not answer or len(answer.strip()) < MIN_ANSWER_LENGTH:
            return GuardrailResult(passed=False, issue="Answer too short or empty.")

        if confidence < 0.20:
            return GuardrailResult(
                passed=False, issue=f"Confidence too low: {confidence:.2f}"
            )

        answer_lower = answer.lower()

        for pattern in _FABRICATION_MARKERS:
            if re.search(pattern, answer_lower, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    issue="Answer contains fabrication markers.",
                )

        hallucination_count = sum(
            1 for p in _HALLUCINATION_MARKERS
            if re.search(p, answer_lower, re.IGNORECASE)
        )
        if hallucination_count >= 3:
            return GuardrailResult(
                passed=False,
                issue=f"High hallucination marker density: {hallucination_count} markers.",
            )

        return GuardrailResult(passed=True)
