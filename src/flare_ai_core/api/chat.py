import json

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from web3 import Web3

from flare_ai_core.ai_service import Gemini
from flare_ai_core.attestation_service import Vtpm
from flare_ai_core.blockchain_service import Flare
from flare_ai_core.prompt_service import PromptService, SemanticRouterResponse
from flare_ai_core.settings import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1)


class ChatRouter:
    def __init__(
        self,
        ai_service: Gemini,
        blockchain_service: Flare,
        attestation_service: Vtpm,
        prompt_service: PromptService,
    ) -> None:
        self._router = APIRouter()

        self.ai_service = ai_service
        self.blockchain_service = blockchain_service
        self.attestation_service = attestation_service
        self.prompt_service = prompt_service
        self.logger = logger.bind(router="chat")
        self._setup_routes()

    def _setup_routes(self) -> None:
        @self._router.post("/")
        async def chat(message: ChatMessage) -> dict[str, str]: # pyright: ignore [reportUnusedFunction]
            try:
                self.logger.debug("received_message", message=message.message)

                if message.message.startswith("/"):
                    return await self.handle_command(message.message)
                if (
                    self.blockchain_service.tx_queue
                    and message.message == self.blockchain_service.tx_queue[-1].msg
                ):
                    tx_hash = self.blockchain_service.send_tx_in_queue()
                    prompt, mime_type, schema = (
                        self.prompt_service.get_formatted_prompt(
                            "tx_confirmation",
                            tx_hash=tx_hash,
                            block_explorer=settings.web3_explorer_url,
                        )
                    )
                    tx_confirmation_response = self.ai_service.generate(
                        prompt=prompt,
                        response_mime_type=mime_type,
                        response_schema=schema,
                    )
                    return {"response": tx_confirmation_response.text}
                if self.attestation_service.attestation_requested:
                    token = self.attestation_service.get_token([message.message])
                    return {"response": token}

                route = await self.get_semantic_route(message.message)
                return await self.route_message(route, message.message)

            except Exception as e:
                self.logger.exception("message_handling_failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e)) from e

    @property
    def router(self) -> APIRouter:
        """Get the FastAPI router with registered routes."""
        return self._router

    async def handle_command(self, command: str) -> dict[str, str]:
        if command == "/reset":
            self.blockchain_service.reset()
            # Implement reset logic
            return {"response": "Reset completed"}
        return {"response": "Unknown command"}

    async def get_semantic_route(self, message: str) -> SemanticRouterResponse:
        try:
            prompt, mime_type, schema = self.prompt_service.get_formatted_prompt(
                "semantic_router", user_input=message
            )
            route_response = self.ai_service.generate(
                prompt=prompt, response_mime_type=mime_type, response_schema=schema
            )
            return SemanticRouterResponse(route_response.text)
        except Exception as e:
            self.logger.exception("routing_failed", error=str(e))
            return SemanticRouterResponse.CONVERSATIONAL

    async def route_message(
        self, route: SemanticRouterResponse, message: str
    ) -> dict[str, str]:
        handlers = {
            SemanticRouterResponse.GENERATE_ACCOUNT: self.handle_generate_account,
            SemanticRouterResponse.SEND_TOKEN: self.handle_send_token,
            SemanticRouterResponse.SWAP_TOKEN: self.handle_swap_token,
            SemanticRouterResponse.REQUEST_ATTESTATION: self.handle_attestation,
            SemanticRouterResponse.CONVERSATIONAL: self.handle_conversation,
        }

        handler = handlers.get(route)
        if not handler:
            return {"response": "Unsupported route"}

        return await handler(message)

    async def handle_generate_account(self, _: str) -> dict[str, str]:
        if self.blockchain_service.address:
            return {"response": f"Account exists - {self.blockchain_service.address}"}
        address = self.blockchain_service.generate_account()
        prompt, mime_type, schema = self.prompt_service.get_formatted_prompt(
            "generate_account", address=address
        )
        gen_address_response = self.ai_service.generate(
            prompt=prompt, response_mime_type=mime_type, response_schema=schema
        )
        return {"response": gen_address_response.text}

    async def handle_send_token(self, message: str) -> dict[str, str]:
        if not self.blockchain_service.address:
            await self.handle_generate_account(message)

        prompt, mime_type, schema = self.prompt_service.get_formatted_prompt(
            "token_send", user_input=message
        )
        send_token_response = self.ai_service.generate(
            prompt=prompt, response_mime_type=mime_type, response_schema=schema
        )
        send_token_json = json.loads(send_token_response.text)
        expected_json_len = 2
        if (
            len(send_token_json) != expected_json_len
            or send_token_json.get("amount") == 0.0
        ):
            prompt, _, _ = self.prompt_service.get_formatted_prompt(
                "follow_up_token_send"
            )
            follow_up_response = self.ai_service.generate(prompt)
            return {"response": follow_up_response.text}

        tx = self.blockchain_service.create_send_flr_tx(
            to_address=send_token_json.get("to_address"),
            amount=send_token_json.get("amount"),
        )
        self.logger.debug("send_token_tx", tx=tx)
        self.blockchain_service.add_tx_to_queue(msg=message, tx=tx)
        formatted_preview = (
            "Transaction Preview: "
            + f"Sending {Web3.from_wei(tx.get('value', 0), 'ether')} "
            + f"FLR to {tx.get('to')}\nType CONFIRM to proceed."
        )
        return {"response": formatted_preview}

    async def handle_swap_token(self, _: str) -> dict[str, str]:
        return {"response": "Sorry I can't do that right now"}

    async def handle_attestation(self, _: str) -> dict[str, str]:
        prompt = self.prompt_service.get_formatted_prompt("request_attestation")[0]
        request_attestation_response = self.ai_service.generate(prompt=prompt)
        self.attestation_service.attestation_requested = True
        return {"response": request_attestation_response.text}

    async def handle_conversation(self, message: str) -> dict[str, str]:
        response = self.ai_service.generate(message)
        return {"response": response.text}
