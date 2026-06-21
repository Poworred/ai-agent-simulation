from pydantic import ValidationError

from app.llm.schemas import DialogueResult, ReflectionResult
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
