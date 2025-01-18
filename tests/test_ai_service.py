from flare_ai_core.ai_service import Gemini


async def test_generate() -> None:
    service = Gemini("test_key", "gemini-1.5-flash")
    response = service.generate("Test prompt")
    assert response is not None
