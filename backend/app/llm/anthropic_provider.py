from typing import Any, TypeVar

import anthropic
from pydantic import BaseModel

from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.prompts import SYSTEM_PROMPT, dialogue_prompt, intervention_prompt, reflection_prompt
from app.llm.schemas import DialogueResult, InterventionDecision, ReflectionResult

T = TypeVar("T", bound=BaseModel)


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate_dialogue(self, context: dict[str, Any]) -> DialogueResult:
        return self._parse(DialogueResult, dialogue_prompt(context))

    def reflect_day(self, context: dict[str, Any]) -> ReflectionResult:
        return self._parse(ReflectionResult, reflection_prompt(context))

    def decide_intervention(self, context: dict[str, Any]) -> InterventionDecision:
        return self._parse(InterventionDecision, intervention_prompt(context))

    def _parse(self, model_type: type[T], prompt: str) -> T:
        response = self.client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=4000,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": model_type.model_json_schema(),
                }
            },
        )
        text = next(block.text for block in response.content if block.type == "text")
        return model_type.model_validate_json(text)
