from dataclasses import dataclass


@dataclass(frozen=True)
class ModerationResult:
    allowed: bool
    reason: str


class Moderation:
    """Basic moderation layer for abusive or restricted content."""

    _blocked_terms = {
        "idiot",
        "stupid",
        "hate",
        "kill",
        "racist",
    }

    def check(self, text: str) -> ModerationResult:
        normalized = (text or "").strip().lower()
        if not normalized:
            return ModerationResult(allowed=True, reason="empty_input")

        for term in self._blocked_terms:
            if term in normalized:
                return ModerationResult(allowed=False, reason=f"blocked_term:{term}")

        return ModerationResult(allowed=True, reason="clean")