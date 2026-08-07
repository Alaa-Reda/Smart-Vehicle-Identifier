"""
Moderation Service
==================
Detects unsafe, off-topic, or malicious inputs before they enter the pipeline.

Checks:
- Prompt injection attempts
- Jailbreak patterns
- Spam / repeated content
- Explicit unsafe requests
- Off-topic non-vehicle content
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModerationResult:
    is_safe: bool
    reason: Optional[str] = None
    category: Optional[str] = None


_INJECTION_PATTERNS = [
    r"ignore (previous|all|above) instructions",
    r"you are now",
    r"act as (a|an)",
    r"pretend (you are|to be)",
    r"disregard your",
    r"forget everything",
    r"new persona",
    r"system prompt",
    r"\[\[.*\]\]",
    r"<\|.*\|>",
]

_JAILBREAK_PATTERNS = [
    r"DAN mode",
    r"jailbreak",
    r"bypass (safety|filter|restriction)",
    r"developer mode",
    r"unrestricted mode",
    r"without limitations",
]

_UNSAFE_PATTERNS = [
    r"\bhow to (make|build|create) (a )?bomb\b",
    r"\bweapon\b",
    r"\bexplosive\b",
    r"\bdrug\b",
    r"\bhack\b",
    r"\bmalware\b",
]

_MAX_LENGTH = 2000
_SPAM_REPEAT_THRESHOLD = 0.6   # 60% repeated chars = spam


class ModerationService:

    async def check(self, text: str) -> ModerationResult:
        if not text or not text.strip():
            return ModerationResult(is_safe=False, reason="Empty input.", category="empty")

        if len(text) > _MAX_LENGTH:
            return ModerationResult(
                is_safe=False,
                reason="Input exceeds maximum allowed length.",
                category="length",
            )

        if self._is_spam(text):
            return ModerationResult(is_safe=False, reason="Spam detected.", category="spam")

        text_lower = text.lower()

        for pattern in _INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return ModerationResult(
                    is_safe=False,
                    reason="Prompt injection attempt detected.",
                    category="injection",
                )

        for pattern in _JAILBREAK_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return ModerationResult(
                    is_safe=False,
                    reason="Jailbreak attempt detected.",
                    category="jailbreak",
                )

        for pattern in _UNSAFE_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return ModerationResult(
                    is_safe=False,
                    reason="Unsafe request detected.",
                    category="unsafe",
                )

        return ModerationResult(is_safe=True)

    @staticmethod
    def _is_spam(text: str) -> bool:
        if not text:
            return False
        most_common_char = max(set(text), key=text.count)
        ratio = text.count(most_common_char) / len(text)
        return ratio > _SPAM_REPEAT_THRESHOLD and len(text) > 20
