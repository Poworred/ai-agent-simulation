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
