from pydantic import BaseModel

from app.domain.actions import ProposedAction
from app.domain.constants import ActionType


class ValidationResult(BaseModel):
    allowed: bool
    reason: str


class GameMaster:
    def __init__(self, paths: dict[str, set[str]], locations: set[str]):
        self.paths = paths
        self.locations = locations

    def validate(self, current_location_id: str, action: ProposedAction) -> ValidationResult:
        if action.type == ActionType.MOVE:
            return self._validate_move(current_location_id, action)
        if action.type == ActionType.TALK and not action.target_agent_id:
            return ValidationResult(allowed=False, reason="对话行动缺少目标 Agent。")
        return ValidationResult(allowed=True, reason="行动合法。")

    def _validate_move(self, current_location_id: str, action: ProposedAction) -> ValidationResult:
        if not action.target_location_id:
            return ValidationResult(allowed=False, reason="移动行动缺少目标地点。")
        if action.target_location_id not in self.locations:
            return ValidationResult(allowed=False, reason="目标地点不存在。")
        if action.target_location_id == current_location_id:
            return ValidationResult(allowed=True, reason="Agent 已在目标地点。")
        connected = self.paths.get(current_location_id, set())
        if action.target_location_id not in connected:
            return ValidationResult(allowed=False, reason="当前地点和目标地点不连通。")
        return ValidationResult(allowed=True, reason="移动行动合法。")
