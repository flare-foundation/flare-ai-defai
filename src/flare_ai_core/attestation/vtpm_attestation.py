"""
Client for communicating with the Confidential Space vTPM attestation service.

This module provides a client to request attestation tokens from a local Unix domain
socket endpoint. It uses the requests library with a custom transport adapter to handle
Unix socket communication and implements token request functionality
with nonce validation.

Classes:
    VtpmAttestationError: Exception for attestation service communication errors
    VtpmAttestation: Client for requesting attestation tokens
"""

import json
from pathlib import Path

import requests
import structlog
from requests_unixsocket import UnixAdapter

logger = structlog.get_logger(__name__)


def get_simulated_token() -> str:
    """Reads the first line from a given file path."""
    with (Path(__file__).parent / "simulated_token.txt").open("r") as f:
        return f.readline().strip()


SIM_TOKEN = get_simulated_token()


class VtpmAttestationError(Exception):
    """
    Exception raised for attestation service communication errors.

    This includes invalid nonce values, connection failures, and
    unexpected responses from the attestation service.
    """


class Vtpm:
    """
    Client for requesting attestation tokens via Unix domain socket.

    Uses requests with UnixAdapter to communicate with the local attestation service
    through a Unix domain socket instead of TCP/IP.

    Args:
        unix_socket_path: Path to the attestation service Unix socket
            (default: "/run/container_launcher/teeserver.sock")
        simulate: Whether to run in simulation mode (default: False)

    Example:
    client = VtpmAttestation()
    try:
        token = client.get_token(
            nonces=["random_nonce_value"],
            audience="https://sts.google.com",
            token_type="OIDC"
        )
    except VtpmAttestationError as e:
        # Handle attestation error
    """

    def __init__(
        self,
        unix_socket_path: str = "/run/container_launcher/teeserver.sock",
        simulate: bool = False,  # noqa: FBT001,FBT002
    ) -> None:
        self.unix_socket_path = unix_socket_path
        self.simulate = simulate
        self.session: requests.Session | None = None
        self.attestation_requested: bool = False
        self.logger = logger.bind(router="vtpm")
        self.logger.debug("simulate_mode", simulate=simulate)

    def _get_session(self) -> requests.Session:
        """
        Get or create a requests session with Unix socket adapter.

        Returns:
            requests.Session: Session configured for Unix socket communication
        """
        if self.session is None:
            self.session = requests.Session()
            if not self.simulate:
                # Convert the Unix socket path to the format
                # expected by requests_unixsocket
                unix_url = f"http+unix://{self.unix_socket_path.replace('/', '%2F')}"
                self.session.mount("http+unix://", UnixAdapter())
                self.base_url = unix_url
                self.logger.debug(
                    "connect_socket", unix_socket_path=self.unix_socket_path
                )
        return self.session

    def _post(self, endpoint: str, body: str, headers: dict[str, str]) -> str:
        """
        Send POST request to attestation service endpoint.

        Args:
            endpoint: API endpoint path
            body: JSON request body
            headers: HTTP request headers

        Returns:
            str: Response content from the attestation service

        Raises:
            VtpmAttestationError: If request fails or response status is not 200
        """
        self.logger.debug("post", body=body)
        session = self._get_session()

        try:
            response = session.post(
                f"{self.base_url}{endpoint}", data=body, headers=headers
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            msg = f"Failed to get attestation response: {e!s}"
            raise VtpmAttestationError(msg) from e

        return response.text

    def _check_nonce_length(self, nonces: list[str]) -> None:
        """
        Validate the byte length of provided nonces.

        Each nonce must be between 10 and 74 bytes when UTF-8 encoded.

        Args:
            nonces: List of nonce strings to validate

        Raises:
            VtpmAttestationError: If any nonce is outside the valid length range
        """
        min_byte_len = 10
        max_byte_len = 74
        for nonce in nonces:
            byte_len = len(nonce.encode("utf-8"))
            self.logger.debug("nonce_length", byte_len=byte_len)
            if byte_len < min_byte_len or byte_len > max_byte_len:
                msg = f"Nonce '{nonce}' must be between {min_byte_len} bytes"
                f" and {max_byte_len} bytes"
                raise VtpmAttestationError(msg)

    def get_token(
        self,
        nonces: list[str],
        audience: str = "https://sts.google.com",
        token_type: str = "OIDC",  # noqa: S107
    ) -> str:
        """
        Request an attestation token from the service.

        Requests a token with specified nonces for replay protection,
        targeted at the specified audience. Supports both OIDC and PKI
        token types.

        Args:
            nonces: List of random nonce strings for replay protection
            audience: Intended audience for the token (default: "https://sts.google.com")
            token_type: Type of token, either "OIDC" or "PKI" (default: "OIDC")

        Returns:
            str: The attestation token in JWT format

        Raises:
            VtpmAttestationError: If token request fails for any reason
                (invalid nonces, service unavailable, etc.)

        Example:
            client = VtpmAttestation()
            token = client.get_token(
                nonces=["random_nonce"],
                audience="https://my-service.example.com",
                token_type="OIDC"
            )
        """
        self._check_nonce_length(nonces)
        if self.simulate:
            self.logger.debug("sim_token")
            return SIM_TOKEN

        headers = {"Content-Type": "application/json"}
        body = json.dumps(
            {"audience": audience, "token_type": token_type, "nonces": nonces}
        )
        token = self._post("/v1/token", body=body, headers=headers)
        self.logger.debug("token", token_type=token_type, token=token)
        return token
