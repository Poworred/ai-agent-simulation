from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.db.session import get_session
from app.domain.schemas import EventRead
from app.models.tables import Event

router = APIRouter(prefix="/api/runs", tags=["events"])


@router.get("/{run_id}/events", response_model=list[EventRead])
def list_events(
    run_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    agent_id: str | None = None,
    session: Session = Depends(get_session),
) -> list[EventRead]:
    events = session.exec(
        select(Event).where(Event.run_id == run_id).order_by(Event.created_at.desc()).limit(limit)
    ).all()
    if agent_id:
        events = [event for event in events if agent_id in event.agent_ids]
    return list(reversed(events))
