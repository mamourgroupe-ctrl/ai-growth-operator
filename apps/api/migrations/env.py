import os
import re

from alembic import context
from app.config import get_settings
from app.models import Base
from sqlalchemy import create_engine

config = context.config
target_metadata = Base.metadata


def _application_role() -> str:
    role = os.environ.get("AGO_APP_ROLE", "ago_app")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", role):
        raise ValueError("AGO_APP_ROLE contains invalid characters")
    return role


def run_migrations_online() -> None:
    url = get_settings().database_url.replace("%", "%%")
    config.set_main_option("sqlalchemy.url", url)
    connectable = create_engine(config.get_main_option("sqlalchemy.url"), future=True)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table="alembic_version",
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
        connection.exec_driver_sql(f"GRANT USAGE ON SCHEMA public TO {_application_role()}")


run_migrations_online()
