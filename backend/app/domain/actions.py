from pydantic import BaseModel

from app.domain.constants import ActionType


class ProposedAction(BaseModel):
    type: ActionType
    agent_id: str
    reason: str
    target_location_id: str | None = None
    target_agent_id: str | None = None
    topic: str | None = None
