"""
Intent Classifier
=================
Classifies user queries into structured intents.

Intents drive query routing decisions downstream.

Supported Intents:
- IDENTIFY_VEHICLE: User wants to know what the vehicle is.
- GET_SPECS: User wants technical specifications.
- GET_PRICE: User wants pricing information.
- COMPARE_VEHICLES: User wants to compare two or more vehicles.
- GET_SAFETY: User wants safety ratings or crash test results.
- GET_FEATURES: User wants feature lists (infotainment, ADAS, etc.).
- GENERAL_INFO: General open-ended vehicle question.
- OFF_TOPIC: Not related to vehicles.
- DISAGREEMENT: User disputes a previous answer.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional


class Intent(str, Enum):
    IDENTIFY_VEHICLE = "identify_vehicle"
    GET_SPECS = "get_specs"
    GET_PRICE = "get_price"
    COMPARE_VEHICLES = "compare_vehicles"
    GET_SAFETY = "get_safety"
    GET_FEATURES = "get_features"
    GENERAL_INFO = "general_info"
    OFF_TOPIC = "off_topic"
    DISAGREEMENT = "disagreement"


# Keyword patterns per intent (case-insensitive, ordered by priority)
_INTENT_PATTERNS: list[tuple[Intent, list[str]]] = [
    (Intent.DISAGREEMENT, [
        r"\bwrong\b", r"\bincorrect\b", r"\bmistake\b", r"\bغلط\b",
        r"\bخطأ\b", r"\bأنت غلطان\b", r"\bthat's not right\b",
    ]),
    (Intent.COMPARE_VEHICLES, [
        r"\bcompare\b", r"\bvs\b", r"\bversus\b", r"\bمقارنة\b",
        r"\bqarren\b", r"\bأيهما أفضل\b", r"\bbetter than\b",
        r"\bdifference between\b",
    ]),
    (Intent.IDENTIFY_VEHICLE, [
        r"\bwhat car\b", r"\bwhat vehicle\b", r"\bidentify\b",
        r"\bما هذه السيارة\b", r"\bما اسم\b", r"\bما موديل\b",
        r"\bwhich model\b", r"\bwhich car\b",
    ]),
    (Intent.GET_PRICE, [
        r"\bprice\b", r"\bcost\b", r"\bهow much\b", r"\bسعر\b",
        r"\bثمن\b", r"\bكم تكلف\b", r"\bافضل سعر\b",
    ]),
    (Intent.GET_SAFETY, [
        r"\bsafety\b", r"\bcrash\b", r"\bncap\b", r"\bnhtsa\b",
        r"\brating\b", r"\bأمان\b", r"\bتقييم السلامة\b",
    ]),
    (Intent.GET_SPECS, [
        r"\bengine\b", r"\bhorsepower\b", r"\btorque\b", r"\bspecs\b",
        r"\bspecifications\b", r"\bمواصفات\b", r"\bالمحرك\b",
        r"\bالعزم\b", r"\bالقوة\b", r"\btransmission\b",
        r"\bfuel\b", r"\bconsumption\b", r"\bسرعة\b",
    ]),
    (Intent.GET_FEATURES, [
        r"\bfeatures\b", r"\binfotainment\b", r"\badas\b",
        r"\bassist\b", r"\bتقنيات\b", r"\bمميزات\b",
        r"\bشاشة\b", r"\bنظام\b",
    ]),
]

_OFF_TOPIC_PATTERNS = [
    r"\bweather\b", r"\bcooking\b", r"\brecipe\b", r"\bpolitics\b",
    r"\bطبخ\b", r"\bسياسة\b", r"\bأخبار\b(?!.*سيار)",
]


class IntentClassifier:
    """
    Rule-based intent classifier with priority ordering.

    A lightweight and deterministic alternative to an LLM classifier.
    Fast, no external API calls, zero cost.
    """

    async def classify(self, text: str) -> Intent:
        if not text or not text.strip():
            return Intent.OFF_TOPIC

        text_lower = text.lower()

        # Check off-topic first
        for pattern in _OFF_TOPIC_PATTERNS:
            if re.search(pattern, text_lower):
                return Intent.OFF_TOPIC

        # Check intents in priority order
        for intent, patterns in _INTENT_PATTERNS:
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return intent

        return Intent.GENERAL_INFO

    def is_vehicle_related(self, intent: Intent) -> bool:
        return intent not in {Intent.OFF_TOPIC}

    def requires_comparison(self, intent: Intent) -> bool:
        return intent == Intent.COMPARE_VEHICLES

    def requires_fresh_data(self, intent: Intent) -> bool:
        return intent in {Intent.GET_PRICE, Intent.GET_SPECS, Intent.GET_FEATURES}
