from fastapi.testclient import TestClient
import os


def test_global_auth_rate_limit_cutoff(test_db_env):
    # Ensure admin password for signup in tests
    os.environ.setdefault("ADMIN_PASSWORD", "test-admin")

    # Reset global/per-IP limiters (no module reload to keep app/client stable)
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

    # Read configured limit for this test run
    max_global = int(os.getenv("AUTH_GLOBAL_MAX_REQUESTS", "30"))
    ok_logins = max(0, max_global - 1)  # after 1 signup

    # Perform ok_logins-1 requests first, then one more to reach the limit
    for i in range(max(0, ok_logins - 1)):
        r = client.post(
            "/api/login",
            data={"username": "ratelimit@example.com", "password": "secret123"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Forwarded-For": f"203.0.113.{i}",
            },
        )
        assert r.status_code == 200, f"Attempt {i} failed: {r.status_code} {r.text}"

    # Last OK request to reach the limit exactly
    r_last_ok = client.post(
        "/api/login",
        data={"username": "ratelimit@example.com", "password": "secret123"},
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Forwarded-For": "203.0.113.200",
        },
    )
    assert r_last_ok.status_code == 200

    # Next one should be blocked by global rate limiter (429)
    r_blocked = client.post(
        "/api/login",
        data={"username": "ratelimit@example.com", "password": "secret123"},
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Forwarded-For": "203.0.113.250",
        },
    )
    assert r_blocked.status_code == 429

    # Reset limiters to avoid affecting other tests
    reset_all_limiters()


