from pydantic import BaseModel, Field


class DialogueLine(BaseModel):
    speaker: str
    text: str


class RelationshipDelta(BaseModel):
    affinity: int = 0
    familiarity: int = 0
    trust: int = 0


class DialogueResult(BaseModel):
    dialogue: list[DialogueLine]
    relationship_delta: RelationshipDelta
    memory_writes: list[str]
    event_summary: str


class ReflectionResult(BaseModel):
    reflection: str
    goal_updates: list[str] = Field(default_factory=list)
    important_memories: list[str] = Field(default_factory=list)
    mood_delta: str = "neutral"
    adaptation_delta: int = 0


class InterventionDecision(BaseModel):
    decision: str
    reason: str
    new_immediate_goal: str | None = None


class ComplexEventDecision(BaseModel):
    chosen_action: str
    target_location: str | None = None
    reason: str


class PolishedEvent(BaseModel):
    summary: str
    details: str = ""
