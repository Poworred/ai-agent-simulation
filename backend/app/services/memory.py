from sqlmodel import Session, select

from app.models.tables import Memory


def score_memory(
    content: str,
    importance: int,
    created_day: int,
    created_minute: int,
    current_day: int,
    current_minute: int,
    query_terms: list[str],
) -> float:
    age_minutes = max(0, (current_day - created_day) * 24 * 60 + (current_minute - created_minute))
    recency_score = max(0.0, 5.0 - age_minutes / 180.0)
    importance_score = float(importance)
    relevance_score = sum(2.0 for term in query_terms if term and term in content)
    return recency_score + importance_score + relevance_score


class MemoryService:
    def __init__(self, session: Session):
        self.session = session

    def retrieve(
        self,
        *,
        run_id: str,
        agent_id: str,
        current_day: int,
        current_minute: int,
        query_terms: list[str],
        limit: int = 8,
    ) -> list[Memory]:
        memories = self.session.exec(
            select(Memory).where(Memory.run_id == run_id, Memory.agent_id == agent_id)
        ).all()
        ranked = sorted(
            memories,
            key=lambda memory: score_memory(
                memory.content,
                memory.importance,
                memory.created_day,
                memory.created_minute,
                current_day,
                current_minute,
                query_terms,
            ),
            reverse=True,
        )
        return ranked[:limit]
