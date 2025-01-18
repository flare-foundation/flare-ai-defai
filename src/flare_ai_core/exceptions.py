class FlareAiError(Exception):
    """Base exception for Flare AI errors"""


class TransactionError(FlareAiError):
    """Raised when transaction processing fails"""


class AttestationError(FlareAiError):
    """Raised when attestation processing fails"""


class RoutingError(FlareAiError):
    """Raised when semantic routing fails"""
