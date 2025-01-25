"""
Client for communicating with the Confidential Space vTPM attestation service.

This module provides a client to request attestation tokens from a local Unix domain
socket endpoint. It extends HTTPConnection to handle Unix socket communication and
implements token request functionality with nonce validation.

Classes:
    VtpmAttestationError: Exception for attestation service communication errors
    VtpmAttestation: Client for requesting attestation tokens
"""

import json
import socket
from http.client import HTTPConnection
from pathlib import Path
from typing import override

import structlog

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


class Vtpm(HTTPConnection):
    """
    Client for requesting attestation tokens via Unix domain socket.

    Extends HTTPConnection to communicate with the local attestation service
    through a Unix domain socket instead of TCP/IP.

    Args:
        host: Hostname for the HTTP connection (default: "localhost")
        unix_socket_path: Path to the attestation service Unix socket
            (default: "/run/container_launcher/teeserver.sock")

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
        host: str = "http://localhost",
        unix_socket_path: str = "/run/container_launcher/teeserver.sock",
        simulate: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        super().__init__(host)
        self.unix_socket_path = unix_socket_path
        self.simulate = simulate
        self.attestation_requested: bool = False
        self.logger = logger.bind(router="vtpm")
        self.logger.debug(
            "vtpm", simulate=simulate, host=host, unix_socket_path=self.unix_socket_path
        )

    def reset(self) -> None:
        self.sock.close()
        self.logger("reset_vtpm", sock=self.sock)

    @override
    def connect(self) -> None:
        """
        Establish connection to the Unix domain socket.

        Overrides HTTPConnection.connect() to use Unix domain socket
        instead of TCP/IP socket.

        Raises:
            VtpmAttestationError: If connection to socket fails
        """
        if self.simulate:
            return
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.unix_socket_path)
        self.logger.debug("connect_socket", unix_socket_path=self.unix_socket_path)

    def _post(self, endpoint: str, body: str, headers: dict[str, str]) -> bytes:
        """
        Send POST request to attestation service endpoint.

        Args:
            endpoint: API endpoint path
            body: JSON request body
            headers: HTTP request headers

        Returns:
            bytes: Raw response from the attestation service

        Raises:
            VtpmAttestationError: If request fails or response status is not 200
        """
        self.logger.debug("post", body=body)
        self.request("POST", endpoint, body=body, headers=headers)
        res = self.getresponse()
        success_status = 200
        if res.status != success_status:
            msg = f"Failed to get attestation response: {res.status} {res.reason}"
            raise VtpmAttestationError(msg)
        return res.read()

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
            self.logger.debug("sim_token", token=SIM_TOKEN)
            return SIM_TOKEN

        headers = {"Content-Type": "application/json"}
        body = json.dumps(
            {"audience": audience, "token_type": token_type, "nonces": nonces}
        )
        token_bytes = self._post("/v1/token", body=body, headers=headers)
        token = token_bytes.decode()
        self.logger.debug("token", token_type=token_type, token=token)
        return token
