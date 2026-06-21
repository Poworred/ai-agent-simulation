from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.domain.schemas import CreateRunRequest, RunStateResponse
from app.models.tables import Agent, Event, Location, SimulationRun
from app.seed.seed_service import create_seed_run

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=RunStateResponse, status_code=status.HTTP_201_CREATED)
def create_run(
    payload: CreateRunRequest,
    session: Session = Depends(get_session),
) -> RunStateResponse:
    run = create_seed_run(session, payload.name)
    return _build_run_state(session, run.id)


@router.get("/{run_id}/state", response_model=RunStateResponse)
def get_run_state(run_id: str, session: Session = Depends(get_session)) -> RunStateResponse:
    return _build_run_state(session, run_id)


def _build_run_state(session: Session, run_id: str) -> RunStateResponse:
    run = session.get(SimulationRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    locations = session.exec(select(Location).where(Location.run_id == run_id)).all()
    agents = session.exec(select(Agent).where(Agent.run_id == run_id)).all()
    events = session.exec(
        select(Event).where(Event.run_id == run_id).order_by(Event.created_at.desc()).limit(50)
    ).all()
    return RunStateResponse(
        run=run,
        locations=locations,
        agents=agents,
        recent_events=list(reversed(events)),
    )
