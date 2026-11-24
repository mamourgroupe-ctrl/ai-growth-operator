import json
import uuid

from app.db import set_tenant_context
from app.jobs import claim_next_job, enqueue_job
from app.models import Tenant, TenantMembership, User
from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.conftest import clear_rls_context


def _seed_tenant(db: Session, name: str, slug: str, email: str) -> tuple[uuid.UUID, uuid.UUID]:
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    set_tenant_context(db, str(tenant_id), str(user_id))
    db.add(User(id=user_id, email=email, password_hash="test-hash", full_name=name))
    db.flush()
    db.add(
        Tenant(
            id=tenant_id,
            name=name,
            slug=slug,
            display_currencies=json.loads('{"DZD": true, "USD": true}'),
            supported_ui_locales=json.loads('{"ar": true, "fr": true}'),
        )
    )
    db.flush()
    db.add(TenantMembership(tenant_id=tenant_id, user_id=user_id, role="owner"))
    db.commit()
    return tenant_id, user_id


def test_migration_created_tables(app_engine) -> None:
    with app_engine.connect() as connection:
        tables = set(connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).scalars())
    assert {
        "users",
        "sessions",
        "tenants",
        "tenant_memberships",
        "ai_generation_jobs",
        "outbox_events",
        "audit_logs",
    } <= tables


def test_rls_with_application_role(app_db: Session) -> None:
    tenant_a, user_a = _seed_tenant(app_db, "مخبز الجزائر", "bakerie-alger", "owner-a@example.test")
    tenant_b, user_b = _seed_tenant(app_db, "Boulangerie Oran", "boulangerie-oran", "owner-b@example.test")

    clear_rls_context(app_db)
    assert app_db.scalar(text("SELECT count(*) FROM tenants")) == 0

    set_tenant_context(app_db, str(tenant_a), str(user_a))
    assert app_db.scalars(text("SELECT id FROM tenants")).all() == [tenant_a]

    set_tenant_context(app_db, str(tenant_b), str(user_b))
    assert app_db.scalars(text("SELECT id FROM tenants")).all() == [tenant_b]

    set_tenant_context(app_db, str(tenant_a), str(user_a))
    assert app_db.scalar(text("SELECT count(*) FROM tenant_memberships WHERE user_id = :uid"), {"uid": user_b}) == 0


def test_job_claim_never_returns_same_job_twice(app_engine) -> None:
    with Session(app_engine, expire_on_commit=False, future=True) as setup:
        tenant_id, user_id = _seed_tenant(setup, "Studio A", "studio-a", "studio-a@example.test")
        set_tenant_context(setup, str(tenant_id), str(user_id))
        for index in range(2):
            set_tenant_context(setup, str(tenant_id), str(user_id))
            enqueue_job(
                setup,
                tenant_id=tenant_id,
                requested_by=user_id,
                capability="text",
                kind="social_post",
                locale="ar",
                style="darija",
                prompt=f"مسودة {index}",
                idempotency_key=f"key-{index}",
            )

    claimed = []
    for worker in ("worker-1", "worker-2"):
        with Session(app_engine, expire_on_commit=False, future=True) as db:
            set_tenant_context(db, str(tenant_id), str(user_id))
            job = claim_next_job(db, worker)
            assert job is not None
            assert job.status == "running"
            assert job.locked_by == worker
            claimed.append(job.id)

    assert len(set(claimed)) == 2
