"""Phase 1 remediation (#31): automated session expiry and revocation checks."""

import uuid

from app.auth import SESSION_COOKIE
from app.security import hash_token
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

PASSWORD = "CorrectHorseBatteryStaple42!"  # secret-scan-exempt: dummy test credential


def _register(client: TestClient) -> str:
    response = client.post(
        "/auth/register",
        json={
            "email": f"session-{uuid.uuid4().hex[:10]}@example.com",
            "password": PASSWORD,
            "full_name": "Session test",
            "organization_name": "Session org",
            "organization_slug": f"session-{uuid.uuid4().hex[:10]}",
        },
    )
    assert response.status_code == 201, response.text
    raw_token = client.cookies.get(SESSION_COOKIE)
    assert raw_token
    return raw_token


EXPIRY_STATEMENTS = {
    "expires_at": "UPDATE sessions SET expires_at = now() - interval '1 minute' WHERE token_hash = :hash",
    "absolute_expires_at": (
        "UPDATE sessions SET absolute_expires_at = now() - interval '1 minute' WHERE token_hash = :hash"
    ),
    "revoked_at": "UPDATE sessions SET revoked_at = now() - interval '1 minute' WHERE token_hash = :hash",
}


def _expire(database, raw_token: str, column: str) -> None:
    # Admin connection is used only to simulate the passing of time / revocation;
    # authentication itself always goes through the API runtime role.
    engine = create_engine(database.admin_url, future=True)
    try:
        with engine.begin() as connection:
            connection.execute(text(EXPIRY_STATEMENTS[column]), {"hash": hash_token(raw_token)})
    finally:
        engine.dispose()


def test_idle_expiry_rejects_authenticated_routes(client: TestClient, database) -> None:
    raw_token = _register(client)
    assert client.get("/auth/me").status_code == 200

    _expire(database, raw_token, "expires_at")

    assert client.get("/auth/me").status_code == 401
    assert client.get("/organizations").status_code == 401


def test_absolute_expiry_rejects_session(client: TestClient, database) -> None:
    raw_token = _register(client)
    assert client.get("/auth/me").status_code == 200

    _expire(database, raw_token, "absolute_expires_at")

    assert client.get("/auth/me").status_code == 401


def test_direct_revocation_rejects_session(client: TestClient, database) -> None:
    raw_token = _register(client)
    assert client.get("/auth/me").status_code == 200

    _expire(database, raw_token, "revoked_at")

    assert client.get("/auth/me").status_code == 401


def test_logout_marks_session_revoked(client: TestClient, database) -> None:
    registration = client.post(
        "/auth/register",
        json={
            "email": f"logout-{uuid.uuid4().hex[:10]}@example.com",
            "password": PASSWORD,
            "full_name": "Logout test",
            "organization_name": "Logout org",
        },
    )
    assert registration.status_code == 201, registration.text
    raw_token = client.cookies.get(SESSION_COOKIE)
    assert raw_token

    logout = client.post(
        "/auth/logout", headers={"X-CSRF-Token": registration.json()["csrf_token"]}
    )
    assert logout.status_code == 204

    engine = create_engine(database.admin_url, future=True)
    try:
        with engine.connect() as connection:
            revoked_at = connection.execute(
                text("SELECT revoked_at FROM sessions WHERE token_hash = :hash"),
                {"hash": hash_token(raw_token)},
            ).scalar()
        assert revoked_at is not None
    finally:
        engine.dispose()

    assert client.get("/auth/me").status_code == 401
