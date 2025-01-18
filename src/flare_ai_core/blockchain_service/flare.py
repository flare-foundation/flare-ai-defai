import logging
from dataclasses import dataclass

from eth_account import Account
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.types import TxParams


@dataclass
class TxQueueElement:
    msg: str
    tx: TxParams


logger = logging.getLogger()


class Flare:
    def __init__(self, web3_provider_url: str) -> None:
        self.address: ChecksumAddress | None = None
        self.private_key: str | None = None
        self.tx_queue: list[TxQueueElement] = []
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))

    def reset(self) -> str:
        self.address = None
        self.private_key = None
        self.tx_queue = []
        return "Reset account history"

    def add_tx_to_queue(self, msg: str, tx: TxParams) -> None:
        tx_queue_element = TxQueueElement(msg=msg, tx=tx)
        self.tx_queue.append(tx_queue_element)
        logger.debug("Added tx to queue: %s", self.tx_queue)

    def send_tx_in_queue(self) -> str:
        if self.tx_queue:
            tx_hash = self.sign_and_send_transaction(self.tx_queue[-1].tx)
            self.tx_queue.pop()
            return tx_hash
        msg = "Unable to find confirmed tx"
        raise ValueError(msg)

    def generate_account(self) -> ChecksumAddress:
        account = Account.create()
        self.private_key = account.key.hex()
        self.address = self.w3.to_checksum_address(account.address)
        return self.address

    def sign_and_send_transaction(self, tx: TxParams) -> str:
        """Sign and send a transaction, then wait for receipt."""
        if not self.private_key or not self.address:
            msg = "Account not initialized"
            raise ValueError(msg)
        signed_tx = self.w3.eth.account.sign_transaction(
            tx, private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return "0x" + tx_hash.hex()

    def check_balance(self) -> float:
        if not self.address:
            msg = "Account does not exist"
            raise ValueError(msg)
        balance_wei = self.w3.eth.get_balance(self.address)
        return float(self.w3.from_wei(balance_wei, "ether"))

    def create_send_flr_tx(self, to_address: str, amount: float) -> TxParams:
        if not self.address:
            msg = "Account does not exist"
            raise ValueError(msg)
        tx: TxParams = {
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "to": self.w3.to_checksum_address(to_address),
            "value": self.w3.to_wei(amount, unit="ether"),
            "gas": 21000,
            "maxFeePerGas": self.w3.eth.gas_price,
            "maxPriorityFeePerGas": self.w3.eth.max_priority_fee,
            "chainId": self.w3.eth.chain_id,
            "type": 2,
        }
        return tx
