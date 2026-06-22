from enum import StrEnum


DEFAULT_START_DAY = 1
DEFAULT_START_MINUTE = 7 * 60 + 30
DEFAULT_END_DAY = 7
DEFAULT_END_MINUTE = 23 * 60 + 30
DEFAULT_TICK_MINUTES = 30


class RunStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class EventType(StrEnum):
    CLASS = "class"
    MEAL = "meal"
    SOCIAL = "social"
    CLUB = "club"
    LOST_ITEM = "lost_item"
    REFLECTION = "reflection"
    INTERVENTION = "intervention"
    SYSTEM = "system"
    MOVE = "move"


class ActionType(StrEnum):
    MOVE = "move"
    ATTEND_CLASS = "attend_class"
    EAT = "eat"
    TALK = "talk"
    JOIN_ACTIVITY = "join_activity"
    ASK_HELP = "ask_help"
    HANDLE_LOST_ITEM = "handle_lost_item"
    STUDY = "study"
    REST = "rest"
    REFLECT = "reflect"
    IDLE = "idle"
