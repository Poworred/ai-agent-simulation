from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, or_, select

from app.core.ids import new_id
from app.core.time import format_sim_time
from app.db.session import get_session
from app.domain.constants import EventType
from app.domain.schemas import (
    AgentDetailResponse,
    AgentProfileRead,
    AgentStateRead,
    CreateInterventionRequest,
    InterventionResponse,
)
from app.models.tables import Agent, Event, Memory, Relationship, SimulationRun, UserIntervention
from app.services.events import create_event
from app.services.safety import is_safe_user_intervention

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/{agent_id}", response_model=AgentDetailResponse)
def get_agent(agent_id: str, session: Session = Depends(get_session)) -> AgentDetailResponse:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    recent_events = session.exec(
        select(Event).where(Event.run_id == agent.run_id).order_by(Event.created_at.desc()).limit(50)
    ).all()
    filtered_events = [event for event in recent_events if agent_id in event.agent_ids][:10]

    important_memories = session.exec(
        select(Memory).where(Memory.agent_id == agent_id).order_by(Memory.importance.desc()).limit(10)
    ).all()

    relationships = session.exec(
        select(Relationship).where(
            or_(Relationship.agent_a_id == agent_id, Relationship.agent_b_id == agent_id)
        )
    ).all()

    return AgentDetailResponse(
        profile=AgentProfileRead.model_validate(agent),
        state=AgentStateRead.model_validate(agent),
        recent_events=list(reversed(filtered_events)),
        important_memories=important_memories,
        relationships=relationships,
    )


@router.post(
    "/{agent_id}/interventions",
    response_model=InterventionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_intervention(
    agent_id: str,
    payload: CreateInterventionRequest,
    session: Session = Depends(get_session),
) -> InterventionResponse:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    run = session.get(SimulationRun, agent.run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if not is_safe_user_intervention(payload.content):
        event = create_event(
            session,
            run_id=run.id,
            day=run.current_day,
            minute=run.current_minute,
            event_type=EventType.SYSTEM,
            summary="系统拒绝了一条不适合进入模拟的用户干预。",
            details="用户干预未写入 Agent 记忆。",
            agent_ids=[agent.id],
        )
        session.commit()
        return InterventionResponse(intervention_id=event.id, status="rejected")

    intervention = UserIntervention(
        id=new_id("int"),
        run_id=run.id,
        agent_id=agent.id,
        content=payload.content,
        created_day=run.current_day,
        created_minute=run.current_minute,
    )
    session.add(intervention)
    session.add(
        Memory(
            id=new_id("mem"),
            run_id=run.id,
            agent_id=agent.id,
            memory_type="intervention",
            content=f"用户在{format_sim_time(run.current_day, run.current_minute)}建议：{payload.content}",
            importance=5,
            tags=["intervention"],
            source="user",
            created_day=run.current_day,
            created_minute=run.current_minute,
        )
    )
    create_event(
        session,
        run_id=run.id,
        day=run.current_day,
        minute=run.current_minute,
        event_type=EventType.INTERVENTION,
        summary=f"用户给{agent.name}留下建议：{payload.content}",
        agent_ids=[agent.id],
    )
    session.commit()
    return InterventionResponse(intervention_id=intervention.id, status=intervention.status)
