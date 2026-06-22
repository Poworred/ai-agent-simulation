from abc import ABC, abstractmethod
from typing import Any

from app.llm.schemas import DialogueResult, InterventionDecision, ReflectionResult


class LLMProvider(ABC):
    @abstractmethod
    def generate_dialogue(self, context: dict[str, Any]) -> DialogueResult:
        raise NotImplementedError

    @abstractmethod
    def reflect_day(self, context: dict[str, Any]) -> ReflectionResult:
        raise NotImplementedError

    @abstractmethod
    def decide_intervention(self, context: dict[str, Any]) -> InterventionDecision:
        raise NotImplementedError
