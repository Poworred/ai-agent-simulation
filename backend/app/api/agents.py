from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, or_, select

from app.db.session import get_session
from app.domain.schemas import AgentDetailResponse, AgentProfileRead, AgentStateRead
from app.models.tables import Agent, Event, Memory, Relationship

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
