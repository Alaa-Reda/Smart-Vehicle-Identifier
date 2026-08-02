from typing import Any

from .schemas import ChatMessage


class ConversationManager:

    def __init__(self):

        self.messages: list[ChatMessage] = []

    def clear(self):

        self.messages.clear()

    def add_system(self, text: str):

        self.messages.append(

            ChatMessage(
                role="system",
                content=text,
            )
        )

    def add_user(self, content: Any):
        """Add a user message."""
        self.messages.append(

            ChatMessage(
                role="user",
                content=content,
            )
        )

    def add_assistant(self, text: str):

        self.messages.append(

            ChatMessage(
                role="assistant",
                content=text,
            )
        )

    def get_messages(self) -> list[dict]:

        return [

            message.model_dump()

            for message in self.messages

        ]

    def load_messages(self, messages):

        self.messages = [

            ChatMessage(**message)

            for message in messages

        ]  # Fixed: closing bracket was misaligned
