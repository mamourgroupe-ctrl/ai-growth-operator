from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings


def make_engine(url: str):
    return create_engine(url, pool_pre_ping=True, future=True)


def get_engine():
    # The API must never connect with the migration/superuser role: RLS would
    # be bypassed. The privileged URL is reserved for Alembic only.
    return make_engine(get_settings().app_database_url)


def get_sessionmaker():
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()


def set_tenant_context(db: Session, tenant_id: str | None = None, user_id: str | None = None) -> None:
    """Set request-local RLS context inside the current transaction."""
    db.execute(text("SELECT set_config('app.current_tenant_id', :value, true)"), {"value": tenant_id or ""})
    db.execute(text("SELECT set_config('app.current_user_id', :value, true)"), {"value": user_id or ""})
