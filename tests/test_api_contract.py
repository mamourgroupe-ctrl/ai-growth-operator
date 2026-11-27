import json
from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_problem_response_for_unknown_route() -> None:
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["status"] == 404
    assert body["instance"] == "/does-not-exist"
    assert body["type"].endswith("/http-error")


def test_committed_openapi_matches_application() -> None:
    committed = json.loads(Path("apps/api/openapi.json").read_text(encoding="utf-8"))
    assert committed == app.openapi()
