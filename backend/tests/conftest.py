import os
import time
import importlib
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_db_env(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("db")
    db_path = str(db_dir / "test.db")
    os.environ["DB_PATH"] = db_path
    yield db_path


@pytest.fixture(scope="session")
def client(test_db_env):
    # Import after setting DB_PATH so init_db() uses the temp DB
    import main
    importlib.reload(main)
    return TestClient(main.app)


def _signup_or_login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/api/signup", json={"email": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    # fallback to login
    r = client.post(
        "/api/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def auth_token(client: TestClient) -> str:
    unique = int(time.time())
    email = f"tester{unique}@example.com"
    return _signup_or_login(client, email, "secret123")


@pytest.fixture(scope="session")
def auth_headers(auth_token: str):
    return {"Authorization": f"Bearer {auth_token}"}


