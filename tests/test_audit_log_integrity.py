"""Phase 1 remediation (#30): audit_logs.tenant_id integrity and retention."""

import uuid

import pytest
from app.db import set_tenant_context
from app.models import AuditLog, Tenant, TenantMembership, User
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def _seed_tenant(db: Session, slug: str) -> tuple[uuid.UUID, uuid.UUID]:
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    set_tenant_context(db, str(tenant_id), str(user_id))
    db.add(User(id=user_id, email=f"{slug}@example.com", password_hash="test-hash", full_name=slug))
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


def test_audit_log_tenant_fk_blocks_unknown_tenant_and_hard_delete(app_db: Session, database) -> None:
    slug = f"audit-{uuid.uuid4().hex[:10]}"
    tenant_id, user_id = _seed_tenant(app_db, slug)

    set_tenant_context(app_db, str(tenant_id), str(user_id))
    app_db.add(AuditLog(tenant_id=tenant_id, action="test.audit_write", extra={"source": "test"}))
    app_db.commit()

    admin = create_engine(database.admin_url, future=True)
    try:
        with admin.begin() as connection:
            constraint = connection.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE conrelid = 'audit_logs'::regclass AND confrelid = 'tenants'::regclass"
                )
            ).scalar()
            assert constraint == "fk_audit_logs_tenant_id"

        with pytest.raises(IntegrityError):
            with admin.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO audit_logs (tenant_id, action, metadata) "
                        "VALUES (:tenant_id, 'test.unknown', '{}'::jsonb)"
                    ),
                    {"tenant_id": uuid.uuid4()},
                )

        # RESTRICT protects retained audit history from an accidental hard delete.
        with pytest.raises(IntegrityError):
            with admin.begin() as connection:
                connection.execute(text("DELETE FROM tenants WHERE id = :id"), {"id": tenant_id})

        with admin.begin() as connection:
            connection.execute(text("DELETE FROM audit_logs WHERE tenant_id = :id"), {"id": tenant_id})
            connection.execute(text("DELETE FROM tenants WHERE id = :id"), {"id": tenant_id})
    finally:
        admin.dispose()
