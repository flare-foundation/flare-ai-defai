from typing import Any, override

import google.generativeai as genai
import structlog
from google.generativeai.types import ContentDict

from flare_ai_core.ai.base import BaseAIProvider, ModelResponse

logger = structlog.get_logger(__name__)


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str, **kwargs: str) -> None:
        genai.configure(api_key=api_key)
        self.chat: genai.ChatSession | None = None
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=kwargs.get(
                "system_instruction",
                "Your name is Artemis and you run on Flare, "
                "the blockchain for data. You can help users to "
                "generate a new account, swap and send tokens. "
                "Artemis is mildly sarcastic but smart and concise in their responses.",
            ),
        )
        self.chat_history: list[ContentDict] = [
            ContentDict(parts=["Hi, I'm Artemis"], role="model")
        ]
        self.logger = logger.bind(service="gemini")

    @override
    def reset(self) -> None:
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
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
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
