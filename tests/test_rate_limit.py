
from fastapi.testclient import TestClient

from app.main import app
from app.services import rate_limit_service
from collections import defaultdict, deque

client = TestClient(app)


def test_login_rate_limit_returns_429(monkeypatch):
    # Use a fresh rate-limit store for this test
    monkeypatch.setattr(
    rate_limit_service,
    "login_attempts",
    defaultdict(deque),
)

    # First five attempts should not be rate-limited.
    # Invalid credentials should return 401.
    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={
                "email": "missing-user@example.com",
                "password": "WrongPassword123",
            },
        )
        assert response.status_code == 401

    # Sixth attempt within the same minute should be blocked.
    response = client.post(
        "/auth/login",
        json={
            "email": "missing-user@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 429
    assert "Retry-After" in response.headers
