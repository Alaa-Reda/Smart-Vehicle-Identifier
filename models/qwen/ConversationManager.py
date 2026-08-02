from __future__ import annotations

from typing import Any, Dict, List, Optional

from .logger import logger
from .schemas import ChatMessage
from .exceptions import InvalidPromptError
from .prompts import SYSTEM_PROMPT


class ConversationManager:
    # ==========================================================
    # Conversation Management
    # ==========================================================

    def set_system_prompt(self, prompt: str) -> None:
        """
        Update the system prompt.
        """

        if not prompt.strip():
            raise InvalidPromptError(
                "System prompt cannot be empty."
            )

        self.system_prompt = prompt

        logger.info("System prompt updated.")

    def get_system_prompt(self) -> str:
        """
        Return the current system prompt.
        """

        return self.system_prompt

    def reset_system_prompt(self) -> None:
        """
        Reset the system prompt to the default prompt.
        """

        self.system_prompt = SYSTEM_PROMPT

        logger.info("System prompt reset to default.")

    def clear_history(self) -> None:
        """
        Remove all conversation history.
        """

        self.history.clear()

        logger.info("Conversation history cleared.")

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Return conversation history.
        """

        return self.history.copy()

    def add_message(
        self,
        role: str,
        content: Any,
    ) -> None:
        """
        Add a message to the conversation history.

        Parameters
        ----------
        role : str
            system | user | assistant

        content : Any
            Message content.
        """

        self.messages.append(
            ChatMessage(
                role=role,
                content=content,
            )
        )

    def remove_last_message(self) -> None:
        """
        Remove the last message from history.
        """

        if self.history:

            self.history.pop()

    def save_last_response(
        self,
        response: str,
    ) -> None:
        """
        Save the latest model response.
        """

        self.last_response = response

        self.add_message(
            role="assistant",
            content=response,
        )

    def set_generation_config(
        self,
        *,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stream: Optional[bool] = None,
    ) -> None:
        """
        Update generation parameters.
        """

        if max_tokens is not None:
            self.max_tokens = max_tokens

        if temperature is not None:
            self.temperature = temperature

        if top_p is not None:
            self.top_p = top_p

        if stream is not None:
            self.stream = stream

        logger.info("Generation configuration updated.")

    def load_messages(self, messages: list[dict]) -> None:
        """
        Load conversation history.
        """

        self.messages = [
            ChatMessage(**message)
            for message in messages
        ]

        logger.info("Conversation history loaded.")
