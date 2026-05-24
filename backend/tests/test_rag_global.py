from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.rag.embedding import LocalEmbedder
from app.rag.indexing import load_index
from app.rag.retrieval import retrieve
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


def test_rag_global_retrieval() -> None:
    reset_state()
    client = TestClient(app)

    token1 = _signup(client, "alice")
    headers1 = {"Authorization": f"Bearer {token1}"}

    token2 = _signup(client, "bob")
    headers2 = {"Authorization": f"Bearer {token2}"}

    kb1 = client.post(
        "/api/v1/kb/create",
        headers=headers1,
        json={"title": "IAFB", "content_md": "## Abstract\nIAFB pruning method"},
    )
    kb1_id = kb1.json()["id"]
    client.post(f"/api/v1/kb/{kb1_id}/publish", headers=headers1)

    client.post(
        "/api/v1/kb/create",
        headers=headers2,
        json={"title": "Secret", "content_md": "## Abstract\nUnpublished content"},
    )

    vector_dir = Path(__file__).resolve().parents[1] / "vector_store"
    index, metadata = load_index(vector_dir)
    embedder = LocalEmbedder()

    results = retrieve("IAFB pruning", index, metadata, embedder, top_k=3)
    assert results, "No results found"
    assert any(item["title"] == "IAFB" for item in results)
    assert all(item["title"] != "Secret" for item in results)
