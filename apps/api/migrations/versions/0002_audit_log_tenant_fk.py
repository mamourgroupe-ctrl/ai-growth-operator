"""Add a retention-safe tenant FK to audit_logs.

Revision ID: 0002_audit_log_tenant_fk
Revises: 0001_initial
Create Date: 2026-11-24

Audit logs are kept for retention even when a tenant is retired. Tenants use
soft deletion (`deleted_at`), so a hard DELETE must be blocked while audit
history exists. ON DELETE RESTRICT enforces that without cascading away logs.
"""

from alembic import op

revision = "0002_audit_log_tenant_fk"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


CONSTRAINT = "fk_audit_logs_tenant_id"


def upgrade() -> None:
    op.create_foreign_key(
        CONSTRAINT,
        "audit_logs",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(CONSTRAINT, "audit_logs", type_="foreignkey")
