from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class SourceScore:
    source: str
    score: float
    reason: str


class RankingEngine:
    """Rank candidate sources before prompt construction."""

    _base_weights = {
        "rag": 0.9,
        "web_scraping": 0.6,
        "classification_model": 0.8,
        "qwen_vl": 0.85,
    }

    def rank(self, candidates: Iterable[str], intent: str) -> List[SourceScore]:
        scored: List[SourceScore] = []
        for source in candidates:
            base = self._base_weights.get(source, 0.5)
            intent_bonus = self._intent_bonus(source=source, intent=intent)
            total = min(1.0, base + intent_bonus)
            scored.append(SourceScore(source=source, score=total, reason=f"base={base}+bonus={intent_bonus}"))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored

    @staticmethod
    def _intent_bonus(source: str, intent: str) -> float:
        if intent in {"car_question", "comparison"} and source == "rag":
            return 0.1
        if intent == "comparison" and source == "classification_model":
            return 0.1
        if intent == "general_chat" and source == "qwen_vl":
            return 0.05
        return 0.0