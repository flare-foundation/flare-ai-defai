import json
import logging

import requests
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)


class FlareExplorer:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def _get(self, params: dict) -> dict:
        """Get data from the Chain Explorer API.

        :param params: Query parameters
        :return: JSON response
        """
        headers = {"accept": "application/json"}
        try:
            response = requests.get(
                self.base_url, params=params, headers=headers, timeout=10
            )
            response.raise_for_status()
            json_response = response.json()

            if "result" not in json_response:
                msg = (f"Malformed response from API: {json_response}",)
                raise ValueError(msg)

        except (RequestException, Timeout):
            logger.exception("Network error during API request")
            raise
        else:
            return json_response

    def get_contract_abi(self, contract_address: str) -> dict:
        """Get the ABI for a contract from the Chain Explorer API.

        :param contract_address: Address of the contract
        :return: Contract ABI
        """
        logger.info("Fetching ABI for `%s` from `%s`", contract_address, self.base_url)
        response = self._get(
            params={
                "module": "contract",
                "action": "getabi",
                "address": contract_address,
            }
        )
        return json.loads(response["result"])
