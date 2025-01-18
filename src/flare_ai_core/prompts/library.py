import structlog

from flare_ai_core.prompts.schemas import (
    Prompt,
    SemanticRouterResponse,
    TokenSendResponse,
    TokenSwapResponse,
)
from flare_ai_core.prompts.templates import (
    CONVERSATIONAL,
    GENERATE_ACCOUNT,
    REMOTE_ATTESTATION,
    SEMANTIC_ROUTER,
    TOKEN_SEND,
    TOKEN_SWAP,
    TX_CONFIRMATION,
)

logger = structlog.get_logger(__name__)


class PromptLibrary:
    def __init__(self) -> None:
        self.prompts: dict[str, Prompt] = {}
        self._initialize_default_prompts()

    def _initialize_default_prompts(self) -> None:
        default_prompts = [
            Prompt(
                name="semantic_router",
                description="Route user query based on user input",
                template=SEMANTIC_ROUTER,
                required_inputs=["user_input"],
                response_mime_type="text/x.enum",
                response_schema=SemanticRouterResponse,
                category="router",
            ),
            Prompt(
                name="token_send",
                description="Extract token send parameters from user input",
                template=TOKEN_SEND,
                required_inputs=["user_input"],
                response_mime_type="application/json",
                response_schema=TokenSendResponse,
                category="defai",
            ),
            Prompt(
                name="token_swap",
                description="Extract token swap parameters from user input",
                template=TOKEN_SWAP,
                required_inputs=["user_input"],
                response_schema=TokenSwapResponse,
                response_mime_type="application/json",
                category="defai",
            ),
            Prompt(
                name="generate_account",
                description="Generate a new account for a user",
                template=GENERATE_ACCOUNT,
                required_inputs=["address"],
                response_schema=None,
                response_mime_type=None,
                category="account",
            ),
            Prompt(
                name="conversational",
                description="Converse with a user",
                template=CONVERSATIONAL,
                required_inputs=["user_input"],
                response_schema=None,
                response_mime_type=None,
                category="conversational",
            ),
            Prompt(
                name="request_attestation",
                description="User has requested a remote attestation",
                template=REMOTE_ATTESTATION,
                required_inputs=None,
                response_schema=None,
                response_mime_type=None,
                category="conversational",
            ),
            Prompt(
                name="tx_confirmation",
                description="Confirm a user's transaction",
                template=TX_CONFIRMATION,
                required_inputs=["tx_hash", "block_explorer"],
                response_schema=None,
                response_mime_type=None,
                category="account",
            ),
        ]

        for prompt in default_prompts:
            self.add_prompt(prompt)

    def add_prompt(self, prompt: Prompt) -> None:
        """Add a new prompt to the library."""
        self.prompts[prompt.name] = prompt
        logger.debug("prompt_added", name=prompt.name, category=prompt.category)

    def get_prompt(self, name: str) -> Prompt:
        """Retrieve a prompt by name."""
        if name not in self.prompts:
            logger.error("prompt_not_found", name=name)
            msg = f"Prompt '{name}' not found in library"
            raise KeyError(msg)
        return self.prompts[name]

    def get_prompts_by_category(self, category: str) -> list[Prompt]:
        """Get all prompts in a specific category."""
        return [
            prompt for prompt in self.prompts.values() if prompt.category == category
        ]

    def list_categories(self) -> list[str]:
        """List all available prompt categories."""
        return list(
            {
                prompt.category
                for prompt in self.prompts.values()
                if prompt.category is not None
            }
        )
