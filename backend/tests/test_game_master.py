from sqlmodel import Session

from app.db.session import engine
from app.domain.actions import ProposedAction
from app.domain.constants import ActionType
from app.models.tables import Agent, SimulationRun
from app.services.game_master import GameMaster
from app.services.simulation import SimulationService


def test_game_master_rejects_invalid_location():
    gm = GameMaster(paths={"dorm": {"canteen"}}, locations={"dorm", "canteen"})
    action = ProposedAction(
        type=ActionType.MOVE,
        agent_id="agent_1",
        target_location_id="moon",
        reason="test",
    )

    result = gm.validate(current_location_id="dorm", action=action)

    assert result.allowed is False
    assert "不存在" in result.reason


def test_game_master_rejects_unconnected_move():
    gm = GameMaster(paths={"dorm": {"canteen"}}, locations={"dorm", "canteen", "library"})
    action = ProposedAction(
        type=ActionType.MOVE,
        agent_id="agent_1",
        target_location_id="library",
        reason="test",
    )

    result = gm.validate(current_location_id="dorm", action=action)

    assert result.allowed is False
    assert "不连通" in result.reason


def test_game_master_allows_connected_move():
    gm = GameMaster(paths={"dorm": {"canteen"}}, locations={"dorm", "canteen"})
    action = ProposedAction(
        type=ActionType.MOVE,
        agent_id="agent_1",
        target_location_id="canteen",
        reason="test",
    )

    result = gm.validate(current_location_id="dorm", action=action)

    assert result.allowed is True


def test_rejected_move_creates_system_event_and_keeps_location():
    with Session(engine) as session:
        run = SimulationRun(id="run_test", name="test", current_day=1, current_minute=480)
        agent = Agent(
            id="agent_1",
            run_id=run.id,
            name="测试 Agent",
            role="新生",
            major="测试专业",
            personality="谨慎",
            interests=[],
            long_term_goals=[],
            social_style="克制",
            current_location_id="dorm",
            current_goal="测试",
        )
        session.add(run)
        session.add(agent)
        session.commit()

        action = ProposedAction(
            type=ActionType.MOVE,
            agent_id=agent.id,
            target_location_id="moon",
            reason="测试非法地点",
        )
        service = SimulationService(session)
        event = service._apply_rule_action(
            run,
            agent,
            action,
            GameMaster(paths={"dorm": {"canteen"}}, locations={"dorm", "canteen"}),
        )

        assert agent.current_location_id == "dorm"
        assert agent.current_action == ActionType.IDLE.value
        assert event.event_type == "system"
        assert "拒绝" in event.summary
