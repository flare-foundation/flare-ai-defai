from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    simulate_attestation: bool = False
    cors_origins: list[str] = ["*"]
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    api_version: str = "v1"
    web3_provider_url: str = "https://coston2-api.flare.network/ext/C/rpc"
    web3_explorer_url: str = "https://coston2-explorer.flare.network/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
