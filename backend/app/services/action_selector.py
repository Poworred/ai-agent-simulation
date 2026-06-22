from typing import Any

from app.domain.actions import ProposedAction
from app.domain.constants import ActionType


def choose_rule_action(
    agent_id: str,
    current_location_id: str,
    current_minute: int,
    nearby_agent_ids: list[str],
    pending_interventions: list[str],
    current_schedule: dict[str, Any] | None,
) -> ProposedAction:
    if any("社团" in intervention for intervention in pending_interventions) and current_location_id != "club_fair":
        return ProposedAction(
            type=ActionType.MOVE,
            agent_id=agent_id,
            target_location_id="club_fair",
            reason="用户建议 Agent 去社团招新点看看，且该建议符合校园适应目标。",
        )

    if current_schedule:
        target_location_id = current_schedule["location_id"]
        schedule_type = current_schedule["type"]
        if current_location_id != target_location_id:
            return ProposedAction(
                type=ActionType.MOVE,
                agent_id=agent_id,
                target_location_id=target_location_id,
                reason=f"当前日程是{current_schedule['title']}，需要前往目标地点。",
            )
        if schedule_type == "class":
            return ProposedAction(type=ActionType.ATTEND_CLASS, agent_id=agent_id, reason="已到达教学地点，按计划上课。")
        if schedule_type == "meal":
            return ProposedAction(type=ActionType.EAT, agent_id=agent_id, reason="已到达食堂，按饭点吃饭。")
        if schedule_type == "club":
            return ProposedAction(type=ActionType.JOIN_ACTIVITY, agent_id=agent_id, reason="已到达社团招新点，参加活动。")
        if schedule_type == "rest":
            return ProposedAction(type=ActionType.REST, agent_id=agent_id, reason="晚上回到宿舍休息。")

    if pending_interventions:
        return ProposedAction(type=ActionType.IDLE, agent_id=agent_id, reason="正在考虑用户建议，暂时观察环境。")

    if nearby_agent_ids and 10 * 60 <= current_minute <= 21 * 60:
        return ProposedAction(
            type=ActionType.TALK,
            agent_id=agent_id,
            target_agent_id=nearby_agent_ids[0],
            topic="校园适应",
            reason="附近有认识同学的机会。",
        )

    return ProposedAction(type=ActionType.IDLE, agent_id=agent_id, reason="当前没有高优先级日程，暂时等待。")
