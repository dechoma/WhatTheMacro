import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class FakeChoice:
    def __init__(self, content):
        self.message = type("msg", (), {"content": content})

def fake_image_bytes():
    return b"fakeimagedata"

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

def test_openai_logs_smoke():
    resp = client.get("/api/openai-logs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
