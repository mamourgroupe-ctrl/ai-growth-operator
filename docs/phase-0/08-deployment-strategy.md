# Phase 0 — Deployment Strategy

**Status:** Proposed for approval. No infrastructure is created in Phase 0.

## 1. Environments

| Environment | Trigger | Data | Access |
|---|---|---|---|
| Local | `docker compose` | Synthetic | Developer |
| CI ephemeral | Pull request | Synthetic | CI only |
| Staging | Merge to `main` after review | Anonymized/synthetic | Team |
| Production | Explicit approved deploy/tag | Real pilot data | Restricted |

No direct push to `main`; no auto-merge; no automatic production promotion from a merge.

## 2. Pipeline outline

1. PR opened from Arena-managed branch → lint, typecheck, unit, integration, security, contract tests.
2. Build container image, scan dependencies, publish to registry with SHA tag.
3. Reviewer approves; checks pass; PR merges to `main`.
4. Staging deploy uses the merge SHA; smoke tests run.
5. Production deploy is a separate manually approved action in GitHub Environments.

## 3. Database migrations

- Alembic runs as a pre-deploy step with a dedicated migration role.
- Expand-then-contract: add nullable/backward-compatible structures first, remove old ones in a later release.
- Every migration has a tested downgrade path.
- Backups are taken immediately before a migration that touches large tables.
- Rollback = redeploy previous image tag plus forward-only migration if schema already changed; never blind DB downgrade under load.

## 4. Secrets and configuration

- All secrets live in GitHub Environments (staging/production) or the host's secret manager.
- Required reviewer on production environment.
- Config is read from environment variables; no `.env` files committed (only `.env.example`).
- Rotate provider and DB credentials on schedule and immediately after suspected exposure.

## 5. Availability and observability

- Health endpoints: `/healthz` (process) and `/readyz` (DB + worker).
- Structured JSON logs with request ID, tenant ID (non-sensitive), and no secret values.
- Basic error reporting added in Phase 3; full APM is not a Phase 1 dependency.
- Alerts on 5xx rate, job failure rate, DB connections, and provider cost anomalies.

## 6. Backups and recovery

- Daily automated backups with 7-day PITR for production.
- Restore drill before pilot and quarterly thereafter.
- Recovery objectives to be confirmed with PRD/business owner: proposed RPO ≤ 24h, RTO ≤ 4h.

## 7. Cost controls

- Per-tenant generation quota enforced in API and DB counter.
- Provider timeout, max tokens, and monthly budget alert.
- Worker concurrency limited initially to 2.
- No always-on preview environments for every PR beyond CI lifetime.

## 8. Host decision

Default planning assumption: a container host with managed PostgreSQL (for example Fly.io/Render-class services) to avoid Kubernetes. Final host selection must be approved before Phase 3 deployment work.
