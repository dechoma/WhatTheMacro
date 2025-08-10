from fastapi.testclient import TestClient


def test_signup_and_login(client: TestClient):
    email = "auth_tester@example.com"
    password = "secret123"

    r = client.post("/api/signup", json={"email": email, "password": password})
    if r.status_code == 200:
        token = r.json().get("access_token")
        assert token
    else:
        assert r.status_code == 400
        # already exists, proceed to login

    r2 = client.post(
        "/api/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r2.status_code == 200
    token2 = r2.json().get("access_token")
    assert token2

    r3 = client.post(
        "/api/targets",
        json={"protein": 1, "carbs": 2, "fat": 3, "calories": 4},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r3.status_code == 200

    r4 = client.post("/api/targets", json={"protein": 1, "carbs": 2, "fat": 3, "calories": 4})
    assert r4.status_code in (401, 403)


