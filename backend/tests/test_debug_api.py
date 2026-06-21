from fastapi.testclient import TestClient

from app.main import app


def test_debug_memories_returns_agent_memories():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Debug Test"})
    agent_id = run_response.json()["agents"][0]["id"]

    response = client.get(f"/api/debug/agents/{agent_id}/memories")

    assert response.status_code == 200
    assert isinstance(response.json()["memories"], list)


def test_debug_llm_calls_returns_logged_fake_reflection_calls():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Debug LLM Test"})
    run_id = run_response.json()["run"]["id"]

    client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 30, "llm_mode": "offline"})
    response = client.get(f"/api/debug/runs/{run_id}/llm-calls")

    assert response.status_code == 200
    assert len(response.json()["llm_calls"]) >= 1
