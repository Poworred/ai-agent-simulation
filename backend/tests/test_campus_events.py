from fastapi.testclient import TestClient

from app.main import app


def test_one_day_generates_campus_specific_events():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Campus Event Test"})
    run_id = run_response.json()["run"]["id"]

    response = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 30, "llm_mode": "offline"})

    summaries = "\n".join(event["summary"] for event in response.json()["new_events"])
    assert any(keyword in summaries for keyword in ["社团", "食堂", "教学楼", "图书馆", "校园卡"])
