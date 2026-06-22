from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel

from app.domain.constants import DEFAULT_TICK_MINUTES, RunStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SimulationRun(SQLModel, table=True):
    __tablename__ = "simulation_runs"

    id: str = Field(primary_key=True)
    name: str
    current_day: int
    current_minute: int
    tick_minutes: int = DEFAULT_TICK_MINUTES
    status: str = RunStatus.PAUSED.value
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Location(SQLModel, table=True):
    __tablename__ = "locations"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    name: str
    type: str
    description: str
    x: int
    y: int
    open_minutes: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    available_actions: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    event_tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class Path(SQLModel, table=True):
    __tablename__ = "paths"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    from_location_id: str = Field(index=True)
    to_location_id: str = Field(index=True)
    distance_minutes: int


class Agent(SQLModel, table=True):
    __tablename__ = "agents"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    name: str
    role: str
    major: str
    personality: str
    interests: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    long_term_goals: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    social_style: str
    current_location_id: str = Field(index=True)
    current_goal: str
    current_action: str = "idle"
    mood: str = "neutral"
    energy: int = 80
    stress: int = 20
    adaptation_score: int = 0
    last_reflection_at: str | None = None


class Schedule(SQLModel, table=True):
    __tablename__ = "schedules"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_id: str = Field(index=True)
    day: int
    start_minute: int
    end_minute: int
    type: str
    title: str
    location_id: str
    priority: int = 0


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    day: int
    minute: int
    event_type: str
    location_id: str | None = None
    agent_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    summary: str
    details: str = ""
    visibility: str = "public"
    llm_generated: bool = False
    state_delta: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now)


class Memory(SQLModel, table=True):
    __tablename__ = "memories"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_id: str = Field(index=True)
    memory_type: str
    content: str
    importance: int = 1
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    source: str = "system"
    related_agent_id: str | None = None
    related_event_id: str | None = None
    created_day: int
    created_minute: int
    last_accessed_at: datetime | None = None
    expires_at: datetime | None = None


class Relationship(SQLModel, table=True):
    __tablename__ = "relationships"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_a_id: str = Field(index=True)
    agent_b_id: str = Field(index=True)
    affinity: int = 0
    familiarity: int = 0
    trust: int = 0
    relationship_tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    last_interaction_event_id: str | None = None


class UserIntervention(SQLModel, table=True):
    __tablename__ = "user_interventions"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_id: str = Field(index=True)
    content: str
    status: str = "pending"
    created_day: int
    created_minute: int
    handled_event_id: str | None = None


class LLMCall(SQLModel, table=True):
    __tablename__ = "llm_calls"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_id: str | None = Field(default=None, index=True)
    function_name: str
    prompt_version: str
    input_summary: str
    output_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    status: str
    latency_ms: int | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
