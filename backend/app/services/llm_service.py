from app.core.config import get_settings
from app.llm.anthropic_provider import AnthropicLLMProvider
from app.llm.base import LLMProvider
from app.llm.fake_provider import FakeLLMProvider


def get_llm_provider(llm_mode: str = "normal") -> LLMProvider:
    settings = get_settings()
    if llm_mode == "offline" or settings.llm_provider == "fake":
        return FakeLLMProvider()
    if settings.llm_provider == "anthropic":
        return AnthropicLLMProvider(settings)
    return FakeLLMProvider()
