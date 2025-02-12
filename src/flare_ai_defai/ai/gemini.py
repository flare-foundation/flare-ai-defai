"""
Gemini AI Provider Module

This module implements the Gemini AI provider for the AI Agent API, integrating
with Google's Generative AI service. It handles chat sessions, content generation,
and message management while maintaining a consistent AI personality.
"""

from typing import Any, override

import google.generativeai as genai
import structlog
from google.generativeai.types import ContentDict

from flare_ai_defai.ai.base import BaseAIProvider, ModelResponse

logger = structlog.get_logger(__name__)


SYSTEM_INSTRUCTION = """
You are Artemis, an AI assistant specialized in helping users navigate
the Flare blockchain ecosystem. As an expert in blockchain data and operations,
you assist users with:

- Account creation and management on the Flare network
- Token swaps and transfers
- Understanding blockchain data structures and smart contracts
- Explaining technical concepts in accessible terms
- Monitoring network status and transaction processing

Your personality combines technical precision with light wit - you're
knowledgeable but approachable, occasionally using clever remarks while staying
focused on providing accurate, actionable guidance. You prefer concise responses
that get straight to the point, but can elaborate when technical concepts
need more explanation.

When helping users:
- Prioritize security best practices
- Verify user understanding of important steps
- Provide clear warnings about risks when relevant
- Format technical information (addresses, hashes, etc.) in easily readable ways

If users request operations you cannot directly perform, clearly explain what
steps they need to take themselves while providing relevant guidance.

You maintain professionalism while allowing your subtle wit to make interactions
more engaging - your goal is to be helpful first, entertaining second.
"""


class GeminiProvider(BaseAIProvider):
    """
    Provider class for Google's Gemini AI service.

    This class implements the BaseAIProvider interface to provide AI capabilities
    through Google's Gemini models. It manages chat sessions, generates content,
    and maintains conversation history.

    Attributes:
        chat (genai.ChatSession | None): Active chat session
        model (genai.GenerativeModel): Configured Gemini model instance
        chat_history (list[ContentDict]): History of chat interactions
        logger (BoundLogger): Structured logger for the provider
    """

    def __init__(self, api_key: str, model: str, **kwargs: str) -> None:
        """
        Initialize the Gemini provider with API credentials and model configuration.

        Args:
            api_key (str): Google API key for authentication
            model (str): Gemini model identifier to use
            **kwargs (str): Additional configuration parameters including:
                - system_instruction: Custom system prompt for the AI personality
        """
        genai.configure(api_key=api_key)  # pyright: ignore [reportPrivateImportUsage]
        self.chat: genai.ChatSession | None = None  # pyright: ignore [reportPrivateImportUsage]
        self.model = genai.GenerativeModel(  # pyright: ignore [reportPrivateImportUsage]
            model_name=model,
            system_instruction=kwargs.get("system_instruction", SYSTEM_INSTRUCTION),
        )
        self.chat_history: list[ContentDict] = [
            ContentDict(parts=["Hi, I'm Artemis"], role="model")
        ]
        self.logger = logger.bind(service="gemini")

    @override
    def reset(self) -> None:
        """
        Reset the provider state.

        Clears chat history and terminates active chat session.
        """
        self.chat_history = []
        self.chat = None
        self.logger.debug(
            "reset_gemini", chat=self.chat, chat_history=self.chat_history
        )

    @override
    def generate(
        self,
        prompt: str,
        response_mime_type: str | None = None,
        response_schema: Any | None = None,
    ) -> ModelResponse:
        """
        Generate content using the Gemini model.

        Args:
            prompt (str): Input prompt for content generation
            response_mime_type (str | None): Expected MIME type for the response
            response_schema (Any | None): Schema defining the response structure

        Returns:
            ModelResponse: Generated content with metadata including:
                - text: Generated text content
                - raw_response: Complete Gemini response object
                - metadata: Additional response information including:
                    - candidate_count: Number of generated candidates
                    - prompt_feedback: Feedback on the input prompt
        """
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(  # pyright: ignore [reportPrivateImportUsage]
                response_mime_type=response_mime_type, response_schema=response_schema
            ),
        )
        self.logger.debug("generate", prompt=prompt, response_text=response.text)
        return ModelResponse(
            text=response.text,
            raw_response=response,
            metadata={
                "candidate_count": len(response.candidates),
                "prompt_feedback": response.prompt_feedback,
            },
        )

    @override
    def send_message(
        self,
        msg: str,
    ) -> ModelResponse:
        """
        Send a message in a chat session and get the response.

        Initializes a new chat session if none exists, using the current chat history.

        Args:
            msg (str): Message to send to the chat session

        Returns:
            ModelResponse: Response from the chat session including:
                - text: Generated response text
                - raw_response: Complete Gemini response object
                - metadata: Additional response information including:
                    - candidate_count: Number of generated candidates
                    - prompt_feedback: Feedback on the input message
        """
        if not self.chat:
            self.chat = self.model.start_chat(history=self.chat_history)
        response = self.chat.send_message(msg)
        self.logger.debug("send_message", msg=msg, response_text=response.text)
        return ModelResponse(
            text=response.text,
            raw_response=response,
            metadata={
                "candidate_count": len(response.candidates),
                "prompt_feedback": response.prompt_feedback,
            },
        )
