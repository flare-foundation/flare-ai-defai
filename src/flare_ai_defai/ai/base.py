from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Protocol, TypedDict, runtime_checkable

import httpx
import requests


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


class CompletionRequest(TypedDict):
    model: str
    prompt: str


class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(TypedDict):
    model: str
    messages: list[Message]


class BaseRouter:
    """A base class to handle HTTP requests and common logic for API interaction."""

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        """
        :param base_url: The base URL for the API.
        :param api_key: Optional API key for authentication.
        """
        self.base_url = base_url.rstrip("/")  # Ensure no trailing slash
        self.api_key = api_key
        self.session = requests.Session()
        # Set up headers: include the Authorization header if an API key is provided.
        self.headers = {"accept": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        """
        Make a GET request to the API and return the JSON response.

        :param endpoint: The API endpoint (should begin with a slash, e.g., "/models").
        :param params: Optional query parameters.
        :return: JSON response as a dictionary.
        """
        params = params or {}

        url = self.base_url + endpoint
        response = self.session.get(
            url=url, params=params, headers=self.headers, timeout=30
        )

        success_status = 200
        if response.status_code == success_status:
            return response.json()
        msg = f"Error ({response.status_code}): {response.text}"
        raise ConnectionError(msg)

    def _post(
        self,
        endpoint: str,
        json_payload: dict[str, Any] | CompletionRequest | ChatRequest,
    ) -> dict:
        """
        Make a POST request to the API with a JSON payload and return the JSON response.

        :param endpoint: The API endpoint (should begin with a slash,
            e.g., "/completions").
        :param json_payload: The JSON payload to send.
        :return: JSON response as a dictionary.
        """
        url = self.base_url + endpoint
        response = self.session.post(
            url=url, headers=self.headers, json=json_payload, timeout=30
        )

        success_status = 200
        if response.status_code == success_status:
            return response.json()
        msg = f"Error ({response.status_code}): {response.text}"
        raise ConnectionError(msg)


class AsyncBaseRouter:
    """
    An asynchronous base class to handle HTTP requests and
    common logic for API interaction.
    """

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        """
        :param base_url: The base URL for the API.
        :param api_key: Optional API key for authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {"accept": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        """
        Make an asynchronous GET request to the API and return the JSON response.

        :param endpoint: The API endpoint (should begin with a slash, e.g., "/models").
        :param params: Optional query parameters.
        :return: JSON response as a dictionary.
        """
        params = params or {}
        url = self.base_url + endpoint
        response = await self.client.get(url, params=params, headers=self.headers)

        success_status = 200
        if response.status_code == success_status:
            return response.json()
        msg = f"Error ({response.status_code}): {response.text}"
        raise ConnectionError(msg)

    async def _post(
        self,
        endpoint: str,
        json_payload: dict[str, Any] | CompletionRequest | ChatRequest,
    ) -> dict:
        """
        Make an asynchronous POST request to the API with a JSON
        payload and return the JSON response.

        :param endpoint: The API endpoint
            (should begin with a slash, e.g., "/completions").
        :param json_payload: The JSON payload to send.
        :return: JSON response as a dictionary.
        """
        url = self.base_url + endpoint
        response = await self.client.post(url, headers=self.headers, json=json_payload)

        success_status = 200
        if response.status_code == success_status:
            return response.json()
        msg = f"Error ({response.status_code}): {response.text}"
        raise ConnectionError(msg)

    async def close(self) -> None:
        """
        Close the underlying asynchronous HTTP client.
        """
        await self.client.aclose()
