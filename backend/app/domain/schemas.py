from pydantic import BaseModel, ConfigDict


class CreateRunRequest(BaseModel):
    name: str = "AI 南大默认模拟"


class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    current_day: int
    current_minute: int
    tick_minutes: int
    status: str


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    description: str
    x: int
    y: int
    available_actions: list[str]
    event_tags: list[str]


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    role: str
    major: str
    personality: str
    interests: list[str]
    long_term_goals: list[str]
    social_style: str
    current_location_id: str
    current_goal: str
    current_action: str
    mood: str
    energy: int
    stress: int
    adaptation_score: int


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    day: int
    minute: int
    event_type: str
    location_id: str | None
    agent_ids: list[str]
    summary: str
    details: str
    llm_generated: bool


class RunStateResponse(BaseModel):
    run: RunRead
    locations: list[LocationRead]
    agents: list[AgentRead]
    recent_events: list[EventRead]
