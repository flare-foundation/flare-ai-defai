import pytest

from flare_ai_core.ai_service import Gemini
from flare_ai_core.attestation_service import Vtpm
from flare_ai_core.blockchain_service import Flare


@pytest.fixture
def ai_service() -> Gemini:
    return Gemini("some_api_key", "gemini-1.5-flash")


@pytest.fixture
def blockchain_service() -> Flare:
    return Flare("http://localhost:8545")


@pytest.fixture
def attestation_service() -> Vtpm:
    return Vtpm(simulate=True)
