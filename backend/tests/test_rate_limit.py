from fastapi.testclient import TestClient
import os


def test_global_auth_rate_limit_cutoff(test_db_env):
    # Ensure admin password for signup in tests
    os.environ.setdefault("ADMIN_PASSWORD", "test-admin")

    # Reset global/per-IP limiters and use the current app
    from rate_limit import reset_all_limiters
    reset_all_limiters()

    import main
    client = TestClient(main.app)

    # Prepare a valid user once (with admin header)
    signup = client.post(
        "/api/signup",
        json={"email": "ratelimit@example.com", "password": "secret123"},
        headers={"X-Admin-Password": "test-admin"},
    )
    assert signup.status_code in (200, 400)

    # We already used 1 request for signup; allow 28 more successful logins (total 29)
    for i in range(28):
        r = client.post(
            "/api/login",
            data={"username": "ratelimit@example.com", "password": "secret123"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Forwarded-For": f"203.0.113.{i}",
            },
        )
        assert r.status_code == 200, f"Attempt {i} failed: {r.status_code} {r.text}"

    # 30th total should still pass
    r30 = client.post(
        "/api/login",
        data={"username": "ratelimit@example.com", "password": "secret123"},
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Forwarded-For": "203.0.113.200",
        },
    )
    assert r30.status_code == 200

    # 31st total should be blocked by global rate limiter (429)
    r31 = client.post(
        "/api/login",
        data={"username": "ratelimit@example.com", "password": "secret123"},
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Forwarded-For": "203.0.113.250",
        },
    )
    assert r31.status_code == 429

    # Reset limiters to avoid affecting other tests
    reset_all_limiters()


