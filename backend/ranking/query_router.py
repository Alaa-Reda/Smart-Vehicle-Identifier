from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    destination: str
    reason: str


class QueryRouter:
    """Route requests to the best backend path."""

    def route(self, intent: str, has_image: bool = False) -> RouteDecision:
        if intent == "off_topic":
            return RouteDecision(destination="guardrails", reason="off_topic_intent")

        if has_image:
            if intent == "comparison":
                return RouteDecision(destination="classification_model", reason="image_comparison")
            return RouteDecision(destination="qwen_vl", reason="image_understanding")

        if intent == "comparison":
            return RouteDecision(destination="rag", reason="comparison_with_knowledge")

        if intent == "car_question":
            return RouteDecision(destination="rag", reason="domain_question")

        return RouteDecision(destination="web_scraping", reason="fallback_retrieval")