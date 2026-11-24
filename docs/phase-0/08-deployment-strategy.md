# Phase 0 — Deployment Strategy (post-audit)

**Status:** Corrected for approval. No infrastructure created in Phase 0.

## 1. Environments

| Environment | Trigger | Data | Access |
|---|---|---|---|
| Local | `docker compose` | Synthetic | Developer |
| CI ephemeral | Pull request | Synthetic | CI only |
| Staging | Merge to `main` after review | Anonymized/synthetic | Team |
| Production | Explicit approved deploy/tag | Pilot data | Restricted |

No direct push to `main`; no auto-merge; no automatic production promotion. PR #15 stays draft and unmerged.

## 2. Pipeline

1. PR → lint, typecheck, unit, integration, security, contract tests.
2. Build/scan container image, tag with commit SHA.
3. Reviewer approves; checks pass; merge to `main`.
4. Staging deploy from merge SHA + smoke tests (Arabic UI, approval gate).
5. Production deploy requires explicit GitHub Environment approval.

## 3. Database migrations

- Alembic pre-deploy step; admin/migration role bypasses RLS explicitly.
- Expand-then-contract; tested downgrade; deferred ad tables excluded from baseline.
- RLS policies created with tables in the same migration.
- Backup before large-table migrations.

## 4. Secrets and provider config

- Provider API keys, FX source credentials, and DB credentials only in GitHub Environments/host secret manager.
- `ai_provider_configs`/`ai_models` are data rows, not secrets; keys remain external references.
- Required reviewer on production environment; rotate on exposure.
- No `.env` files committed; `.env.example` only.

## 5. Observability

- `/healthz`, `/readyz`; structured JSON logs with request/org IDs and redaction.
- Alerts: 5xx rate, approval-gate blocks, dead-letter jobs, provider cost anomalies, FX snapshot staleness.
- Full APM deferred.

## 6. Backups and recovery

- Daily encrypted backups, 7-day PITR; restore drill before pilot and quarterly.
- Proposed RPO ≤24h, RTO ≤4h pending business confirmation.
- Rollback: previous image tag + forward-only migration; no blind DB downgrade under load.

## 7. Cost and scale controls

- Per-tenant generation/image quotas; provider cost caps; queue threshold monitoring.
- Worker concurrency 2 initially; adaptive poll; revisit Redis/Celery at >100 jobs/min or >10k backlog (see ADR-012).

## 8. Host decision

Generic container host + managed PostgreSQL (Fly.io/Render-class). Final selection requires approval before Phase 4 deployment work.
