from fastapi.testclient import TestClient

from app.main import app
from tests._utils import reset_state


def _signup(client: TestClient, username: str) -> str:
    client.post(
        "/api/v1/auth/signup",
        json={"username": username, "email": f"{username}@example.com", "password": "secret123"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "secret123"},
    )
    return login.json()["access_token"]


def test_kb_crud_flow() -> None:
    reset_state()
    client = TestClient(app)

    token = _signup(client, "alice")
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        "/api/v1/kb/create",
        headers=headers,
        json={"title": "My KB", "content_md": "## Abstract\nHello"},
    )
    assert create.status_code == 200, create.text
    kb_id = create.json()["id"]

    update = client.put(
        f"/api/v1/kb/{kb_id}",
        headers=headers,
        json={"title": "My KB v2"},
    )
    assert update.status_code == 200, update.text

    listing = client.get("/api/v1/kb/my-kbs", headers=headers)
    assert listing.status_code == 200, listing.text
    assert len(listing.json()) == 1

    token2 = _signup(client, "bob")
    headers2 = {"Authorization": f"Bearer {token2}"}
    forbidden = client.put(
        f"/api/v1/kb/{kb_id}",
        headers=headers2,
        json={"title": "Hack"},
    )
    assert forbidden.status_code == 403
