from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_targets_flow():
    # Set new target
    data = {
        "protein": 123,
        "carbs": 321,
        "fat": 11,
        "calories": 999
    }
    resp = client.post("/api/targets", json=data)
    assert resp.status_code == 200
    assert resp.json().get("success") is True

    # Get current target (should match just set)
    resp = client.get("/api/targets")
    assert resp.status_code == 200
    js = resp.json()
    for k in data:
        assert abs(js[k] - data[k]) < 0.01

    # Get target history
    resp = client.get("/api/targets/history")
    assert resp.status_code == 200
    hist = resp.json()
    assert isinstance(hist, list)
    assert hist[0]["protein"] == 123
