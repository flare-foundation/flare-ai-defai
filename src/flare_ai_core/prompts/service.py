from typing import Any

import structlog

from flare_ai_core.prompts.library import PromptLibrary

logger = structlog.get_logger(__name__)


class PromptService:
    def __init__(self) -> None:
        self.library = PromptLibrary()
        self.logger = logger.bind(service="prompt")

    def get_formatted_prompt(
        self, prompt_name: str, **kwargs: Any
    ) -> tuple[str, str | None, type | None]:
        """
        Get a formatted prompt with its schema and mime type.

        Returns:
        tuple(formatted_prompt, response_schema, response_mime_type)
        """
        try:
            prompt = self.library.get_prompt(prompt_name)
            formatted = prompt.format(**kwargs)
        except Exception as e:
            self.logger.exception(
                "prompt_formatting_failed", prompt_name=prompt_name, error=str(e)
            )
            raise
        else:
            return (formatted, prompt.response_mime_type, prompt.response_schema)
