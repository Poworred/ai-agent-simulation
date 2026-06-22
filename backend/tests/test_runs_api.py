from fastapi.testclient import TestClient

from app.main import app


def test_create_run_initializes_seed_world():
    client = TestClient(app)

    response = client.post("/api/runs", json={"name": "测试模拟"})

    assert response.status_code == 201
    body = response.json()
    assert body["run"]["current_day"] == 1
    assert body["run"]["current_minute"] == 450
    assert len(body["locations"]) >= 6
    assert len(body["agents"]) >= 5
    assert len(body["recent_events"]) >= 1


def test_create_run_can_be_called_multiple_times():
    client = TestClient(app)

    first = client.post("/api/runs", json={"name": "第一次模拟"}).json()
    second_response = client.post("/api/runs", json={"name": "第二次模拟"})

    assert second_response.status_code == 201
    second = second_response.json()
    assert first["run"]["id"] != second["run"]["id"]
    assert len(second["locations"]) >= 6
    assert len(second["agents"]) >= 5
    assert set(agent["id"] for agent in first["agents"]).isdisjoint(
        agent["id"] for agent in second["agents"]
    )


def test_second_created_run_can_tick_with_world_locations():
    client = TestClient(app)
    client.post("/api/runs", json={"name": "第一次模拟"})
    second = client.post("/api/runs", json={"name": "第二次模拟"}).json()
    run_id = second["run"]["id"]

    response = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 2, "llm_mode": "offline"})

    assert response.status_code == 200
    event_types = {event["event_type"] for event in response.json()["new_events"]}
    assert "move" in event_types


def test_tick_advances_time_and_creates_events():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Tick Test"})
    run_id = run_response.json()["run"]["id"]

    response = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"})

    assert response.status_code == 200
    body = response.json()
    assert body["run"]["current_minute"] == 480
    assert len(body["new_events"]) >= 1
    assert len(body["updated_agents"]) >= 1


def test_tick_writes_agent_memory():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Memory Tick Test"})
    run_id = run_response.json()["run"]["id"]
    agent_id = run_response.json()["agents"][0]["id"]

    client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"})
    detail_response = client.get(f"/api/agents/{agent_id}")

    assert detail_response.status_code == 200
    assert len(detail_response.json()["important_memories"]) >= 1


def test_tick_near_night_generates_reflection_event_offline():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Reflection Test"})
    run_id = run_response.json()["run"]["id"]

    response = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 30, "llm_mode": "offline"})

    assert response.status_code == 200
    summaries = [event["summary"] for event in response.json()["new_events"]]
    assert any("反思" in summary or "回顾" in summary for summary in summaries)


def test_offline_tick_can_generate_social_dialogue_event():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Dialogue Test"})
    run_id = run_response.json()["run"]["id"]

    response = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 7, "llm_mode": "offline"})

    assert response.status_code == 200
    events = response.json()["new_events"]
    assert any(event["event_type"] == "social" for event in events)
