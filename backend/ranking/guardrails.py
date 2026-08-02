from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailsResult:
    allowed: bool
    message: str


class Guardrails:
    """Simple response guardrails used before returning output."""

    _blocked_phrases = {
        "i can hack",
        "build a weapon",
        "illegal instructions",
    }

    def validate_query_scope(self, text: str) -> GuardrailsResult:
        normalized = (text or "").strip().lower()
        if not normalized:
            return GuardrailsResult(allowed=False, message="Please provide a question.")

        if any(phrase in normalized for phrase in self._blocked_phrases):
            return GuardrailsResult(allowed=False, message="Request rejected by policy.")

        return GuardrailsResult(allowed=True, message="ok")

    def enforce_answer_style(self, answer: str) -> str:
        if not answer:
            return "I could not produce a reliable answer for this request."
        return answer.strip()