import pytest

from flare_ai_defai.ai import GeminiProvider
from flare_ai_defai.attestation import Vtpm
from flare_ai_defai.blockchain import FlareProvider


@pytest.fixture
def ai_service() -> GeminiProvider:
    return GeminiProvider("some_api_key", "gemini-1.5-flash")


@pytest.fixture
def blockchain_service() -> FlareProvider:
    return FlareProvider("http://localhost:8545")


@pytest.fixture
def attestation_service() -> Vtpm:
    return Vtpm(simulate=True)
