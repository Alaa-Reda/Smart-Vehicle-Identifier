# Ranking Module

The ranking module is a pre-processing layer that decides how a request should be handled.

## Files

- `intent_classifier.py`: classify user intent into `car_question`, `comparison`, `general_chat`, or `off_topic`.
- `moderation.py`: detect offensive or restricted language.
- `query_router.py`: select the best processing path based on intent and request signals.
- `guardrails.py`: enforce response policy checks before sending output.
- `ranking_engine.py`: rank available sources by score and priority.

## Goal

Improve relevance and safety by selecting the right source before prompt building and generation.
