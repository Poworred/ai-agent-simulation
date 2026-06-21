from sqlmodel import Session

from app.core.ids import new_id
from app.domain.constants import EventType
from app.models.tables import Event


def create_event(
    session: Session,
    *,
    run_id: str,
    day: int,
    minute: int,
    event_type: EventType | str,
    summary: str,
    details: str = "",
    location_id: str | None = None,
    agent_ids: list[str] | None = None,
    llm_generated: bool = False,
    state_delta: dict | None = None,
) -> Event:
    event_value = event_type.value if isinstance(event_type, EventType) else str(event_type)
    event = Event(
        id=new_id("event"),
        run_id=run_id,
        day=day,
        minute=minute,
        event_type=event_value,
        location_id=location_id,
        agent_ids=agent_ids or [],
        summary=summary,
        details=details,
        llm_generated=llm_generated,
        state_delta=state_delta or {},
    )
    session.add(event)
    return event
