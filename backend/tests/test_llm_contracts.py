import os

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.llm.deepseek_provider import DeepSeekLLMProvider
from app.llm.fake_provider import FakeLLMProvider
from app.llm.schemas import DialogueResult, ReflectionResult
import app.services.llm_service as llm_service
from app.services.llm_service import get_llm_provider


def test_dialogue_result_schema_accepts_valid_output():
    result = DialogueResult.model_validate(
        {
            "dialogue": [
                {"speaker": "王一诺", "text": "请问教学楼怎么走？"},
                {"speaker": "林见川", "text": "我也去那里，一起吧。"},
            ],
            "relationship_delta": {"affinity": 1, "familiarity": 1, "trust": 1},
            "memory_writes": ["王一诺记住林见川帮他找路。"],
            "event_summary": "王一诺向林见川问路，两人因此认识。",
        }
    )

    assert result.event_summary.startswith("王一诺")


def test_reflection_result_schema_rejects_missing_reflection():
    try:
        ReflectionResult.model_validate({"goal_updates": []})
    except ValidationError:
        return
    raise AssertionError("Expected validation error")


def test_offline_llm_provider_returns_valid_fake_reflection():
    provider = get_llm_provider("offline")

    reflection = provider.reflect_day({"agent_name": "王一诺"})

    assert reflection.reflection.startswith("王一诺")
    assert reflection.adaptation_delta >= 0


def test_deepseek_provider_posts_json_completion(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"reflection":"王一诺认真回顾了今天。",'
                                '"goal_updates":["明天继续上课"],'
                                '"important_memories":["完成一次反思"],'
                                '"mood_delta":"neutral",'
                                '"adaptation_delta":1}'
                            )
                        }
                    }
                ]
            }

    class FakeClient:
        def __init__(self, **kwargs):
            captured["client_kwargs"] = kwargs

        def post(self, path, json):
            captured["path"] = path
            captured["payload"] = json
            return FakeResponse()

    monkeypatch.setattr("app.llm.deepseek_provider.httpx.Client", FakeClient)
    provider = DeepSeekLLMProvider(
        Settings(deepseek_api_key="test-key", deepseek_model="deepseek-v4-flash")
    )

    result = provider.reflect_day({"agent_name": "王一诺"})

    assert result.adaptation_delta == 1
    assert captured["client_kwargs"]["base_url"] == "https://api.deepseek.com"
    assert captured["client_kwargs"]["headers"]["Authorization"] == "Bearer test-key"
    assert captured["path"] == "/chat/completions"
    assert captured["payload"]["model"] == "deepseek-v4-flash"
    assert captured["payload"]["response_format"] == {"type": "json_object"}
    assert captured["payload"]["thinking"] == {"type": "disabled"}
    assert captured["payload"]["max_tokens"] == 1200
    assert "JSON" in captured["payload"]["messages"][0]["content"]
    assert "reflection" in captured["payload"]["messages"][0]["content"]


def test_llm_provider_selects_deepseek_when_configured(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "get_settings",
        lambda: Settings(llm_provider="deepseek", deepseek_api_key="test-key"),
    )

    provider = get_llm_provider("normal")

    assert isinstance(provider, DeepSeekLLMProvider)


def test_offline_mode_overrides_deepseek_config(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "get_settings",
        lambda: Settings(llm_provider="deepseek", deepseek_api_key="test-key"),
    )

    provider = get_llm_provider("offline")

    assert isinstance(provider, FakeLLMProvider)


@pytest.mark.llm
def test_deepseek_provider_real_reflection_smoke():
    if os.getenv("RUN_LLM_TESTS") != "1" or not os.getenv("DEEPSEEK_API_KEY"):
        pytest.skip("Set RUN_LLM_TESTS=1 and DEEPSEEK_API_KEY to run this test.")

    provider = DeepSeekLLMProvider(Settings())

    result = provider.reflect_day({"agent_name": "王一诺", "current_goal": "适应大学生活"})

    assert result.reflection
