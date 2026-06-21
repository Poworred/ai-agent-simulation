from app.core.time import format_sim_time, is_after_simulation_end, next_tick


def test_format_sim_time():
    assert format_sim_time(day=1, minute=450) == "Day 1 07:30"
    assert format_sim_time(day=7, minute=1410) == "Day 7 23:30"


def test_next_tick_rolls_to_next_day():
    assert next_tick(day=1, minute=1410, tick_minutes=30) == (2, 0)


def test_simulation_end_after_day_7_2330():
    assert is_after_simulation_end(day=7, minute=1410) is True
    assert is_after_simulation_end(day=7, minute=1380) is False
