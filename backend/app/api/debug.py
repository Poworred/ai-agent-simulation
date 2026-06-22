from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.tables import Agent, LLMCall, Memory

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/agents/{agent_id}/memories")
def debug_agent_memories(agent_id: str, session: Session = Depends(get_session)) -> dict:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    memories = session.exec(select(Memory).where(Memory.agent_id == agent_id)).all()
    return {"agent_id": agent_id, "memories": [memory.model_dump(mode="json") for memory in memories]}


@router.get("/runs/{run_id}/llm-calls")
def debug_llm_calls(run_id: str, session: Session = Depends(get_session)) -> dict:
    calls = session.exec(select(LLMCall).where(LLMCall.run_id == run_id)).all()
    return {"run_id": run_id, "llm_calls": [call.model_dump(mode="json") for call in calls]}
