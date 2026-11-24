"""Phase 1 remediation (#28): API runtime must use the unprivileged role."""

import uuid

from app.config import get_settings
from app.db import get_engine, set_tenant_context
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

PASSWORD = "CorrectHorseBatteryStaple42!"  # secret-scan-exempt: dummy test credential


def _register(client: TestClient, label: str) -> dict:
    response = client.post(
        "/auth/register",
        json={
            "email": f"{label}-{uuid.uuid4().hex[:10]}@example.com",
            "password": PASSWORD,
            "full_name": label,
            "organization_name": f"{label} org",
            "organization_slug": f"{label}-{uuid.uuid4().hex[:10]}",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_runtime_engine_uses_app_database_url(database) -> None:
    assert get_settings().app_database_url == database.app_url
    engine = get_engine()
    try:
        assert engine.url.render_as_string(hide_password=False) == database.app_url
    finally:
        engine.dispose()


def test_app_role_is_not_privileged(database) -> None:
    engine = create_engine(database.admin_url, future=True)
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT rolsuper, rolbypassrls, rolcanlogin FROM pg_roles WHERE rolname = :role"),
            {"role": database.role},
        ).one()
    assert row.rolsuper is False
    assert row.rolbypassrls is False
    assert row.rolcanlogin is True
    engine.dispose()


def test_api_runs_through_app_role_and_rejects_cross_tenant_access() -> None:
    owner = TestClient(app)
    other = TestClient(app)
    owner_body = _register(owner, "owner")
    other_body = _register(other, "other")
    org_id = owner_body["organization"]["id"]

    assert owner.get(f"/organizations/{org_id}").status_code == 200
    assert other.get(f"/organizations/{org_id}").status_code == 404
    assert other.get("/organizations").json()[0]["id"] == other_body["organization"]["id"]

    added = owner.post(
        f"/organizations/{org_id}/members",
        headers={"X-CSRF-Token": owner_body["csrf_token"]},
        json={"email": other_body["user"]["email"], "role": "editor"},
    )
    assert added.status_code == 201, added.text
    assert other.get(f"/organizations/{org_id}").status_code == 200

    # The editor is now a member but still cannot perform owner-only changes.
    blocked = other.patch(
        f"/organizations/{org_id}",
        headers={"X-CSRF-Token": other_body["csrf_token"]},
        json={"name": "hijacked"},
    )
    assert blocked.status_code == 403


def test_tenant_context_is_transaction_local_and_pool_safe(database) -> None:
    engine = create_engine(database.app_url, pool_size=1, max_overflow=0, future=True)
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    try:
        with Session(engine, future=True) as db:
            set_tenant_context(db, str(tenant_id), str(user_id))
            assert db.scalar(text("SELECT current_setting('app.current_tenant_id', true)")) == str(tenant_id)
            assert db.scalar(text("SELECT current_setting('app.current_user_id', true)")) == str(user_id)
            db.commit()

        with engine.connect() as connection:
            backend_pid = connection.execute(text("SELECT pg_backend_pid()")).scalar()
            assert connection.execute(text("SELECT current_setting('app.current_tenant_id', true)")).scalar() == ""
            assert connection.execute(text("SELECT current_setting('app.current_user_id', true)")).scalar() == ""

        with engine.connect() as connection:
            # Same pooled backend connection, no context carried over.
            assert connection.execute(text("SELECT pg_backend_pid()")).scalar() == backend_pid
    finally:
        engine.dispose()
