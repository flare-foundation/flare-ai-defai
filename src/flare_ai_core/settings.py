"""
Settings Configuration Module

This module defines the configuration settings for the AI Agent API
using Pydantic's BaseSettings. It handles environment variables and
provides default values for various service configurations.

The settings can be overridden by environment variables or through a .env file.
Environment variables take precedence over values defined in the .env file.
"""

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.get_logger(__name__)


class Settings(BaseSettings):
    """
    Application settings model that provides configuration for all components.

    Attributes:
        simulate_attestation (bool): Flag to enable/disable attestation simulation.
            Defaults to False.

        cors_origins (list[str]): List of allowed CORS origins.
            Defaults to ["*"] allowing all origins.

        gemini_api_key (str): API key for accessing Google's Gemini AI service.
            Must be provided via environment variable or .env file.
            Defaults to empty string.

        gemini_model (str): The Gemini model identifier to use.
            Defaults to "gemini-1.5-flash".

        api_version (str): Version string for the API.
            Defaults to "v1".

        web3_provider_url (str): URL for the Flare Network Web3 provider.
            Defaults to Coston2 testnet RPC endpoint:
            "https://coston2-api.flare.network/ext/C/rpc"

        web3_explorer_url (str): URL for the Flare Network block explorer.
            Defaults to Coston2 testnet explorer:
            "https://coston2-explorer.flare.network/"

    Environment Variables:
        All settings can be overridden by environment variables with the same name
        in uppercase, e.g.:
        - SIMULATE_ATTESTATION
        - CORS_ORIGINS
        - GEMINI_API_KEY
        - GEMINI_MODEL
        - API_VERSION
        - WEB3_PROVIDER_URL
        - WEB3_EXPLORER_URL
    """

    simulate_attestation: bool = False
    cors_origins: list[str] = ["*"]
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    api_version: str = "v1"
    web3_provider_url: str = "https://coston2-api.flare.network/ext/C/rpc"
    web3_explorer_url: str = "https://coston2-explorer.flare.network/"

    model_config = SettingsConfigDict(
        # This enables .env file support
        env_file=".env",
        # If .env file is not found, don't raise an error
        env_file_encoding="utf-8",
        # Optional: you can also specify multiple .env files
        extra="ignore",
    )


# Create a global settings instance
settings = Settings()
logger.debug("settings", settings=settings.model_dump())
