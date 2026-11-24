import uuid

from app.main import app
from fastapi.testclient import TestClient

PASSWORD = "CorrectHorseBatteryStaple42!"


def _register(client: TestClient, *, email: str | None = None, slug: str | None = None) -> dict:
    email = email or f"user-{uuid.uuid4().hex[:10]}@example.com"
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "full_name": "مالك المخبز",
            "organization_name": "مخبز الجزائر",
            "organization_slug": slug,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_registration_creates_owner_and_session(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": f"owner-{uuid.uuid4().hex[:10]}@example.com",
            "password": PASSWORD,
            "full_name": "مالك المخبز",
            "organization_name": "مخبز الجزائر",
            "organization_slug": f"bakery-{uuid.uuid4().hex[:8]}",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["organization"]["default_ui_locale"] == "ar"
    assert body["organization"]["display_currencies"] == {"DZD": True, "USD": True}
    assert "HttpOnly" in response.headers["set-cookie"]
    assert body["csrf_token"]

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["memberships"][0]["role"] == "owner"


def test_login_and_logout_require_valid_credentials_and_csrf() -> None:
    client = TestClient(app)
    registered = _register(client)
    email = registered["user"]["email"]

    bad = TestClient(app).post("/auth/login", json={"email": email, "password": "wrong-password"})
    assert bad.status_code == 401
    assert bad.headers["content-type"].startswith("application/problem+json")

    other = TestClient(app)
    good = other.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert good.status_code == 200
    csrf = good.json()["csrf_token"]

    missing_csrf = other.post("/auth/logout")
    assert missing_csrf.status_code == 403

    logout = other.post("/auth/logout", headers={"X-CSRF-Token": csrf})
    assert logout.status_code == 204
    assert other.get("/auth/me").status_code == 401


def test_duplicate_email_returns_conflict(client: TestClient) -> None:
    email = f"dup-{uuid.uuid4().hex[:10]}@example.com"
    _register(client, email=email)
    conflict = TestClient(app).post(
        "/auth/register",
        json={
            "email": email.upper(),
            "password": PASSWORD,
            "full_name": "Duplicate",
            "organization_name": "Other org",
        },
    )
    assert conflict.status_code == 409


def test_validation_error_uses_problem_format(client: TestClient) -> None:
    response = client.post("/auth/register", json={"email": "not-an-email"})
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["title"] == "Validation error"
