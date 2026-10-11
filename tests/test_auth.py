
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_requires_valid_email():
    response = client.post(
        "/auth/login",
        json={
            "email": "not-an-email",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 422


def test_refresh_requires_cookie():
    response = client.post("/auth/refresh")

    assert response.status_code == 401
