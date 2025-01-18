from typing import Any, TypedDict

import google.generativeai as genai
from google.generativeai.types import ContentDict

from flare_ai_core.models.config import config


class Gemini:
    def __init__(self) -> None:
        genai.configure(api_key=config.api_key)
        self.chat: genai.ChatSession | None = None
        self.model = genai.GenerativeModel(
            model_name=config.model,
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


# Example usage:
if __name__ == "__main__":
    # Create library with default prompts
    gemini = Gemini()

    # Unstructured output
    prompt = """List a few popular cookie recipes in JSON format."""
    result = gemini.generate(prompt)

    class Recipe(TypedDict):
        recipe_name: str
        ingredients: list[str]

    # Structured output
    prompt = """List a few popular cookie recipes in JSON format."""
    result = gemini.generate(prompt, response_schema=list[Recipe])
