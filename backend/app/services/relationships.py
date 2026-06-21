from sqlmodel import Session, or_, select

from app.core.ids import new_id
from app.models.tables import Relationship


class RelationshipService:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create(self, run_id: str, agent_a_id: str, agent_b_id: str) -> Relationship:
        relationship = self.session.exec(
            select(Relationship).where(
                Relationship.run_id == run_id,
                or_(
                    (Relationship.agent_a_id == agent_a_id) & (Relationship.agent_b_id == agent_b_id),
                    (Relationship.agent_a_id == agent_b_id) & (Relationship.agent_b_id == agent_a_id),
                ),
            )
        ).first()
        if relationship:
            return relationship
        relationship = Relationship(
            id=new_id("rel"),
            run_id=run_id,
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
        )
        self.session.add(relationship)
        return relationship

    def apply_delta(
        self,
        relationship: Relationship,
        *,
        affinity: int = 0,
        familiarity: int = 0,
        trust: int = 0,
        tag: str | None = None,
        event_id: str | None = None,
    ) -> Relationship:
        relationship.affinity += affinity
        relationship.familiarity += familiarity
        relationship.trust += trust
        if tag and tag not in relationship.relationship_tags:
            relationship.relationship_tags = [*relationship.relationship_tags, tag]
        relationship.last_interaction_event_id = event_id or relationship.last_interaction_event_id
        self.session.add(relationship)
        return relationship
