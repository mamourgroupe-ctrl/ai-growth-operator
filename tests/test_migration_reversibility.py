"""Phase 1 remediation (#29): full upgrade/downgrade/upgrade cycle on empty Postgres."""

import secrets
import tempfile

import pgserver
from alembic import command
from alembic.config import Config
from app.config import get_settings
from sqlalchemy import create_engine, text

DOMAIN_TABLES = {
    "users",
    "sessions",
    "tenants",
    "tenant_memberships",
    "ai_generation_jobs",
    "outbox_events",
    "audit_logs",
}


def _snapshot(admin_url: str) -> dict[str, set[str]]:
    engine = create_engine(admin_url, future=True)
    try:
        with engine.connect() as connection:
            tables = (
                set(connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).scalars())
                & DOMAIN_TABLES
            )
            indexes = {
                f"{row.tablename}.{row.indexname}"
                for row in connection.execute(
                    text("SELECT tablename, indexname FROM pg_indexes WHERE schemaname='public'")
                )
                if row.tablename in DOMAIN_TABLES
            }
            constraints = {
                f"{row.table_name}.{row.constraint_name}:{row.constraint_type}"
                for row in connection.execute(
                    text(
                        "SELECT table_name, constraint_name, constraint_type "
                        "FROM information_schema.table_constraints WHERE table_schema='public'"
                    )
                )
                if row.table_name in DOMAIN_TABLES and not row.constraint_name.endswith("_not_null")
            }
            policies = {
                f"{row.tablename}.{row.policyname}:{row.qual}:{row.with_check}"
                for row in connection.execute(
                    text("SELECT tablename, policyname, qual, with_check FROM pg_policies WHERE schemaname='public'")
                )
                if row.tablename in DOMAIN_TABLES
            }
            rls = {
                f"{row.relname}:{row.relrowsecurity}:{row.relforcerowsecurity}"
                for row in connection.execute(
                    text(
                        "SELECT relname, relrowsecurity, relforcerowsecurity "
                        "FROM pg_class WHERE relnamespace='public'::regnamespace AND relkind='r'"
                    )
                )
                if row.relname in DOMAIN_TABLES
            }
        return {"tables": tables, "indexes": indexes, "constraints": constraints, "policies": policies, "rls": rls}
    finally:
        engine.dispose()


def test_upgrade_downgrade_upgrade_preserves_schema(monkeypatch) -> None:
    server = pgserver.get_server(tempfile.mkdtemp(prefix="ago-reversibility-pg-"))
    admin_url = server.get_uri()
    role = "ago_app"
    password = secrets.token_urlsafe(24)
    with create_engine(admin_url, future=True).begin() as connection:
        connection.exec_driver_sql(f"CREATE ROLE {role} LOGIN PASSWORD '{password}' NOSUPERUSER NOBYPASSRLS")

    monkeypatch.setenv("AGO_DATABASE_URL", admin_url)
    monkeypatch.setenv("AGO_APP_DATABASE_URL", admin_url)
    monkeypatch.setenv("AGO_APP_ROLE", role)
    get_settings.cache_clear()

    config = Config("alembic.ini")
    try:
        command.upgrade(config, "head")
        with create_engine(admin_url, future=True).connect() as connection:
            head = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        assert head == "0002_audit_log_tenant_fk"
        before = _snapshot(admin_url)
        assert before["tables"] == DOMAIN_TABLES
        assert len(before["policies"]) == 5
        enabled_rls = {row.split(":", 1)[0] for row in before["rls"] if row.endswith(":True:True")}
        assert len(enabled_rls) == 5

        command.downgrade(config, "base")
        with create_engine(admin_url, future=True).connect() as connection:
            remaining = set(
                connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).scalars()
            )
            version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        assert remaining & DOMAIN_TABLES == set()
        assert version is None

        command.upgrade(config, "head")
        after = _snapshot(admin_url)
        assert after == before
    finally:
        get_settings.cache_clear()
        server.cleanup()
