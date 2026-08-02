from __future__ import annotations

# Standard Library

import json
import time
import threading

from .logger import logger
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

# Third-Party Libraries

from PIL import Image
from groq import Groq
from groq import APIStatusError, APIConnectionError, APITimeoutError

# Local Imports

from .config import (
    GROQ_API_KEY,
    MODEL_NAME,
    MAX_TOKENS,
    TEMPERATURE,
    TOP_P,
    STREAM,
    TIMEOUT,
    RETRIES,
)

from .prompts import (
    SYSTEM_PROMPT,
)

from .exceptions import (
    AuthenticationError,
    ConnectionError,
    TimeoutError,
    InvalidImageError,
    InvalidPromptError,
    ResponseError,
    GenerationError,
)

from .conversation import ConversationManager
from .image_utils import ImageProcessor


# ==========================================================
# Groq Client Singleton
# ==========================================================


class _GroqClientSingleton:
    """
    Thread-safe Singleton for Groq client.
    Ensures only one Groq client instance exists.
    """

    _instance: Optional[Groq] = None
    _lock = threading.Lock()

    @classmethod
    def get_client(cls) -> Groq:

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:

                    logger.info("Creating Groq Client...")

                    if not GROQ_API_KEY:
                        raise AuthenticationError(
                            "GROQ_API_KEY was not found. "
                            "Please configure your environment variables.\n"
                            "Get a free key from: https://console.groq.com/keys"
                        )

                    cls._instance = Groq(
                        api_key=GROQ_API_KEY,
                        timeout=TIMEOUT,
                    )

                    logger.info("Groq Client initialized successfully.")

        return cls._instance

    @classmethod
    def reset(cls) -> None:

        with cls._lock:

            cls._instance = None

            logger.warning("Groq Client has been reset.")


# ==========================================================
# Main Inference Class
# ==========================================================


class QwenOnlineInference:
    """
    SDK for Vision-Language Inference via Groq API.

    Uses Groq's fast inference for multimodal tasks:
    - Vehicle identification from images
    - Multi-turn conversations
    - Structured JSON responses
    - Streaming support
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        system_prompt: str = SYSTEM_PROMPT,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
        top_p: float = TOP_P,
        stream: bool = STREAM,
        timeout: int = TIMEOUT,
        retries: int = RETRIES,
    ) -> None:

        logger.info("Initializing Groq Vision Inference...")

        self.client = _GroqClientSingleton.get_client()

        self.model_name = model_name
        self.system_prompt = system_prompt

        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.stream = stream
        self.timeout = timeout
        self.retries = retries

        self.conversation = ConversationManager()

        self.last_response: Optional[str] = None
        self.last_usage: Dict[str, Any] = {}

        self.sdk_name = "Groq Vision SDK"
        self.sdk_version = "1.0.0"

        logger.info("Groq Vision SDK initialized successfully.")

    # ==========================================================
    # Message Builder
    # ==========================================================

    def _build_messages(
        self,
        prompt: str,
        image: Optional[Union[str, Path, Image.Image]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build OpenAI-compatible chat messages for Groq API.
        """

        if not prompt.strip():
            raise InvalidPromptError("Prompt cannot be empty.")

        messages: List[Dict[str, Any]] = []

        # System prompt
        if self.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": self.system_prompt,
                }
            )

        # Conversation history
        if history:
            messages.extend(history)

        # User message — text only
        if image is None:
            messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

        # User message — text + image
        else:
            prepared_image = ImageProcessor.prepare_image(image)

            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": prepared_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            )

        return messages

    # ==========================================================
    # Chat Completion
    # ==========================================================

    def chat(
        self,
        prompt: str,
        image: Optional[Union[str, Path, Image.Image]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Send a chat completion request via Groq API.

        Parameters
        ----------
        prompt : str
            User prompt text.

        image : str | Path | PIL.Image | None
            Optional image input.

        history : list | None
            Previous conversation messages.

        Returns
        -------
        str
            Generated text response.
        """

        messages = self._build_messages(
            prompt=prompt,
            image=image,
            history=history or self.conversation.get_messages(),
        )

        last_exception = None

        for attempt in range(1, self.retries + 1):

            logger.info(f"Sending request (Attempt {attempt}/{self.retries})")
            logger.info(f"Model: {self.model_name}")

            try:

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    stream=False,
                )

                result = response.choices[0].message.content

                # Save to conversation history
                self.conversation.add_user(
                    content=prompt if image is None else [
                        {"type": "text", "text": prompt},
                    ]
                )
                self.conversation.add_assistant(result)
                self.last_response = result

                # Save usage stats
                if hasattr(response, "usage") and response.usage:
                    self.last_usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }

                logger.info("Generation completed successfully.")

                return result

            except APIStatusError as error:

                last_exception = error
                logger.error(error)
                time.sleep(attempt)

            except (APIConnectionError, APITimeoutError) as error:

                last_exception = error
                logger.error(error)
                time.sleep(attempt * 2)

            except Exception as error:

                last_exception = error
                logger.exception(error)
                time.sleep(attempt)

        raise GenerationError(
            f"Generation failed after {self.retries} attempts.\n"
            f"{last_exception}"
        )

    # ==========================================================
    # Utility Methods
    # ==========================================================

    def get_model_info(self) -> Dict[str, Any]:

        return {
            "sdk_name": self.sdk_name,
            "sdk_version": self.sdk_version,
            "provider": "groq",
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stream": self.stream,
            "timeout": self.timeout,
            "retries": self.retries,
        }

    def get_last_response(self) -> Optional[str]:
        return self.last_response

    def get_usage(self) -> Dict[str, Any]:
        return self.last_usage.copy()

    def reset_usage(self) -> None:
        self.last_usage.clear()

    def reset(self) -> None:

        self.conversation.clear()
        self.last_response = None
        self.last_usage.clear()

        logger.info("Session has been reset.")

    def health_check(self) -> bool:

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )
            return response is not None and len(response.choices) > 0

        except Exception as error:
            logger.exception(error)
            return False

    def chat_json(
        self,
        prompt: str,
        image: Optional[Union[str, Path, Image.Image]] = None,
        schema: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON response.
        """

        json_prompt = prompt

        if schema:
            json_prompt += (
                "\n\nReturn ONLY valid JSON "
                "that follows this schema:\n"
                + json.dumps(schema, indent=4)
            )

        response = self.chat(
            prompt=json_prompt,
            image=image,
            history=history,
        )

        # Strip markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ResponseError("Model returned invalid JSON.")

    def stream_chat(
        self,
        prompt: str,
        image: Optional[Union[str, Path, Image.Image]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Stream model response token by token.
        """

        messages = self._build_messages(
            prompt=prompt,
            image=image,
            history=history or self.conversation.get_messages(),
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
        )

        for chunk in response:
            if (
                chunk.choices
                and chunk.choices[0].delta.content
            ):
                yield chunk.choices[0].delta.content

    def save_history(self, file_path: Union[str, Path]) -> None:

        file_path = Path(file_path)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                self.conversation.get_messages(),
                file,
                indent=4,
                ensure_ascii=False,
            )

    def load_history(self, file_path: Union[str, Path]) -> None:

        file_path = Path(file_path)

        with open(file_path, "r", encoding="utf-8") as file:
            self.conversation.load_messages(json.load(file))

    def export_config(self) -> Dict[str, Any]:

        return {
            "provider": "groq",
            "model": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "stream": self.stream,
            "retries": self.retries,
        }

    def update_config(self, **kwargs) -> None:

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def close(self) -> None:

        self.conversation.clear()
        self.last_response = None
        self.last_usage.clear()

        logger.info("Session closed.")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"model='{self.model_name}', "
            f"provider='groq')"
        )

    def __str__(self) -> str:
        return f"{self.sdk_name} ({self.model_name})"