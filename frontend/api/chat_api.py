r"""
===========================================================
Smart Vehicle Identifier
Chat API
===========================================================

High-level API wrapper for the Vision-Language assistant.

Responsibilities
----------------
- Ask questions about uploaded vehicles
- Multi-turn conversations
- Conversation reset
- Optional streaming support

Contains no UI logic.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image

from api.client import client


class ChatAPI:
    """Wrapper around the AI Assistant endpoints."""

    # ======================================================
    # Chat
    # ======================================================

    def ask(
        self,
        question: str,
        image: Image.Image | None = None,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Ask the AI assistant a question.

        Parameters
        ----------
        question:
            User question.

        image:
            Optional uploaded image.

        conversation_id:
            Existing conversation id.
        """

        data = {
            "question": question,
        }

        if conversation_id:
            data["conversation_id"] = conversation_id

        files = None

        if image is not None:
            with BytesIO() as buffer:
                image.save(
                    buffer,
                    format="JPEG",
                    quality=95,
                )

                buffer.seek(0)

                files = {
                    "image": (
                        "vehicle.jpg",
                        buffer.getvalue(),
                        "image/jpeg",
                    )
                }

                return client.post(
                    "/chat",
                    data=data,
                    files=files,
                )

        return client.post(
            "/chat",
            data=data,
            files=None,
        )

    # ======================================================
    # Reset Conversation
    # ======================================================

    def reset(
        self,
        conversation_id: str,
    ) -> dict[str, Any]:

        return client.post(
            "/chat/reset",
            json={
                "conversation_id": conversation_id
            },
        )

    # ======================================================
    # Conversation History
    # ======================================================

    def history(
        self,
        conversation_id: str,
    ) -> dict[str, Any]:

        return client.get(
            f"/chat/{conversation_id}"
        )

    # ======================================================
    # Streaming (Future)
    # ======================================================

    def stream(
        self,
        question: str,
        conversation_id: str | None = None,
    ) -> Any:
        """
        Placeholder for future streaming support.

        Can later be upgraded to:
            - SSE
            - WebSocket
            - Chunked responses
        """

        raise NotImplementedError(
            "Streaming is not implemented yet."
        )


# ==========================================================
# Singleton
# ==========================================================

chat_api = ChatAPI()