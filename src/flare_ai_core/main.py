import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from flare_ai_core import ChatRouter, FlareProvider, GeminiProvider, PromptService, Vtpm
from flare_ai_core.settings import settings

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="AI Agent API", version=settings.api_version)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize router
    chat = ChatRouter(
        ai=GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model),
        blockchain=FlareProvider(web3_provider_url=settings.web3_provider_url),
        attestation=Vtpm(simulate=settings.simulate_attestation),
        prompts=PromptService(),
    )

    # Register routes
    app.include_router(chat.router, prefix="/api/routes/chat", tags=["chat"])

    return app


app = create_app()


def start() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104


if __name__ == "__main__":
    start()
