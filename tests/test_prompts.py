import pytest

from flare_ai_defai.prompts import PromptLibrary


def test_prompt_library_initialization() -> None:
    library = PromptLibrary()
    assert len(library.prompts) > 0
    assert "semantic_router" in library.prompts


def test_prompt_formatting() -> None:
    library = PromptLibrary()
    prompt = library.get_prompt("semantic_router")
    formatted = prompt.format(user_input="test message")
    assert "test message" in formatted


def test_prompt_missing_inputs() -> None:
    library = PromptLibrary()
    prompt = library.get_prompt("generate_account")
    with pytest.raises(ValueError, match="Missing required inputs: address"):
        prompt.format(wrong_input="test")
