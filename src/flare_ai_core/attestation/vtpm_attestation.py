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
import logging
import socket
from http.client import HTTPConnection
from pathlib import Path
from types import TracebackType
from typing import override

from aiohttp import ClientSession, UnixConnector

logger = logging.getLogger(__name__)


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


class VtpmAttestation(HTTPConnection):
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
        host: str = "localhost",
        unix_socket_path: str = "/run/container_launcher/teeserver.sock",
        simulate: bool = False,
    ) -> None:
        super().__init__(host)
        self.unix_socket_path = unix_socket_path
        self.simulate = simulate

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
        self.request("POST", endpoint, body=body, headers=headers)
        res = self.getresponse()
        success_status = 200
        if res.status != success_status:
            msg = f"Failed to get attestation response: {res.status} {res.reason}"
            raise VtpmAttestationError(msg)
        return res.read()

    @staticmethod
    def _check_nonce_length(nonces: list[str]) -> None:
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
            return SIM_TOKEN

        headers = {"Content-Type": "application/json"}
        body = json.dumps(
            {"audience": audience, "token_type": token_type, "nonces": nonces}
        )
        token_bytes = self._post("/v1/token", body=body, headers=headers)
        token = token_bytes.decode()
        logger.info("%s token: %s", token_type, token)
        return token


class AsyncVtpmAttestation:
    """
    Async client for requesting attestation tokens via Unix domain socket.

    Uses aiohttp to communicate with the local attestation service
    through a Unix domain socket instead of TCP/IP.

    Args:
        host: Hostname for the HTTP connection (default: "localhost")
        unix_socket_path: Path to the attestation service Unix socket
            (default: "/run/container_launcher/teeserver.sock")

    Example:
    client = AsyncVtpmAttestation()
    try:
        token = await client.get_token(
            nonces=["random_nonce_value"],
            audience="https://sts.google.com",
            token_type="OIDC"
        )
    except VtpmAttestationError as e:
        # Handle attestation error
    """

    def __init__(
        self,
        host: str = "localhost",
        unix_socket_path: str = "/run/container_launcher/teeserver.sock",
    ) -> None:
        self.host = host
        self.unix_socket_path = unix_socket_path
        self._session: ClientSession | None = None

    async def __aenter__(self) -> "AsyncVtpmAttestation":
        """Context manager entry point."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit point."""
        await self.close()

    async def connect(self) -> None:
        """
        Establish connection to the Unix domain socket.

        Creates an aiohttp ClientSession with UnixConnector for
        communication over the Unix domain socket.

        Raises:
            VtpmAttestationError: If connection to socket fails
        """
        try:
            connector = UnixConnector(path=self.unix_socket_path)
            self._session = ClientSession(connector=connector)
        except Exception as e:
            msg = "Failed to connect to socket"
            raise VtpmAttestationError(msg) from e

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _post(self, endpoint: str, body: str, headers: dict[str, str]) -> bytes:
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
        if not self._session:
            msg = "Client not connected. Call connect() first."
            raise VtpmAttestationError(msg)

        try:
            async with self._session.post(
                f"http://{self.host}{endpoint}", data=body, headers=headers
            ) as response:
                return await response.read()
        except Exception as e:
            msg = "Request failed"
            raise VtpmAttestationError(msg) from e

    @staticmethod
    def _check_nonce_length(nonces: list[str]) -> None:
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
            if byte_len < min_byte_len or byte_len > max_byte_len:
                msg = f"Nonce '{nonce}' must be between {min_byte_len} bytes"
                f" and {max_byte_len} bytes"
                raise VtpmAttestationError(msg)

    async def get_token(
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
            async with AsyncVtpmAttestation() as client:
                token = await client.get_token(
                    nonces=["random_nonce"],
                    audience="https://my-service.example.com",
                    token_type="OIDC"
                )
        """
        self._check_nonce_length(nonces)
        headers = {"Content-Type": "application/json"}
        body = json.dumps(
            {"audience": audience, "token_type": token_type, "nonces": nonces}
        )
        token_bytes = await self._post("/v1/token", body=body, headers=headers)
        token = token_bytes.decode()
        logger.info("%s token: %s", token_type, token)
        return token
