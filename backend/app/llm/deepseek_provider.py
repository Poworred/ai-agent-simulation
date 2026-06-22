from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.prompts import SYSTEM_PROMPT, dialogue_prompt, intervention_prompt, reflection_prompt
from app.llm.schemas import DialogueResult, InterventionDecision, ReflectionResult

T = TypeVar("T", bound=BaseModel)


class DeepSeekLLMProvider(LLMProvider):
    def __init__(self, settings: Settings):
        if not settings.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required when LLM_PROVIDER=deepseek")
        self.settings = settings
        self.client = httpx.Client(
            base_url=settings.deepseek_base_url,
            headers={"Authorization": f"Bearer {settings.deepseek_api_key}"},
            timeout=60.0,
        )

    def generate_dialogue(self, context: dict[str, Any]) -> DialogueResult:
        return self._parse(DialogueResult, dialogue_prompt(context))

    def reflect_day(self, context: dict[str, Any]) -> ReflectionResult:
        return self._parse(ReflectionResult, reflection_prompt(context))

    def decide_intervention(self, context: dict[str, Any]) -> InterventionDecision:
        return self._parse(InterventionDecision, intervention_prompt(context))

    def _parse(self, model_type: type[T], prompt: str) -> T:
        schema = model_type.model_json_schema()
        response = self.client.post(
            "/chat/completions",
            json={
                "model": self.settings.deepseek_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"{SYSTEM_PROMPT}\n"
                            "Return JSON only. Do not wrap it in Markdown.\n"
                            f"JSON schema: {schema}"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "thinking": {"type": "disabled"},
                "max_tokens": 1200,
                "temperature": 0.4,
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return model_type.model_validate_json(content)
