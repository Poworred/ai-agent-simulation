from app.domain.actions import ProposedAction
from app.domain.constants import ActionType
from app.services.action_selector import choose_rule_action


def test_agent_moves_to_class_when_schedule_is_near():
    action = choose_rule_action(
        agent_id="agent_wang_yinuo",
        current_location_id="dorm",
        current_minute=8 * 60 + 10,
        nearby_agent_ids=[],
        pending_interventions=[],
        current_schedule={
            "type": "class",
            "location_id": "teaching_building",
            "title": "上午课程",
            "start_minute": 8 * 60 + 30,
        },
    )

    assert isinstance(action, ProposedAction)
    assert action.type == ActionType.MOVE
    assert action.target_location_id == "teaching_building"


def test_agent_eats_at_meal_time():
    action = choose_rule_action(
        agent_id="agent_wang_yinuo",
        current_location_id="teaching_building",
        current_minute=12 * 60,
        nearby_agent_ids=[],
        pending_interventions=[],
        current_schedule={
            "type": "meal",
            "location_id": "canteen",
            "title": "午饭",
            "start_minute": 12 * 60,
        },
    )

    assert action.type == ActionType.MOVE
    assert action.target_location_id == "canteen"
