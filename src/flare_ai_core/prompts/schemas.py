from dataclasses import dataclass
from enum import Enum
from string import Template
from typing import TypedDict


class SemanticRouterResponse(str, Enum):
    GENERATE_ACCOUNT = "GenerateAccount"
    SEND_TOKEN = "SendToken"
    SWAP_TOKEN = "SwapToken"
    REQUEST_ATTESTATION = "RequestAttestation"
    CONVERSATIONAL = "Conversational"


class TokenSendResponse(TypedDict):
    to_address: str
    amount: float


class TokenSwapResponse(TypedDict):
    from_token: str
    to_token: str
    amount: float


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
            return self.template
        try:
            return Template(self.template).safe_substitute(**kwargs)
        except KeyError as e:
            missing_keys = set(self.required_inputs) - set(kwargs.keys())
            if missing_keys:
                msg = f"Missing required inputs: {missing_keys}"
                raise ValueError(msg) from e
            raise
