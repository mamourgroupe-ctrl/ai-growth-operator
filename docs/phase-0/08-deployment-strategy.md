# Phase 0 — Deployment Strategy (final acceptance draft)

**Status:** Corrected for final approval. No infrastructure created in Phase 0.

## 1. Environments

Local (`docker compose`, synthetic) → CI ephemeral (PR) → Staging (merge to `main` after review) → Production (explicit approved deploy/tag). No direct push to `main`, no auto-merge, PR #15 remains draft and unmerged.

## 2. Pipeline

PR checks (lint, typecheck, unit, integration, security, contract) → build/scan SHA-tagged image → reviewer approval → merge to `main` → staging deploy + smoke (Arabic UI, owner approval gate, outbox replay test) → production by explicit GitHub Environment approval.

## 3. Database migrations

Alembic pre-deploy; migration role bypasses RLS explicitly. Expand-then-contract; tested downgrade. Baseline includes system + MVP tables; deferred ad/social tables excluded. `fx_rate_snapshots` and `approval_snapshots` are insert-only. Backup before large-table migration.

## 4. Configuration and secrets

Provider keys, FX source credentials (once source is selected), DB credentials only in GitHub Environments/host secret manager. `ai_provider_configs`/`ai_models` are data rows, not secrets. **FX rate source and rounding remain an unresolved configuration decision**; no live rate is assumed. Required production reviewer; rotate on exposure; `.env.example` only.

## 5. Runtime jobs

- API: tenant context, owner-only approval, outbox insertion in same transaction.
- Worker: AI jobs + outbox dispatcher; concurrency 2 initially.
- Reconciliation job: resolves `uncertain` external actions, daily ledger check, audit append; alerts on unmatched effects.
- No social publisher or ad executor deployed in MVP (routes return `501`).

## 6. Observability

`/healthz`, `/readyz`; structured redacted logs with org/request IDs. Alerts: 5xx, approval-gate blocks, outbox backlog/age, uncertain actions, dead letters, provider cost anomalies, FX snapshot staleness. Full APM deferred.

## 7. Backups and rollback

Daily encrypted backups, 7-day PITR, restore drill before pilot and quarterly. Proposed RPO ≤24h / RTO ≤4h pending confirmation. Rollback = previous image tag + forward-only migration; no blind DB downgrade under load.

## 8. Scale/cost

Per-tenant quotas, provider caps, queue threshold monitoring; revisit Redis/Celery at >100 jobs/min or >10k backlog (ADR-012). Host: generic container host + managed PostgreSQL; final selection requires approval.
