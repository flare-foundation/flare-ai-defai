from flare_ai_core.blockchain_service import Flare


def test_generate_account() -> None:
    service = Flare("http://localhost:8545")
    address = service.generate_account()
    assert address.startswith("0x")
