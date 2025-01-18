from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class ModelResponse:
    """Standardized response format for all AI models"""

    text: str
    raw_response: Any  # Original provider response
    metadata: dict[str, Any]


@runtime_checkable
class GenerationConfig(Protocol):
    """Protocol for generation configuration options"""

    response_mime_type: str | None
    response_schema: Any | None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def __init__(self, api_key: str, model: str, **kwargs: str) -> None:
        """Initialize the AI provider

        Args:
            api_key: API key for the service
            model: Model identifier/name
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.chat_history: list[Any] = []

    @abstractmethod
    def reset(self) -> None:
        """Reset the conversation history"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        response_mime_type: str | None = None,
        response_schema: Any | None = None,
    ) -> ModelResponse:
        """Generate a response without maintaining conversation context

        Args:
            prompt: Input text prompt
            response_mime_type: Expected response format
                (e.g., "text/plain", "application/json")
            response_schema: Expected response structure schema

        Returns:
            ModelResponse containing the generated text and metadata
        """

    @abstractmethod
    def send_message(self, msg: str) -> ModelResponse:
        """Send a message in a conversational context

        Args:
            msg: Input message text

        Returns:
            ModelResponse containing the response text and metadata
        """
