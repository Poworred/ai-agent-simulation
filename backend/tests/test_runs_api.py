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
