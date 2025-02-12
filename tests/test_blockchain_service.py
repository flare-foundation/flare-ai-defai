from flare_ai_defai.blockchain import FlareProvider


def test_generate_account() -> None:
    service = FlareProvider("http://localhost:8545")
    address = service.generate_account()
    assert address.startswith("0x")
