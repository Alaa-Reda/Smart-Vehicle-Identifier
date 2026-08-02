
# ==========================================================
# Custom Exceptions
# ==========================================================


class QwenError(Exception):
    """
    Base exception for all Qwen Online Inference errors.
    """

    pass


class AuthenticationError(QwenError):
    """
    Raised when the Hugging Face token is invalid
    or authentication fails.
    """

    pass


class ConnectionError(QwenError):
    """
    Raised when the inference provider
    cannot be reached.
    """

    pass


class TimeoutError(QwenError):
    """
    Raised when a request exceeds
    the configured timeout.
    """

    pass


class InvalidImageError(QwenError):
    """
    Raised when an image is invalid,
    corrupted, or unsupported.
    """

    pass


class InvalidPromptError(QwenError):
    """
    Raised when the prompt is empty
    or incorrectly formatted.
    """

    pass


class ResponseError(QwenError):
    """
    Raised when the model returns
    an unexpected response.
    """

    pass


class GenerationError(QwenError):
    """
    Raised when text generation fails.
    """

    pass