from dataclasses import dataclass


@dataclass(frozen=True)
class IntentResult:
    label: str
    confidence: float


class IntentClassifier:
    """Rule-based intent classifier used before routing."""

    _comparison_keywords = {
        "compare",
        "comparison",
        "vs",
        "versus",
        "better",
        "difference",
    }
    _car_keywords = {
        "car",
        "vehicle",
        "model",
        "engine",
        "horsepower",
        "sedan",
        "suv",
        "truck",
    }
    _off_topic_keywords = {
        "politics",
        "religion",
        "hack",
        "explosive",
    }

    def classify(self, text: str) -> IntentResult:
        normalized = (text or "").strip().lower()
        if not normalized:
            return IntentResult(label="general_chat", confidence=0.5)

        if any(token in normalized for token in self._off_topic_keywords):
            return IntentResult(label="off_topic", confidence=0.9)

        if any(token in normalized for token in self._comparison_keywords):
            return IntentResult(label="comparison", confidence=0.9)

        if any(token in normalized for token in self._car_keywords):
            return IntentResult(label="car_question", confidence=0.85)

        return IntentResult(label="general_chat", confidence=0.7)