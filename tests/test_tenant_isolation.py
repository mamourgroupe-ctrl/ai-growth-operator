import uuid

import pytest
from app.db import set_tenant_context
from app.main import app
from app.models import Tenant, TenantMembership, User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from tests.conftest import clear_rls_context

PASSWORD = "CorrectHorseBatteryStaple42!"  # secret-scan-exempt: dummy test credential


def _seed(db: Session, slug: str, email: str) -> tuple[uuid.UUID, uuid.UUID]:
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    set_tenant_context(db, str(tenant_id), str(user_id))
    db.add(User(id=user_id, email=email, password_hash="hash", full_name=slug))
    db.flush()
    db.add(
        Tenant(
            id=tenant_id,
            name=slug,
            slug=slug,
            display_currencies={"DZD": True, "USD": True},
            supported_ui_locales={"ar": True, "fr": True},
        )
    )
    db.flush()
    db.add(TenantMembership(tenant_id=tenant_id, user_id=user_id, role="owner"))
    db.commit()
    return tenant_id, user_id


def test_application_role_is_not_superuser_or_bypassrls(database) -> None:
    engine = create_engine(database.admin_url, future=True)
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = :role"),
            {"role": database.role},
        ).one()
    assert row.rolsuper is False
    assert row.rolbypassrls is False


def test_direct_reads_with_application_role_are_tenant_scoped(app_engine) -> None:
    with Session(app_engine, expire_on_commit=False, future=True) as db:
        tenant_a, user_a = _seed(db, f"iso-a-{uuid.uuid4().hex[:8]}", f"iso-a-{uuid.uuid4().hex[:8]}@example.com")
        tenant_b, _ = _seed(db, f"iso-b-{uuid.uuid4().hex[:8]}", f"iso-b-{uuid.uuid4().hex[:8]}@example.com")

        clear_rls_context(db)
        assert db.scalar(text("SELECT count(*) FROM tenants")) == 0

        set_tenant_context(db, str(tenant_a), str(user_a))
        visible = db.scalars(text("SELECT id FROM tenants")).all()
        assert visible == [tenant_a]

        guessed = db.scalar(text("SELECT count(*) FROM tenants WHERE id = :id"), {"id": tenant_b})
        assert guessed == 0


def test_rls_with_check_rejects_insert_into_other_tenant(app_db: Session) -> None:
    tenant_a, user_a = _seed(app_db, f"chk-a-{uuid.uuid4().hex[:8]}", f"chk-a-{uuid.uuid4().hex[:8]}@example.com")
    tenant_b, _ = _seed(app_db, f"chk-b-{uuid.uuid4().hex[:8]}", f"chk-b-{uuid.uuid4().hex[:8]}@example.com")
    set_tenant_context(app_db, str(tenant_a), str(user_a))

    with pytest.raises(ProgrammingError):
        app_db.execute(
            text(
                "INSERT INTO ai_generation_jobs "
                "(id, tenant_id, capability, kind, prompt, idempotency_key) "
                "VALUES (:id, :tenant_id, 'text', 'social_post', 'x', :key)"
            ),
            {"id": uuid.uuid4(), "tenant_id": tenant_b, "key": uuid.uuid4().hex},
        )
    app_db.rollback()


def test_api_rejects_cross_tenant_and_non_owner_member_change() -> None:
    owner = TestClient(app)
    register = owner.post(
        "/auth/register",
        json={
            "email": f"iso-owner-{uuid.uuid4().hex[:8]}@example.com",
            "password": PASSWORD,
            "full_name": "Owner",
            "organization_name": "ISO org",
            "organization_slug": f"iso-org-{uuid.uuid4().hex[:8]}",
        },
    )
    assert register.status_code == 201
    owner_body = register.json()
    org_id = owner_body["organization"]["id"]

    other = TestClient(app)
    other_register = other.post(
        "/auth/register",
        json={
            "email": f"iso-other-{uuid.uuid4().hex[:8]}@example.com",
            "password": PASSWORD,
            "full_name": "Other",
            "organization_name": "Other org",
            "organization_slug": f"iso-other-{uuid.uuid4().hex[:8]}",
        },
    )
    assert other_register.status_code == 201
    assert other.get(f"/organizations/{org_id}").status_code == 404

    added = owner.post(
        f"/organizations/{org_id}/members",
        headers={"X-CSRF-Token": owner_body["csrf_token"]},
        json={"email": other_register.json()["user"]["email"], "role": "viewer"},
    )
    assert added.status_code == 201

    blocked = other.patch(
        f"/organizations/{org_id}/members/{owner_body['user']['id']}",
        headers={"X-CSRF-Token": "forged"},
        json={"role": "viewer"},
    )
    assert blocked.status_code == 403
