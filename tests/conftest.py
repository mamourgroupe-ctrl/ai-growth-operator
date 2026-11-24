import os
import secrets
import tempfile
from types import SimpleNamespace

import pgserver
import pytest
from alembic import command
from alembic.config import Config
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

APP_ROLE = "ago_app"


@pytest.fixture(scope="session")
def database() -> SimpleNamespace:
    pgdata = tempfile.mkdtemp(prefix="ago-phase1-pg-")
    server = pgserver.get_server(pgdata)
    admin_url = server.get_uri()
    password = secrets.token_urlsafe(24)

    admin_engine = create_engine(admin_url, future=True)
    with admin_engine.begin() as conn:
        conn.exec_driver_sql(
            f"CREATE ROLE {APP_ROLE} LOGIN PASSWORD '{password}' NOSUPERUSER NOBYPASSRLS"
        )

    app_url = make_url(admin_url).set(username=APP_ROLE, password=password).render_as_string(
        hide_password=False
    )
    os.environ["AGO_DATABASE_URL"] = admin_url
    os.environ["AGO_APP_DATABASE_URL"] = app_url
    os.environ["AGO_APP_ROLE"] = APP_ROLE
    os.environ["AGO_COOKIE_SECURE"] = "false"

    command.upgrade(Config("alembic.ini"), "head")

    yield SimpleNamespace(admin_url=admin_url, app_url=app_url, role=APP_ROLE, server=server)
    server.cleanup()


@pytest.fixture(scope="session")
def app_engine(database: SimpleNamespace):
    return create_engine(database.app_url, future=True, pool_pre_ping=True)


@pytest.fixture
def app_db(app_engine):
    with Session(app_engine, expire_on_commit=False, future=True) as session:
        yield session


def clear_rls_context(db: Session) -> None:
    db.execute(text("SELECT set_config('app.current_tenant_id', '', true)"))
    db.execute(text("SELECT set_config('app.current_user_id', '', true)"))


@pytest.fixture
def client(database: SimpleNamespace) -> TestClient:
    return TestClient(app)
