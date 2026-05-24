from pathlib import Path

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


def test_publish_sync() -> None:
    reset_state()
    client = TestClient(app)

    token = _signup(client, "alice")
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        "/api/v1/kb/create",
        headers=headers,
        json={"title": "IAFB Guide", "content_md": "## Abstract\nIAFB pruning"},
    )
    kb_id = create.json()["id"]

    publish = client.post(f"/api/v1/kb/{kb_id}/publish", headers=headers)
    assert publish.status_code == 200, publish.text

    vector_dir = Path(__file__).resolve().parents[1] / "vector_store"
    assert (vector_dir / "kb.index.faiss").exists()
    assert (vector_dir / "kb.metadata.json").exists()
