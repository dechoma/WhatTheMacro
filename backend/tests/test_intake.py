from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_and_get_intake():
    # Add entry
    data = {
        "date": "2099-01-01",
        "protein": 10,
        "carbs": 20,
        "fat": 5,
        "calories": 150,
        "description": "test meal"
    }
    resp = client.post("/api/intake", data=data)
    assert resp.status_code == 200
    assert resp.json().get("success") is True

    # Get for that date
    resp = client.get("/api/intake/2099-01-01")
    assert resp.status_code == 200
    js = resp.json()
    assert "sum" in js
    assert js["sum"]["protein"] >= 10
    found = any(entry["description"] == "test meal" for entry in js["entries"])
    assert found
