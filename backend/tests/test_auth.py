from fastapi.testclient import TestClient

from app.main import app
from tests._utils import reset_state


def test_auth_flow() -> None:
    reset_state()
    client = TestClient(app)

    signup = client.post(
        "/api/v1/auth/signup",
        json={"username": "alice", "email": "alice@example.com", "password": "secret123"},
    )
    assert signup.status_code == 200, signup.text

    login = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "secret123"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["username"] == "alice"
