from sqlmodel import Session

from app.core.ids import new_id
from app.domain.constants import (
    DEFAULT_START_DAY,
    DEFAULT_START_MINUTE,
    DEFAULT_TICK_MINUTES,
    EventType,
    RunStatus,
)
from app.models.tables import Agent, Event, Location, Path, Schedule, SimulationRun
from app.seed.seed_data import AGENTS, LOCATIONS, PATHS


def create_seed_run(session: Session, name: str) -> SimulationRun:
    run = SimulationRun(
        id=new_id("run"),
        name=name,
        current_day=DEFAULT_START_DAY,
        current_minute=DEFAULT_START_MINUTE,
        tick_minutes=DEFAULT_TICK_MINUTES,
        status=RunStatus.PAUSED.value,
    )
    session.add(run)
    session.flush()

    for loc in LOCATIONS:
        session.add(Location(run_id=run.id, open_minutes={}, **loc))

    for from_id, to_id, distance in PATHS:
        session.add(
            Path(
                id=new_id("path"),
                run_id=run.id,
                from_location_id=from_id,
                to_location_id=to_id,
                distance_minutes=distance,
            )
        )
        session.add(
            Path(
                id=new_id("path"),
                run_id=run.id,
                from_location_id=to_id,
                to_location_id=from_id,
                distance_minutes=distance,
            )
        )

    for agent in AGENTS:
        session.add(
            Agent(
                run_id=run.id,
                current_location_id="dorm",
                current_goal="适应大学第一周生活",
                **agent,
            )
        )

    _seed_schedules(session, run.id)

    session.add(
        Event(
            id=new_id("event"),
            run_id=run.id,
            day=run.current_day,
            minute=run.current_minute,
            event_type=EventType.SYSTEM.value,
            summary="AI 南大的一周模拟开始了，第一批新生正在宿舍区整理自己的计划。",
            details="系统初始化了地点、路径、角色、课表和初始事件。",
        )
    )
    session.commit()
    session.refresh(run)
    return run


def _seed_schedules(session: Session, run_id: str) -> None:
    class_agents = [
        "agent_wang_yinuo",
        "agent_chen_nian",
        "agent_zhou_lan",
        "agent_lin_jianchuan",
        "agent_li_mengyao",
    ]
    for day in range(1, 8):
        for agent_id in class_agents:
            session.add(
                Schedule(
                    id=new_id("schedule"),
                    run_id=run_id,
                    agent_id=agent_id,
                    day=day,
                    start_minute=8 * 60 + 30,
                    end_minute=10 * 60,
                    type="class",
                    title="上午课程",
                    location_id="teaching_building",
                    priority=10,
                )
            )
            session.add(
                Schedule(
                    id=new_id("schedule"),
                    run_id=run_id,
                    agent_id=agent_id,
                    day=day,
                    start_minute=12 * 60,
                    end_minute=13 * 60,
                    type="meal",
                    title="午饭",
                    location_id="canteen",
                    priority=8,
                )
            )
            session.add(
                Schedule(
                    id=new_id("schedule"),
                    run_id=run_id,
                    agent_id=agent_id,
                    day=day,
                    start_minute=22 * 60 + 30,
                    end_minute=23 * 60,
                    type="rest",
                    title="晚间反思",
                    location_id="dorm",
                    priority=9,
                )
            )
        if day in {1, 2, 3}:
            for agent_id in class_agents:
                session.add(
                    Schedule(
                        id=new_id("schedule"),
                        run_id=run_id,
                        agent_id=agent_id,
                        day=day,
                        start_minute=16 * 60,
                        end_minute=18 * 60,
                        type="club",
                        title="社团招新",
                        location_id="club_fair",
                        priority=6,
                    )
                )
