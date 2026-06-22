from app.domain.constants import DEFAULT_END_DAY, DEFAULT_END_MINUTE


def format_sim_time(day: int, minute: int) -> str:
    hour = minute // 60
    mins = minute % 60
    return f"Day {day} {hour:02d}:{mins:02d}"


def next_tick(day: int, minute: int, tick_minutes: int) -> tuple[int, int]:
    new_minute = minute + tick_minutes
    new_day = day
    while new_minute >= 24 * 60:
        new_day += 1
        new_minute -= 24 * 60
    return new_day, new_minute


def is_after_simulation_end(day: int, minute: int) -> bool:
    return day > DEFAULT_END_DAY or (day == DEFAULT_END_DAY and minute >= DEFAULT_END_MINUTE)
