from dataclasses import dataclass

from flare_ai_core.config import Config, load_env_var
from flare_ai_core.config import config as base_config


@dataclass(frozen=True)
class GeminiConfig(Config):
    api_key: str
    model: str


config = GeminiConfig(
    **vars(base_config),
    api_key=load_env_var("GEMINI_API_KEY"),
    model=load_env_var("GEMINI_MODEL"),
)
