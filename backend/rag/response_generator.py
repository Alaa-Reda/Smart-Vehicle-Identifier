"""
Response Generator
==================
Calls the Groq API with a fully-built prompt and parses the response.

Responsibilities:
- Execute Groq API requests.
- Parse confidence scores from responses.
- Detect language from responses.
- Detect uncertainty and conflict markers.
- Return structured GeneratedResponse objects.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from models.qwen.config import MODEL_NAME
from groq import AsyncGroq, APIStatusError

logger = logging.getLogger(__name__)

GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_TEXT_MODEL = MODEL_NAME

@dataclass
class GeneratedResponse:
    answer: str
    confidence: float
    language: str
    sources: List[str] = field(default_factory=list)
    structured_data: Dict[str, Any] = field(default_factory=dict)
    conflict_detected: bool = False
    needs_web_search: bool = False


class ResponseGenerator:
    """
    Groq API client for the RAG response generation stage.
    """

    def __init__(self) -> None:
        self._api_key = os.environ.get("GROQ_API_KEY", "")
        self._client = AsyncGroq(api_key=self._api_key)

    async def generate(
        self,
        prompt: str,
        language: str,
        system_override: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> GeneratedResponse:
        if not self._api_key:
            logger.error("GROQ_API_KEY not configured")
            return self._empty_response(language)

        system_prompt = system_override or self._default_system(language)

        try:
            response = await self._client.chat.completions.create(
                model=GROQ_TEXT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        # /no_think disables Qwen3 extended thinking mode
                        "content": prompt + "\n\n/no_think",
                    },
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                )

            content = response.choices[0].message.content or ""

            logger.info("Groq generated %d characters.", len(content))
            return self._parse_response(content, language)
        except APIStatusError as exc:
            logger.error(
                "Groq API HTTP error %s: %s",
                exc.status_code,
                exc,
            )
            return self._empty_response(language)
        except Exception as exc:
            logger.error("Groq API call failed: %s", exc)
            return self._empty_response(language)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _parse_response(self, content: str, fallback_language: str) -> GeneratedResponse:
        confidence = self._extract_confidence(content)
        conflict = self._detect_conflict(content)
        needs_web = self._detect_uncertainty(content)
        lang = self._detect_language(content, fallback_language)
        clean_answer = self._strip_markers(content)

        return GeneratedResponse(
            answer=clean_answer,
            confidence=confidence,
            language=lang,
            conflict_detected=conflict,
            needs_web_search=needs_web,
        )

    @staticmethod
    def _extract_confidence(content: str) -> float:
        match = re.search(r"\[CONFIDENCE:\s*([0-9.]+)\]", content, re.IGNORECASE)
        if match:
            try:
                return min(1.0, max(0.0, float(match.group(1))))
            except ValueError:
                pass
        return 0.65

    @staticmethod
    def _detect_conflict(content: str) -> bool:
        match = re.search(r"\[CONFLICT_DETECTED:\s*(YES|NO)\]", content, re.IGNORECASE)
        if match:
            return match.group(1).upper() == "YES"
        return False

    @staticmethod
    def _detect_uncertainty(content: str) -> bool:
        markers = [
            "[NEEDS_WEB_SEARCH]", "I'm not sure", "I cannot", "unclear",
            "uncertain", "لست متأكد", "لا أستطيع", "غير متأكد",
        ]
        lower = content.lower()
        return any(m.lower() in lower for m in markers)

    @staticmethod
    def _detect_language(content: str, fallback: str) -> str:
        arabic_chars = sum(1 for c in content if "\u0600" <= c <= "\u06ff")
        total_alpha = sum(1 for c in content if c.isalpha())
        if total_alpha > 0 and arabic_chars / total_alpha > 0.3:
            return "ar"
        return fallback if fallback and fallback != "auto" else "en"

    @staticmethod
    def _strip_markers(content: str) -> str:
        # Remove Qwen thinking block
        content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove confidence marker
        content = re.sub(
            r"\[CONFIDENCE:\s*[0-9.]+\]",
            "",
            content,
            flags=re.IGNORECASE,
        )

        # Remove conflict marker
        content = re.sub(
            r"\[CONFLICT_DETECTED:\s*(YES|NO)\]",
            "",
            content,
            flags=re.IGNORECASE,
        )

        # Remove web search marker
        content = re.sub(
            r"\[NEEDS_WEB_SEARCH\]",
            "",
            content,
            flags=re.IGNORECASE,
        )

        return content.strip()

    @staticmethod
    def _default_system(language: str) -> str:
        if language and language.startswith("ar"):
            lang_instr = "أجب باللغة العربية."
        elif language and language.startswith("en"):
            lang_instr = "Respond in English."
        else:
            lang_instr = "Detect the user's language and respond in the same language."

        return (
            f"You are an expert automotive AI assistant. {lang_instr} "
            "Be factual, structured, and concise. Never hallucinate. "
            "Do NOT use <think> tags or show any reasoning process. "
            "Go directly to the answer. "
            "Always include [CONFIDENCE: 0.XX] at the end of your response."
        )

    @staticmethod
    def _empty_response(language: str) -> GeneratedResponse:
        return GeneratedResponse(
            answer="",
            confidence=0.0,
            language=language,
            needs_web_search=True,
        )