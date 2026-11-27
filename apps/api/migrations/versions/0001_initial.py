"""Initial Phase 1 schema: auth, organizations, RBAC, RLS, jobs, outbox.

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-24
"""

import os
import re

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def _role() -> str:
    role = os.environ.get("AGO_APP_ROLE", "ago_app")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", role):
        raise ValueError("AGO_APP_ROLE contains invalid characters")
    return role


def _rls(table: str, *, with_check: bool = True) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    using = "tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid"
    check = using
    if table == "tenants":
        using = (
            "id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid "
            "OR id IN (SELECT tenant_id FROM tenant_memberships "
            "WHERE user_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid)"
        )
    elif table == "tenant_memberships":
        using = (
            "tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid "
            "OR user_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid"
        )
    check = "id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid" if table == "tenants" else check
    op.execute(
        f"CREATE POLICY tenant_isolation ON {table} "
        f"USING ({using})" + (f" WITH CHECK ({check})" if with_check else "")
    )


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_users_email_lower", "users", [sa.text("lower(email)")], unique=True)

    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("base_currency", sa.String(3), nullable=False, server_default="DZD"),
        sa.Column("display_currencies", postgresql.JSONB(), nullable=False),
        sa.Column("default_ui_locale", sa.String(), nullable=False, server_default="ar"),
        sa.Column("supported_ui_locales", postgresql.JSONB(), nullable=False),
        sa.Column("default_content_style", sa.String(), nullable=False, server_default="msa"),
        sa.Column("timezone", sa.String(), nullable=False, server_default="Africa/Algiers"),
        sa.Column("plan_code", sa.String(), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("uq_tenants_slug_lower", "tenants", [sa.text("lower(slug)")], unique=True)

    op.create_table(
        "tenant_memberships",
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role", sa.String(), nullable=False, server_default="viewer"),
        sa.Column("is_arabic_reviewer", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('owner', 'editor', 'viewer')", name="ck_membership_role"),
    )
    op.create_index("ix_tenant_memberships_user_id", "tenant_memberships", ["user_id"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("csrf_token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("token_hash", name="uq_sessions_token_hash"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])

    op.create_table(
        "ai_generation_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("capability", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("locale", sa.String(), nullable=False, server_default="ar"),
        sa.Column("style", sa.String(), nullable=False, server_default="msa"),
        sa.Column("prompt", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="queued"),
        sa.Column("run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider", sa.String(), nullable=True),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("provider_request_id", sa.String(), nullable=True),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("result_ref", sa.String(), nullable=True),
        sa.Column("error_code", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_jobs_tenant_idempotency"),
        sa.CheckConstraint("attempt_count <= max_attempts", name="ck_jobs_attempts"),
    )
    op.create_index("ix_jobs_tenant_status_created", "ai_generation_jobs", ["tenant_id", "status", "created_at"])
    op.execute(
        "CREATE INDEX ix_jobs_queued ON ai_generation_jobs (created_at) WHERE status = 'queued'"
    )

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("aggregate_type", sa.String(), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("available_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_by", sa.String(), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "aggregate_id", "event_type", name="uq_outbox_aggregate_event"),
    )
    op.create_index("ix_outbox_tenant_status", "outbox_events", ["tenant_id", "status", "available_at"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target_type", sa.String(), nullable=True),
        sa.Column("target_id", sa.String(), nullable=True),
        sa.Column("approval_request_id", sa.Uuid(), nullable=True),
        sa.Column("external_action_id", sa.Uuid(), nullable=True),
        sa.Column("request_id", sa.String(), nullable=True),
        sa.Column("outbox_event_id", sa.Uuid(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_tenant_created", "audit_logs", ["tenant_id", "created_at"])

    for table in (
        "tenants",
        "tenant_memberships",
        "ai_generation_jobs",
        "outbox_events",
        "audit_logs",
    ):
        _rls(table)

    role = _role()
    op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {role}")
    op.execute(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {role}")


def _drop_rls(table: str) -> None:
    # The tenants policy has a subquery over tenant_memberships. Dropping that
    # table first fails with DependentObjectsStillExist unless policies are
    # removed before any table in the dependency graph.
    op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
    op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    for table in (
        "tenants",
        "tenant_memberships",
        "ai_generation_jobs",
        "outbox_events",
        "audit_logs",
    ):
        _drop_rls(table)

    for table in (
        "audit_logs",
        "outbox_events",
        "ai_generation_jobs",
        "sessions",
        "tenant_memberships",
        "tenants",
        "users",
    ):
        op.drop_table(table)
