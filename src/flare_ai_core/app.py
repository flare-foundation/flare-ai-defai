import json
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3

from flare_ai_core.attestation import VtpmAttestation
from flare_ai_core.config import config
from flare_ai_core.models import Gemini, PromptLibrary, SemanticRouterResponse
from flare_ai_core.onchain import AgentAccount

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize classes
LIBRARY = PromptLibrary()
GEMINI = Gemini()
USER_ACCOUNT = AgentAccount()
ATTESTATION = VtpmAttestation(simulate=config.simulate_attestation)

RA_QUEUE = []


class ChatMessage(BaseModel):
    message: str


@app.post("/api/chat")
async def chat(message: ChatMessage) -> dict[str, str]:
    logger.debug("Received message: %s", message.message)

    if message.message.startswith("/"):
        match message.message:
            case "/reset":
                res = USER_ACCOUNT.reset()
                return {"response": res}
            case _:
                pass

    # After confirmation, send tx
    if USER_ACCOUNT.tx_queue:
        return {"response": await handle_confirmed_tx(message.message)}
    if RA_QUEUE:
        res = {"response": ATTESTATION.get_token(nonces=[message.message])}
        RA_QUEUE.clear()
        return res

    try:
        router_response = await handle_semantic_routing(message.message)

        match router_response:
            case SemanticRouterResponse.GENERATE_ACCOUNT:
                if not USER_ACCOUNT.address:
                    response = handle_generate_account()
                else:
                    response = f"Account already exists - {USER_ACCOUNT.address}"
            case SemanticRouterResponse.SEND_TOKEN:
                if not USER_ACCOUNT.address:
                    gen_response = handle_generate_account()
                    response = f"{gen_response}\n"
                response = await handle_send_token(message.message)
            case SemanticRouterResponse.SWAP_TOKEN:
                if not USER_ACCOUNT.address:
                    gen_response = handle_generate_account()
                    response = f"{gen_response}\n"
                response = await handle_swap_token(message.message)
            case SemanticRouterResponse.REQUEST_ATTESTATION:
                response = await handle_remote_attestation()
            case _:
                conversational_prompt = LIBRARY.get_prompt("conversational")
                formatted_conversation = conversational_prompt.format(
                    user_input=message.message
                )
                conv_res = GEMINI.generate(formatted_conversation)
                response = conv_res.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return {"response": response}


def handle_generate_account() -> str:
    address = USER_ACCOUNT.generate_account()
    account_prompt = LIBRARY.get_prompt("generate_account")
    formatted_account = account_prompt.format(address=address)
    res = GEMINI.generate(
        formatted_account,
    )
    return res.text


async def handle_send_token(user_input: str) -> str:
    send_prompt = LIBRARY.get_prompt("token_send")
    formatted_send = send_prompt.format(user_input=user_input)
    res = GEMINI.generate(
        formatted_send,
        send_prompt.response_mime_type,
        send_prompt.response_schema,
    )

    try:
        res_json = json.loads(res.text)
        if len(res_json) != 2 or res_json.get("amount") == 0.0:
            follow_up_prompt = LIBRARY.get_prompt("follow_up_token_send")
            formatted_follow_up = follow_up_prompt.format()
            res = GEMINI.generate(formatted_follow_up)
            return res.text

        tx = USER_ACCOUNT.create_send_flr_tx(
            res_json.get("to_address"), res_json.get("amount")
        )
        logger.debug("Tx: %s", tx)
        USER_ACCOUNT.add_tx_to_queue(msg=user_input, tx=tx)

        # Return transaction preview
        return f"Transaction Preview:\nSending {Web3.from_wei(tx.get('value', 0), 'ether')} FLR to {tx.get('to')}\nType CONFIRM to proceed."

    except Exception as e:
        return f"Error creating transaction: {e!s}"


async def handle_remote_attestation() -> str:
    try:
        ra_prompt = LIBRARY.get_prompt("request_attestation")
        res = GEMINI.generate(
            ra_prompt.template
        )
        logger.debug("RA response: %s", res.text)
        RA_QUEUE.append(res.text)
    except Exception as e:
        msg = "Error confirming tx"
        logger.exception(msg)
        return f"{msg}: {e!s}"
    else:
        return res.text

async def handle_confirmed_tx(msg: str) -> str:
    try:
        tx_hash = USER_ACCOUNT.send_confirmed_tx_and_pop_queue(msg)
        tx_confirmation_prompt = LIBRARY.get_prompt("tx_confirmation")
        formatted_tx_confirmation = tx_confirmation_prompt.format(tx_hash=tx_hash)
        res = GEMINI.generate(
            formatted_tx_confirmation,
        )
        logger.debug("Response: %s", res.text)
    except Exception as e:
        msg = "Error confirming tx"
        logger.exception(msg)
        return f"{msg}: {e!s}"
    else:
        return res.text


def map_to_enum(value: str) -> SemanticRouterResponse:
    try:
        return next(
            enum_value
            for enum_value in SemanticRouterResponse
            if enum_value.value == value
        )
    except StopIteration as e:
        msg = f"No matching enum value for: {value}"
        raise ValueError(msg) from e


async def handle_semantic_routing(msg: str) -> SemanticRouterResponse:
    try:
        # Use the semantic router
        router_prompt = LIBRARY.get_prompt("semantic_router")
        formatted_router = router_prompt.format(user_input=msg)
        res = GEMINI.generate(
            formatted_router,
            router_prompt.response_mime_type,
            router_prompt.response_schema,
        )
        logger.debug("Response: %s", res.text)
        return map_to_enum(res.text.strip('"'))
    except Exception:
        msg = "Error handling semantic routing"
        logger.exception(msg)
        return SemanticRouterResponse.CONVERSATIONAL


async def handle_swap_token(msg: str) -> str:
    swap_prompt = LIBRARY.get_prompt("token_swap")
    formatted_swap = swap_prompt.format(user_input=msg)
    swap_res = GEMINI.generate(
        formatted_swap,
        swap_prompt.response_mime_type,
        swap_prompt.response_schema,
    )
    return swap_res.text


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
