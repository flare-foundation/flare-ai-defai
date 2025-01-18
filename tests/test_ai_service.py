from flare_ai_core.ai import GeminiProvider


async def test_generate() -> None:
    service = GeminiProvider("test_key", "gemini-1.5-flash")
    response = service.generate("Test prompt")
    assert response is not None
