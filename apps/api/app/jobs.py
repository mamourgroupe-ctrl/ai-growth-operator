import uuid
from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .db import set_tenant_context
from .models import GenerationJob


def enqueue_job(
    db: Session,
    *,
    tenant_id: uuid.UUID,
    requested_by: uuid.UUID | None,
    capability: str,
    kind: str,
    locale: str,
    style: str,
    prompt: str,
    idempotency_key: str,
) -> GenerationJob:
    job = GenerationJob(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        requested_by=requested_by,
        capability=capability,
        kind=kind,
        locale=locale,
        style=style,
        prompt=prompt,
        idempotency_key=idempotency_key,
        status="queued",
        attempt_count=0,
        max_attempts=3,
    )
    db.add(job)
    db.commit()
    set_tenant_context(db, str(tenant_id), str(requested_by) if requested_by else None)
    db.refresh(job)
    return job


def claim_next_job(db: Session, worker_id: str) -> GenerationJob | None:
    """Atomically claim one due job without blocking on rows held by other workers."""
    now = datetime.now(UTC)
    stmt = (
        select(GenerationJob)
        .where(GenerationJob.status == "queued")
        .where(or_(GenerationJob.run_at.is_(None), GenerationJob.run_at <= now))
        .order_by(GenerationJob.created_at, GenerationJob.id)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    job = db.scalar(stmt)
    if job is None:
        db.rollback()
        return None
    job.status = "running"
    job.locked_by = worker_id
    job.locked_at = now
    job.heartbeat_at = now
    job.attempt_count += 1
    claimed_tenant = str(job.tenant_id)
    db.commit()
    set_tenant_context(db, claimed_tenant)
    db.refresh(job)
    return job
