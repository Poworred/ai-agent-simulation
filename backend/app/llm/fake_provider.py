from typing import Any

from app.llm.base import LLMProvider
from app.llm.schemas import DialogueResult, InterventionDecision, ReflectionResult


class FakeLLMProvider(LLMProvider):
    def generate_dialogue(self, context: dict[str, Any]) -> DialogueResult:
        speaker = context.get("speaker", "王一诺")
        target = context.get("target", "林见川")
        return DialogueResult.model_validate(
            {
                "dialogue": [
                    {"speaker": speaker, "text": "我对这里还不太熟，可以问你一个问题吗？"},
                    {"speaker": target, "text": "当然可以，我们可以一起过去。"},
                ],
                "relationship_delta": {"affinity": 1, "familiarity": 1, "trust": 1},
                "memory_writes": [f"{speaker}和{target}进行了一次友好的校园交流。"],
                "event_summary": f"{speaker}和{target}在校园里交流了一会儿。",
            }
        )

    def reflect_day(self, context: dict[str, Any]) -> ReflectionResult:
        agent_name = context.get("agent_name", "这名 Agent")
        return ReflectionResult(
            reflection=f"{agent_name}回顾了今天的课程、吃饭和社交经历，决定明天继续适应校园生活。",
            goal_updates=["明天继续按计划上课", "留意可以认识同学的机会"],
            important_memories=[f"{agent_name}完成了一天的校园生活。"],
            mood_delta="slightly_positive",
            adaptation_delta=1,
        )

    def decide_intervention(self, context: dict[str, Any]) -> InterventionDecision:
        content = context.get("content", "")
        if "社团" in content:
            return InterventionDecision(
                decision="accepted",
                reason="建议与加入社团的长期目标一致。",
                new_immediate_goal="去社团招新点看看",
            )
        return InterventionDecision(decision="considered", reason="Agent 会把这条建议作为参考。")
