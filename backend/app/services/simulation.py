from sqlmodel import Session, select

from app.core.ids import new_id
from app.core.time import is_after_simulation_end, next_tick
from app.domain.constants import ActionType, EventType, RunStatus
from app.models.tables import Agent, Event, LLMCall, Location, Memory, Path, Schedule, SimulationRun, UserIntervention
from app.seed.event_templates import CLASS_EVENTS, CLUB_EVENTS, LOST_ITEM_EVENTS, MEAL_EVENTS
from app.services.action_selector import choose_rule_action
from app.services.events import create_event
from app.services.game_master import GameMaster
from app.services.llm_service import get_llm_provider
from app.services.relationships import RelationshipService


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

            events, agents = self._tick_agents(run, llm_mode)
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

    def _tick_agents(self, run: SimulationRun, llm_mode: str) -> tuple[list[Event], list[Agent]]:
        agents = self.session.exec(select(Agent).where(Agent.run_id == run.id)).all()
        game_master = self._build_game_master(run.id)
        new_events: list[Event] = []
        updated_agents: list[Agent] = []
        for agent in agents:
            schedule = self._current_schedule(run.id, agent.id, run.current_day, run.current_minute)
            pending_intervention_rows = self._pending_intervention_rows(run.id, agent.id)
            pending_interventions = [intervention.content for intervention in pending_intervention_rows]
            self._decide_pending_interventions(run, agent, pending_intervention_rows, llm_mode)
            nearby_agent_ids = [
                other.id
                for other in agents
                if other.id != agent.id and other.current_location_id == agent.current_location_id
            ]
            action = choose_rule_action(
                agent_id=agent.id,
                current_location_id=agent.current_location_id,
                current_minute=run.current_minute,
                nearby_agent_ids=nearby_agent_ids,
                pending_interventions=pending_interventions,
                current_schedule=schedule,
            )
            event = self._apply_rule_action(run, agent, action, game_master, llm_mode)
            self._write_event_memory(run, event)
            new_events.append(event)
            reflection_event = self._maybe_reflect(run, agent, llm_mode)
            if reflection_event:
                new_events.append(reflection_event)
            lost_item_event = self._maybe_lost_item_event(run, agent)
            if lost_item_event:
                self._write_event_memory(run, lost_item_event, importance=4)
                new_events.append(lost_item_event)
            updated_agents.append(agent)
        return new_events, updated_agents

    def _maybe_reflect(self, run: SimulationRun, agent: Agent, llm_mode: str) -> Event | None:
        reflection_key = f"day-{run.current_day}"
        if run.current_minute < 22 * 60 + 30 or agent.last_reflection_at == reflection_key:
            return None
        provider = get_llm_provider(llm_mode)
        result = provider.reflect_day({"agent_name": agent.name, "current_goal": agent.current_goal})
        self._log_llm_call(
            run,
            agent.id,
            "reflect_day",
            {"agent_name": agent.name, "current_goal": agent.current_goal},
            result.model_dump(mode="json"),
        )
        agent.last_reflection_at = reflection_key
        agent.adaptation_score += result.adaptation_delta
        event = create_event(
            self.session,
            run_id=run.id,
            day=run.current_day,
            minute=run.current_minute,
            event_type=EventType.REFLECTION,
            summary=f"{agent.name}完成今日反思：{result.reflection}",
            details="\n".join(result.goal_updates),
            location_id=agent.current_location_id,
            agent_ids=[agent.id],
            llm_generated=llm_mode != "offline",
        )
        self._write_event_memory(run, event, importance=4)
        return event

    def _maybe_lost_item_event(self, run: SimulationRun, agent: Agent) -> Event | None:
        if not (
            run.current_day == 2
            and run.current_minute == 15 * 60
            and agent.current_location_id in {"library", "canteen"}
        ):
            return None
        return create_event(
            self.session,
            run_id=run.id,
            day=run.current_day,
            minute=run.current_minute,
            event_type=EventType.LOST_ITEM,
            summary=self._template_summary(LOST_ITEM_EVENTS, agent, run),
            details="这条事件会进入记忆流，用于后续失物招领行为。",
            location_id=agent.current_location_id,
            agent_ids=[agent.id],
        )

    def _template_summary(self, templates: list[str], agent: Agent, run: SimulationRun) -> str:
        index_seed = sum(ord(char) for char in agent.id) + run.current_day + run.current_minute
        template = templates[index_seed % len(templates)]
        return template.format(agent=agent.name)

    def _build_game_master(self, run_id: str) -> GameMaster:
        locations = self.session.exec(select(Location).where(Location.run_id == run_id)).all()
        paths = self.session.exec(select(Path).where(Path.run_id == run_id)).all()
        location_ids = {location.id for location in locations}
        path_map: dict[str, set[str]] = {}
        for path in paths:
            path_map.setdefault(path.from_location_id, set()).add(path.to_location_id)
        return GameMaster(paths=path_map, locations=location_ids)

    def _write_event_memory(self, run: SimulationRun, event: Event, importance: int = 2) -> None:
        if event.event_type == EventType.SYSTEM.value:
            return
        for agent_id in event.agent_ids:
            self.session.add(
                Memory(
                    id=new_id("mem"),
                    run_id=run.id,
                    agent_id=agent_id,
                    memory_type="short_term",
                    content=event.summary,
                    importance=importance,
                    tags=[event.event_type],
                    source="event",
                    related_event_id=event.id,
                    created_day=run.current_day,
                    created_minute=run.current_minute,
                )
            )

    def _log_llm_call(
        self,
        run: SimulationRun,
        agent_id: str | None,
        function_name: str,
        input_summary: dict,
        output_json: dict,
        status: str = "success",
        error_message: str | None = None,
    ) -> None:
        self.session.add(
            LLMCall(
                id=new_id("llm"),
                run_id=run.id,
                agent_id=agent_id,
                function_name=function_name,
                prompt_version="v1",
                input_summary=str(input_summary)[:500],
                output_json=output_json,
                status=status,
                latency_ms=0,
                error_message=error_message,
            )
        )

    def _pending_intervention_rows(self, run_id: str, agent_id: str) -> list[UserIntervention]:
        return self.session.exec(
            select(UserIntervention).where(
                UserIntervention.run_id == run_id,
                UserIntervention.agent_id == agent_id,
                UserIntervention.status == "pending",
            )
        ).all()

    def _decide_pending_interventions(
        self,
        run: SimulationRun,
        agent: Agent,
        interventions: list[UserIntervention],
        llm_mode: str,
    ) -> None:
        if not interventions:
            return
        provider = get_llm_provider(llm_mode)
        for intervention in interventions:
            decision = provider.decide_intervention(
                {
                    "agent_name": agent.name,
                    "current_goal": agent.current_goal,
                    "content": intervention.content,
                }
            )
            self._log_llm_call(
                run,
                agent.id,
                "decide_intervention",
                {"content": intervention.content},
                decision.model_dump(mode="json"),
            )
            intervention.status = decision.decision
            if decision.decision == "accepted" and decision.new_immediate_goal:
                agent.current_goal = decision.new_immediate_goal
            self.session.add(intervention)
            create_event(
                self.session,
                run_id=run.id,
                day=run.current_day,
                minute=run.current_minute,
                event_type=EventType.INTERVENTION,
                summary=f"{agent.name}处理了用户建议：{decision.reason}",
                details=intervention.content,
                location_id=agent.current_location_id,
                agent_ids=[agent.id],
                llm_generated=llm_mode != "offline",
            )

    def _current_schedule(self, run_id: str, agent_id: str, day: int, minute: int) -> dict | None:
        schedule = self.session.exec(
            select(Schedule)
            .where(Schedule.run_id == run_id, Schedule.agent_id == agent_id, Schedule.day == day)
            .where(
                Schedule.start_minute <= minute + 30,
                Schedule.end_minute >= minute,
            )
            .order_by(Schedule.priority.desc())
        ).first()
        return schedule.model_dump() if schedule else None

    def _apply_rule_action(
        self,
        run: SimulationRun,
        agent: Agent,
        action,
        game_master: GameMaster,
        llm_mode: str = "offline",
    ) -> Event:
        validation = game_master.validate(agent.current_location_id, action)
        if not validation.allowed:
            agent.current_action = ActionType.IDLE.value
            self.session.add(agent)
            return create_event(
                self.session,
                run_id=run.id,
                day=run.current_day,
                minute=run.current_minute,
                event_type=EventType.SYSTEM,
                summary=f"{agent.name}的行动被 Game Master 拒绝。",
                details=validation.reason,
                location_id=agent.current_location_id,
                agent_ids=[agent.id],
                state_delta={"rejected_action": action.model_dump(mode="json")},
            )

        if action.type == ActionType.MOVE and action.target_location_id:
            old_location_id = agent.current_location_id
            agent.current_location_id = action.target_location_id
            agent.current_action = ActionType.MOVE.value
            summary = f"{agent.name}从{old_location_id}前往{action.target_location_id}。"
            event_type = EventType.MOVE
        elif action.type == ActionType.ATTEND_CLASS:
            agent.current_action = ActionType.ATTEND_CLASS.value
            summary = self._template_summary(CLASS_EVENTS, agent, run)
            event_type = EventType.CLASS
        elif action.type == ActionType.EAT:
            agent.current_action = ActionType.EAT.value
            agent.energy = min(100, agent.energy + 10)
            summary = self._template_summary(MEAL_EVENTS, agent, run)
            event_type = EventType.MEAL
        elif action.type == ActionType.JOIN_ACTIVITY:
            agent.current_action = ActionType.JOIN_ACTIVITY.value
            summary = self._template_summary(CLUB_EVENTS, agent, run)
            event_type = EventType.CLUB
        elif action.type == ActionType.TALK and action.target_agent_id:
            target = self.session.get(Agent, action.target_agent_id)
            provider = get_llm_provider(llm_mode)
            dialogue = provider.generate_dialogue(
                {
                    "speaker": agent.name,
                    "target": target.name if target else "同学",
                    "topic": action.topic,
                }
            )
            self._log_llm_call(
                run,
                agent.id,
                "generate_dialogue",
                {"target_agent_id": action.target_agent_id, "topic": action.topic},
                dialogue.model_dump(mode="json"),
            )
            agent.current_action = ActionType.TALK.value
            summary = dialogue.event_summary
            event_type = EventType.SOCIAL
            if target:
                relationship_service = RelationshipService(self.session)
                relationship = relationship_service.get_or_create(run.id, agent.id, target.id)
                relationship_service.apply_delta(
                    relationship,
                    affinity=dialogue.relationship_delta.affinity,
                    familiarity=dialogue.relationship_delta.familiarity,
                    trust=dialogue.relationship_delta.trust,
                    tag="友好交流",
                )
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
