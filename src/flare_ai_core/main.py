import json

from web3 import Web3

from flare_ai_core.defai.prompt_library import PromptLibrary, SemanticRouterResponse
from flare_ai_core.models.gemini import Gemini
from flare_ai_core.onchain.account import AgentAccount


def generate_account() -> tuple[AgentAccount, str]:
    user_account = AgentAccount()
    address = user_account.generate_account()
    account_prompt = library.get_prompt("generate_account")
    formatted_account = account_prompt.format(address=address)
    res = gemini.generate(
        formatted_account,
    )
    return user_account, res.text


def get_user_confirmation(msg: str) -> bool:
    msg += "\nType CONFIRM in ALL CAPS to confirm.\n"
    confirmation = input(msg)
    return confirmation == "CONFIRM"


def send_token(
    user_account: AgentAccount, library: PromptLibrary, gemini: Gemini
) -> None:
    send_prompt = library.get_prompt("token_send")
    formatted_send = send_prompt.format(user_input=user_input)
    res = gemini.generate(
        formatted_send,
        send_prompt.response_mime_type,
        send_prompt.response_schema,
    )
    res_json = json.loads(res.text)
    expected_res_length = 2
    if len(res_json) != expected_res_length or res_json.get("amount") == 0.0:
        send_prompt = library.get_prompt("follow_up_token_send")
        formatted_send = send_prompt.format()
        res = gemini.generate(formatted_send)
    tx = user_account.create_send_flr_tx(
        res_json.get("to_address"), res_json.get("amount")
    )

    msg = f"Sending {Web3.from_wei(tx.get('value', 0), 'ether')} FLR to {tx.get('to')}."
    confirmed = get_user_confirmation(msg)
    if confirmed:
        tx_hash = user_account.sign_and_send_transaction(tx)
        tx_confirmation_prompt = library.get_prompt("tx_confirmation")
        formatted_tx_confirmation = tx_confirmation_prompt.format(tx_hash=tx_hash)
        res = gemini.generate(
            formatted_tx_confirmation,
        )
        print(res.text)


if __name__ == "__main__":
    # Set up classes
    library = PromptLibrary()
    gemini = Gemini()

    print("Hi, I'm Artemis")

    user_account = None
    # Using the semantic router
    while True:
        user_input = input("Input: ")
        router_prompt = library.get_prompt("semantic_router")
        formatted_router = router_prompt.format(user_input=user_input)
        res = gemini.generate(
            formatted_router,
            router_prompt.response_mime_type,
            router_prompt.response_schema,
        )
        print(res.text)

        match res.text.strip('"'):
            case SemanticRouterResponse.GENERATE_ACCOUNT.value:
                # Generate onchain action
                user_account, response = generate_account()
                print(response)
            case SemanticRouterResponse.SEND_TOKEN.value:
                # Using the token send prompt
                if not user_account:
                    user_account, response = generate_account()
                    print(response)
                send_token(user_account, library, gemini)
            case SemanticRouterResponse.SWAP_TOKEN.value:
                # Using the token swap prompt
                swap_prompt = library.get_prompt("token_swap")
                formatted_swap = swap_prompt.format(user_input=user_input)
                res = gemini.generate(
                    formatted_swap,
                    swap_prompt.response_mime_type,
                    swap_prompt.response_schema,
                )
                res_json = json.loads(res.text)
                expected_res_length = 3
                if (
                    len(res_json) != expected_res_length
                    or res_json.get("amount") == 0.0
                ):
                    swap_prompt = library.get_prompt("follow_up_token_swap")
                    formatted_swap = swap_prompt.format()
                    res = gemini.generate(formatted_swap)
                    print(res.text)
                    continue
                print(res_json)
            case _:
                # Using the token swap prompt
                conversational_prompt = library.get_prompt("conversational")
                formatted_conversation = conversational_prompt.format(
                    user_input=user_input
                )
                res = gemini.generate(
                    formatted_conversation,
                )
                print(res.text)
