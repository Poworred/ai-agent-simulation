from sqlmodel import Session, select

from app.core.time import is_after_simulation_end, next_tick
from app.domain.constants import ActionType, EventType, RunStatus
from app.models.tables import Agent, Event, Schedule, SimulationRun
from app.services.action_selector import choose_rule_action
from app.services.events import create_event


class SimulationService:
    def __init__(self, session: Session):
        self.session = session

    def tick(
        self,
        run_id: str,
        tick_count: int = 1,
        llm_mode: str = "normal",
    ) -> tuple[SimulationRun, list[Event], list[Agent]]:
        run = self.session.get(SimulationRun, run_id)
        if run is None:
            raise ValueError("Run not found")

        new_events: list[Event] = []
        updated_agents: list[Agent] = []
        for _ in range(tick_count):
            if run.status == RunStatus.COMPLETED.value:
                break
            run.current_day, run.current_minute = next_tick(
                run.current_day,
                run.current_minute,
                run.tick_minutes,
            )
            if is_after_simulation_end(run.current_day, run.current_minute):
                run.status = RunStatus.COMPLETED.value

            events, agents = self._tick_agents(run)
            new_events.extend(events)
            updated_agents.extend(agents)

        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        for event in new_events:
            self.session.refresh(event)
        for agent in updated_agents:
            self.session.refresh(agent)
        return run, new_events, updated_agents

    def _tick_agents(self, run: SimulationRun) -> tuple[list[Event], list[Agent]]:
        agents = self.session.exec(select(Agent).where(Agent.run_id == run.id)).all()
        new_events: list[Event] = []
        updated_agents: list[Agent] = []
        for agent in agents:
            schedule = self._current_schedule(run.id, agent.id, run.current_day, run.current_minute)
            action = choose_rule_action(
                agent_id=agent.id,
                current_location_id=agent.current_location_id,
                current_minute=run.current_minute,
                nearby_agent_ids=[],
                pending_interventions=[],
                current_schedule=schedule,
            )
            event = self._apply_rule_action(run, agent, action)
            new_events.append(event)
            updated_agents.append(agent)
        return new_events, updated_agents

    def _current_schedule(self, run_id: str, agent_id: str, day: int, minute: int) -> dict | None:
        schedule = self.session.exec(
            select(Schedule)
            .where(Schedule.run_id == run_id, Schedule.agent_id == agent_id, Schedule.day == day)
            .where(Schedule.start_minute <= minute, Schedule.end_minute >= minute)
            .order_by(Schedule.priority.desc())
        ).first()
        return schedule.model_dump() if schedule else None

    def _apply_rule_action(self, run: SimulationRun, agent: Agent, action) -> Event:
        if action.type == ActionType.MOVE and action.target_location_id:
            old_location_id = agent.current_location_id
            agent.current_location_id = action.target_location_id
            agent.current_action = ActionType.MOVE.value
            summary = f"{agent.name}从{old_location_id}前往{action.target_location_id}。"
            event_type = EventType.MOVE
        elif action.type == ActionType.ATTEND_CLASS:
            agent.current_action = ActionType.ATTEND_CLASS.value
            summary = f"{agent.name}按计划在教学楼上课。"
            event_type = EventType.CLASS
        elif action.type == ActionType.EAT:
            agent.current_action = ActionType.EAT.value
            agent.energy = min(100, agent.energy + 10)
            summary = f"{agent.name}在食堂吃饭，精力稍微恢复。"
            event_type = EventType.MEAL
        elif action.type == ActionType.JOIN_ACTIVITY:
            agent.current_action = ActionType.JOIN_ACTIVITY.value
            summary = f"{agent.name}来到社团招新点，观察不同社团的摊位。"
            event_type = EventType.CLUB
        else:
            agent.current_action = action.type.value
            summary = f"{agent.name}暂时停留，原因是：{action.reason}"
            event_type = EventType.SYSTEM

        self.session.add(agent)
        return create_event(
            self.session,
            run_id=run.id,
            day=run.current_day,
            minute=run.current_minute,
            event_type=event_type,
            summary=summary,
            details=action.reason,
            location_id=agent.current_location_id,
            agent_ids=[agent.id],
            state_delta={"action": action.model_dump(mode="json")},
        )
