from typing import Any

import google.generativeai as genai
from google.generativeai.types import ContentDict


class Gemini:
    def __init__(self, api_key: str, model: str) -> None:
        genai.configure(api_key=api_key)
        self.chat: genai.ChatSession | None = None
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction="Your name is Artemis and you run on Flare, "
            "the blockchain for data. You can help users to "
            "generate a new account, swap and send tokens.",
        )

    def generate(
        self,
        prompt: str,
        response_mime_type: str | None = None,
        response_schema: Any | None = None,
    ) -> genai.types.GenerateContentResponse:
        return self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type=response_mime_type, response_schema=response_schema
            ),
        )

    def send_message(
        self,
        msg: str,
    ) -> str:
        if not self.chat:
            history = [ContentDict(parts=["Hi, I'm Artemis"], role="model")]
            self.chat = self.model.start_chat(history=history)
        res = self.chat.send_message(msg)
        return res.text
