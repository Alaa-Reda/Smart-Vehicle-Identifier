"""
Prompt Builder
==============
Centralized prompt engineering module.

Builds all prompts used in the system:
- RAG Prompt
- Enrichment Prompt
- Comparison Prompt
- Disagreement / Evidence Synthesis Prompt
- Web Verification Prompt
- Conversation Prompt (with memory)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class PromptBuilder:
    """
    All prompt templates in one place.
    No string concatenation scattered across services.
    """

    def build_rag_prompt(
        self,
        question: str,
        context: str,
        vehicle_name: Optional[str],
        conversation_history: Optional[List[Dict[str, str]]],
        language: str,
    ) -> str:
        lang_instruction = _lang_instruction(language)
        history_block = _format_history(conversation_history)
        vehicle_block = f"Vehicle in context: {vehicle_name}\n" if vehicle_name else ""

        return f"""You are an expert automotive AI assistant.

{lang_instruction}

{vehicle_block}

Conversation History:
{history_block or 'No previous conversation.'}

Retrieved Knowledge:
{context or 'No retrieved context available.'}

User Question:
{question}

Instructions:
- Answer only from the retrieved knowledge and conversation history above.
- If the retrieved knowledge does not contain the answer, say so clearly.
- Include a confidence score at the end: [CONFIDENCE: 0.XX]
- Never hallucinate vehicle specifications.
- Be factual, structured, and concise.
"""

    def build_enrichment_prompt(
        self,
        raw_answer: str,
        context: str,
        vehicle_name: str,
        language: str,
    ) -> str:
        lang_instruction = _lang_instruction(language)

        return f"""You are an expert automotive AI assistant enriching a generated answer with verified knowledge.

{lang_instruction}

Vehicle: {vehicle_name}

Initial Answer (from vision model):
{raw_answer}

Additional Verified Knowledge:
{context or 'No additional context available.'}

Instructions:
- Improve the initial answer using the additional knowledge.
- Correct any inaccuracies if the knowledge contradicts the initial answer.
- Keep the response factual and structured.
- Include a confidence score at the end: [CONFIDENCE: 0.XX]
"""

    def build_comparison_prompt(
        self,
        vehicles: List[str],
        attribute_table: Dict[str, Dict[str, Any]],
        aspect: Optional[str],
        language: str,
    ) -> str:
        lang_instruction = _lang_instruction(language)
        vehicles_str = " vs ".join(vehicles)
        aspect_str = f"Focus specifically on: {aspect}\n" if aspect else ""

        table_lines = []
        for attr, values in attribute_table.items():
            row = f"- {attr}: " + " | ".join(
                f"{v}: {val}" for v, val in values.items()
            )
            table_lines.append(row)
        table_str = "\n".join(table_lines)

        return f"""You are an expert automotive comparison analyst.

{lang_instruction}

Vehicles to compare: {vehicles_str}
{aspect_str}
Attribute Data:
{table_str}

Instructions:
- Write a structured, factual comparison.
- Highlight key differences and similarities.
- Provide a recommendation if the data supports it.
- Be concise and honest. Do not speculate beyond the data provided.
"""

    def build_evidence_synthesis_prompt(
        self,
        original_question: str,
        disputed_answer: str,
        user_claim: Optional[str],
        evidence: List[Dict[str, Any]],
        language: str,
    ) -> str:
        lang_instruction = _lang_instruction(language)
        evidence_block = "\n\n".join(
            f"[Source: {e.get('source', 'unknown')} | Confidence: {e.get('confidence', 0):.2f}]\n{e.get('answer', '')}"
            for e in evidence
        )
        user_claim_block = f"\nUser's claim: {user_claim}" if user_claim else ""

        return f"""You are an expert automotive AI analyst performing evidence-based re-evaluation.

{lang_instruction}

Original question: {original_question}
Disputed answer: {disputed_answer}{user_claim_block}

Available Evidence:
{evidence_block or 'No evidence available.'}

Instructions:
- Evaluate all evidence carefully.
- If evidence contradicts the disputed answer, correct it and explain why.
- If evidence supports the disputed answer, defend it with citations.
- If sources conflict, explain the conflict clearly and honestly.
- Never hallucinate. Never guess.
- Include [CONFLICT_DETECTED: YES/NO] at the end.
- Include [CONFIDENCE: 0.XX] at the end.
"""

    def build_web_verification_prompt(
        self,
        claim: str,
        web_results: List[str],
        language: str,
    ) -> str:
        lang_instruction = _lang_instruction(language)
        sources_block = "\n\n".join(
            f"[Source {i + 1}]: {r}" for i, r in enumerate(web_results)
        )

        return f"""You are an automotive fact-checker.

{lang_instruction}

Claim to verify: {claim}

Web sources:
{sources_block}

Instructions:
- Assess whether the claim is supported, contradicted, or unresolvable from these sources.
- Return verdict: SUPPORTED | CONTRADICTED | UNCERTAIN
- Provide a brief explanation.
"""


# ---------------------------------------------------------------------------
# Private Helpers
# ---------------------------------------------------------------------------

def _lang_instruction(language: str) -> str:
    if language and language.startswith("ar"):
        return "يجب أن تكون إجابتك باللغة العربية. يُقبل استخدام اللهجة المصرية."
    if language and language.startswith("en"):
        return "Respond in English."
    return (
        "Detect the user's language from the question and respond in the same language. "
        "If no question is present, respond in English."
    )


def _format_history(
    history: Optional[List[Dict[str, str]]]
) -> str:
    if not history:
        return ""
    lines = []
    for turn in history[-8:]:   # Last 8 turns max
        user_msg = turn.get("role_user", "")
        asst_msg = turn.get("role_assistant", "")
        if user_msg:
            lines.append(f"User: {user_msg}")
        if asst_msg:
            lines.append(f"Assistant: {asst_msg}")
    return "\n".join(lines)
