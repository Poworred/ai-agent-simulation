from fastapi.testclient import TestClient

from app.main import app


def test_submit_intervention_creates_pending_intervention_and_memory():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Intervention Test"})
    agent_id = run_response.json()["agents"][0]["id"]

    response = client.post(
        f"/api/agents/{agent_id}/interventions",
        json={"content": "你可以去社团招新点看看。"},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"

    detail = client.get(f"/api/agents/{agent_id}").json()
    assert any("社团招新" in memory["content"] for memory in detail["important_memories"])


def test_intervention_can_affect_next_tick_action():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Intervention Action Test"})
    run_id = run_response.json()["run"]["id"]
    agent_id = run_response.json()["agents"][0]["id"]

    client.post(f"/api/agents/{agent_id}/interventions", json={"content": "你可以去社团招新点看看。"})
    tick = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"}).json()

    updated = next(agent for agent in tick["updated_agents"] if agent["id"] == agent_id)
    assert updated["current_location_id"] == "club_fair"


def test_tick_marks_intervention_considered():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Intervention Status Test"})
    run_id = run_response.json()["run"]["id"]
    agent_id = run_response.json()["agents"][0]["id"]

    client.post(f"/api/agents/{agent_id}/interventions", json={"content": "你可以去社团招新点看看。"})
    client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"})

    events = client.get(f"/api/runs/{run_id}/events?limit=50").json()
    assert any("建议" in event["summary"] or "社团" in event["summary"] for event in events)


def test_accepted_intervention_updates_agent_goal_after_tick():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Intervention Goal Test"})
    run_id = run_response.json()["run"]["id"]
    agent_id = run_response.json()["agents"][0]["id"]

    client.post(f"/api/agents/{agent_id}/interventions", json={"content": "你可以去社团招新点看看。"})
    client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"})

    detail = client.get(f"/api/agents/{agent_id}").json()
    assert detail["state"]["current_goal"] == "去社团招新点看看"
