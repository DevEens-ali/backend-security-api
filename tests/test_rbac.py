
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import get_current_user


class FakeUser:
    def __init__(self, user_id: int, name: str, role: str):
        self.id = user_id
        self.name = name
        self.email = f"{role}@example.com"
        self.role = role


client = TestClient(app)


@pytest.fixture
def set_test_user():
    def _set_user(role: str):
        app.dependency_overrides[get_current_user] = (
            lambda: FakeUser(1, "Test User", role)
        )

    yield _set_user

    app.dependency_overrides.clear()


def test_user_can_access_own_profile(set_test_user):
    set_test_user("user")

    response = client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["role"] == "user"


def test_user_cannot_access_admin_endpoint(set_test_user):
    set_test_user("user")

    response = client.get("/users/admin-only")

    assert response.status_code == 403


def test_admin_can_access_admin_endpoint(set_test_user):
    set_test_user("admin")

    response = client.get("/users/admin-only")

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_user_cannot_access_moderator_endpoint(set_test_user):
    set_test_user("user")

    response = client.get("/users/moderator-only")

    assert response.status_code == 403


def test_moderator_can_access_moderator_endpoint(set_test_user):
    set_test_user("moderator")

    response = client.get("/users/moderator-only")

    assert response.status_code == 200
    assert response.json()["role"] == "moderator"


def test_moderator_cannot_access_user_area(set_test_user):
    set_test_user("moderator")

    response = client.get("/users/user-area")

    assert response.status_code == 403
