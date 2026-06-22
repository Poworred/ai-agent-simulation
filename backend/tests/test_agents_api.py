from fastapi.testclient import TestClient

from app.main import app


def test_get_agent_detail_includes_profile_state_events_and_memory():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Agent Detail Test"})
    agent_id = run_response.json()["agents"][0]["id"]

    response = client.get(f"/api/agents/{agent_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["id"] == agent_id
    assert "state" in body
    assert "recent_events" in body
    assert "important_memories" in body
    assert "relationships" in body
