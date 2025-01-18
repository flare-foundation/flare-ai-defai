import enum
from dataclasses import dataclass
from string import Template
from typing import TypedDict

semantic_router_template = """
Given the following input, identify which of the
responses make the most sense:

1. Generate account: The user clearly states they want to generate a new account.
2. Send token: The user clearly states that they want to send tokens.
3. Swap token: The user clearly states that they want to swap tokens.
4. Request attestation: The user clearly states that they want a remote attestation.
5. Conversational: The user is unclear, maybe they just want to chat. This
    is your default response.

<input>
${user_input}
</input>
"""


class SemanticRouterResponse(enum.Enum):
    GENERATE_ACCOUNT = "GenerateAccount"
    SEND_TOKEN = "SendToken"
    SWAP_TOKEN = "SwapToken"
    REQUEST_ATTESTATION = "RequestAttestation"
    CONVERSATIONAL = "Conversational"


generate_account_prompt = """
You have just generated a new account for the user.
Send them a message showing that you are excited to have them on board.
Highlight how the account is secured using TEEs.

The message must clearly contain the following account address:

${address}

DO NOT change anything in the address. Addresses can be shared publicly.
"""


token_send_template = """
Given the following input, identify:
1. Address to swap to
2. Amount to swap

<input>
${user_input}
</input>

If the amount is an integer, convert it to floating point.
"""

token_send_follow_up_template = """
A user tried to initiate a token send, but provided insufficient info.

Make it clear to them that they need to provide:

1. Address to send to: e.g. 0xE2Cbb26fB6EBb050191aaa040b75959Fe6888888
2. Amount to send: How many FLR tokens they want to send
"""


class TokenSendResponse(TypedDict):
    to_address: str
    amount: float


token_swap_template = """
Given the following input, identify:
1. Token to swap from: e.g. FLR or flr
2. Token to swap to: e.g. USDC or usdc
3. Amount to swap: This can be a float or an int. If
    the user supplies an int, convert it to float.

<input>
${user_input}
</input>
"""


class TokenSwapResponse(TypedDict):
    from_token: str
    to_token: str
    amount: float


token_swap_follow_up_template = """
A user tried to initiate a token swap, but provided insufficient info.

Make it clear to them that they need to provide:

1. Token to swap from: e.g. FLR or flr
2. Token to swap to: e.g. USDC or usdc
3. Amount to swap: How many tokens they want to swap

"""

sentiment_analysis_template = """
Analyze the sentiment of the following text:

<input>
${user_input}
</input>

Provide a rating from 1-5 where:
1: Very Negative
2: Negative
3: Neutral
4: Positive
5: Very Positive
"""


conversational_template = """
Pretend you are Artemis, AI agent of Flare.
Flare is the full-stack blockchain for data.
Respond creatively to what the user says.

<input>
${user_input}
</input>
"""

tx_confirmation_template = """
The user has successfully confirmed a transaction.
Send them a message showing that you are happy for them.

The message must clearly contain the following transaction hash:

${tx_hash}

DO NOT change anything in the tx_hash.
"""

remote_attestation_template = """
The user has requested a remote attestation from a TEE.
Inform them that they need to supply a random message that is between
10 and 74 characters

They should only supply the random message in their next chat and NOTHING ELSE.

The user should then visit the URL https://jwt.io and check the attestation response,
the response MUST contain the random message that the user sends.
"""


class PromptInputs(TypedDict, total=False):
    user_input: str
    text: str
    content: str
    code: str


@dataclass
class Prompt:
    name: str
    description: str
    template: str
    required_inputs: list[str] | None
    response_schema: type | None
    response_mime_type: str | None
    examples: list[dict[str, str]] | None = None
    category: str | None = None
    version: str = "1.0"

    def format(self, **kwargs: str | PromptInputs) -> str:
        if not self.required_inputs:
            msg = "Nothing to format"
            raise ValueError(msg)
        try:
            return Template(self.template).safe_substitute(**kwargs)
        except KeyError:
            missing_keys = set(self.required_inputs) - set(kwargs.keys())
            if missing_keys:
                msg = f"Missing required inputs: {missing_keys}"
                raise ValueError(msg) from None
            raise


class PromptLibrary:
    def __init__(self) -> None:
        self.prompts: dict[str, Prompt] = {}
        self._initialize_default_prompts()

    def _initialize_default_prompts(self) -> None:
        default_prompts = [
            Prompt(
                name="semantic_router",
                description="Route user query based on user input",
                template=semantic_router_template,
                required_inputs=["user_input"],
                response_mime_type="text/x.enum",
                response_schema=SemanticRouterResponse,
                category="router",
            ),
            Prompt(
                name="token_send",
                description="Extract token send parameters from user input",
                template=token_send_template,
                required_inputs=["user_input"],
                response_mime_type="application/json",
                response_schema=TokenSendResponse,
                category="defai",
            ),
            Prompt(
                name="follow_up_token_send",
                description="Follow up with a user about sending tokens",
                template=token_send_follow_up_template,
                required_inputs=None,
                response_schema=None,
                response_mime_type=None,
                category="follow_up",
            ),
            Prompt(
                name="token_swap",
                description="Extract token swap parameters from user input",
                template=token_swap_template,
                required_inputs=["user_input"],
                response_schema=TokenSwapResponse,
                response_mime_type="application/json",
                category="defai",
            ),
            Prompt(
                name="follow_up_token_swap",
                description="Follow up with a user about swapping tokens",
                template=token_swap_follow_up_template,
                required_inputs=None,
                response_schema=None,
                response_mime_type=None,
                category="follow_up",
            ),
            Prompt(
                name="generate_account",
                description="Generate a new account for a user",
                template=generate_account_prompt,
                required_inputs=["address"],
                response_schema=None,
                response_mime_type=None,
                category="account",
            ),
            Prompt(
                name="tx_confirmation",
                description="Confirm a user's transaction",
                template=tx_confirmation_template,
                required_inputs=["tx_hash"],
                response_schema=None,
                response_mime_type=None,
                category="account",
            ),
            Prompt(
                name="conversational",
                description="Converse with a user",
                template=conversational_template,
                required_inputs=["user_input"],
                response_schema=None,
                response_mime_type=None,
                category="conversational",
            ),
            Prompt(
                name="request_attestation",
                description="User has requested a remote attestation",
                template=remote_attestation_template,
                required_inputs=None,
                response_schema=None,
                response_mime_type=None,
                category="conversational",
            ),
        ]

        for prompt in default_prompts:
            self.add_prompt(prompt)

    def add_prompt(self, prompt: Prompt) -> None:
        self.prompts[prompt.name] = prompt

    def get_prompt(self, name: str) -> Prompt:
        if name not in self.prompts:
            msg = f"Prompt '{name}' not found in library"
            logger.exception(msg)
            raise KeyError(msg)
        return self.prompts[name]

    def get_prompts_by_category(self, category: str) -> list[Prompt]:
        return [
            prompt for prompt in self.prompts.values() if prompt.category == category
        ]

    def list_categories(self) -> list[str]:
        return list(
            {
                prompt.category
                for prompt in self.prompts.values()
                if prompt.category is not None
            }
        )


# Example usage:
if __name__ == "__main__":
    # Create library with default prompts
    library = PromptLibrary()

    # Use token swap prompt
    swap_prompt = library.get_prompt("token_swap")
    formatted_swap = swap_prompt.format(user_input="Swap 10 FLR to USDC")

    # Use semantic router
    swap_prompt = library.get_prompt("semantic_router")
    formatted_swap = swap_prompt.format(user_input="Generate an account for me")
