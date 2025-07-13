import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class FakeChoice:
    def __init__(self, content):
        self.message = type("msg", (), {"content": content})

def fake_image_bytes():
    return b"fakeimagedata"

# ----- FOOD_MACROS: /estimate-macro -----

def test_estimate_macro_barcode_found(mocker):
    barcode_json = '{"barcode": "5901234567890", "description": "barcode detected", "base_amount": 100, "unit": "g", "protein": null, "carbs": null, "fat": null, "calories": null}'
    mocker.patch(
        "routers.food_macros.openai.chat.completions.create",
        return_value=type("R", (), {"choices": [FakeChoice(barcode_json)]}),
    )
    def fake_off(barcode):
        if barcode == "5901234567890":
            return {"description": "Milk 3.2%", "protein": 3.2, "carbs": 5, "fat": 3.2, "calories": 61, "barcode": barcode}
        return None
    mocker.patch("routers.food_macros.get_macros_from_openfoodfacts", side_effect=fake_off)

    resp = client.post(
        "/api/estimate-macro",
        files={"image": ("test.jpg", fake_image_bytes(), "image/jpeg")}
    )
    js = resp.json()
    assert resp.status_code == 200
    assert js["barcode"] == "5901234567890"
    assert js["description"] == "Milk 3.2%"
    assert js["protein"] == 3.2

def test_estimate_macro_no_barcode_gpt_estimation(mocker):
    no_barcode_json = '{"barcode": null, "description": "omelette", "base_amount": 100, "unit": "g", "protein": 9, "carbs": 2, "fat": 8, "calories": 110}'
    mocker.patch(
        "routers.food_macros.openai.chat.completions.create",
        return_value=type("R", (), {"choices": [FakeChoice(no_barcode_json)]}),
    )
    mocker.patch("routers.food_macros.get_macros_from_openfoodfacts", return_value=None)

    resp = client.post(
        "/api/estimate-macro",
        files={"image": ("test2.jpg", fake_image_bytes(), "image/jpeg")}
    )
    js = resp.json()
    assert resp.status_code == 200
    assert js["barcode"] is None
    assert js["protein"] == 9
    assert js["description"] == "omelette"

def test_estimate_macro_bad_gpt_json(mocker):
    bad_json = 'not a json'
    mocker.patch(
        "routers.food_macros.openai.chat.completions.create",
        return_value=type("R", (), {"choices": [FakeChoice(bad_json)]}),
    )
    mocker.patch("routers.food_macros.get_macros_from_openfoodfacts", return_value=None)

    resp = client.post(
        "/api/estimate-macro",
        files={"image": ("bad.jpg", fake_image_bytes(), "image/jpeg")}
    )
    js = resp.json()
    assert resp.status_code == 200
    assert "error" in js

# ----- FOOD_MACROS: /openai-logs -----

def test_openai_logs_smoke():
    resp = client.get("/api/openai-logs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

# ----- INTAKE -----

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

# ----- TARGETS -----

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
