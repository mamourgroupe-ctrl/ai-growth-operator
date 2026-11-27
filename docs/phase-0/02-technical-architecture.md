# Phase 0 — Technical Architecture (final acceptance draft)

**Status:** Corrected for final approval. No implementation authorized.
**Principles:** Arabic-first, smallest sufficient system, tenant isolation, owner-only approval, fail-closed external effects.

## 1. System shape

```text
Responsive Web (Next.js, MVP, ar/RTL + fr)
        | HTTPS/JSON
        v
API (FastAPI) -- Organization/RBAC -- Approval center -- Outbox dispatcher
        |-- AI Gateway (TextProvider + ImageProvider)
        |-- Arabic quality review queue
        |-- Postgres job dispatcher --> Worker
        v
PostgreSQL 16 (RLS, fx_rate_snapshots, usage, outbox, audit)
        |
        v
Providers (one active initially; external publishing/ad execution deferred)
```

Deployables: web, API, worker, reconciliation job (can be part of worker initially).

## 2. Roles and bypass prevention

- **Owner:** only final approval authority; member/settings management.
- **Editor:** prepare content, request Arabic review, submit for approval; edit products/landing pages.
- **Viewer:** read-only.
- Enforcement is centralized in an authorization dependency used by every route. Approval decision routes check `role='owner'` server-side; client UI hiding is not a control. Direct calls to publish/execute endpoints with a forged `approval_id`, non-owner role, or wrong `tenant_id` are rejected before any outbox row or provider call. RLS adds a second isolation boundary.

## 3. AI Gateway

`TextProvider` + `ImageProvider` protocols; `ai_provider_configs`/`ai_models` hold capability, enabled flag, priority/fallback, residency tag, unit price, rate limits, `supports_darija`. Usage/cost recorded in `ai_usage_records`. Timeouts, bounded retries, circuit breaker, policy-gated fallback. One provider active initially; no client-selectable provider URLs.

## 4. Arabic pipeline

1. Generation job carries `style`: `msa` (`ar`), `darija` (`ar-DZ`), `fr`.
2. `ar`/`ar-DZ` output enters `arabic_reviews` pending human check.
3. Designated editor reviewer approves or requests changes with notes.
4. Editor submits reviewed content as an `approval_requests` row.
5. Owner decides. Only then can a publish/execute outbox event be created.

## 5. Approval + financial execution safety

### 5.1 Approval gate
Approvals are versioned and snapshot-hashed; edits supersede prior approvals. No in-place change to approved data. Owner decides; editor cannot decide.

### 5.2 Transactional outbox
In the **same DB transaction** that records an authorized external action, insert an `outbox_events` row (`aggregate_type='external_action'`, payload = action ID + approval ID + idempotency key). A dispatcher publishes due events to the executor. This avoids "approval committed but action lost" and avoids dual-write inconsistency. No external call is made before the outbox row is committed.

### 5.3 Idempotency
- Client `Idempotency-Key` on approval creation and action requests; `UNIQUE (tenant_id, idempotency_key)`.
- Each `external_actions` row stores a deterministic `provider_idempotency_key` derived from its own ID and approval version. **Retries reuse the same key**; never regenerate.
- Provider reference stored once outcome is known. Replaying an event with the same action ID is a no-op, not a new side effect.

### 5.4 External execution state machine

```text
created -> authorized -> queued(outbox) -> dispatching -> executed
                                      \-> uncertain -> reconciled_executed
                                                   \-> reconciled_failed
                                      \-> failed -> dead_letter
blocked / cancelled reachable from authorized before dispatch
```

`uncertain` is entered on timeout/network ambiguity **after** a provider call attempt. Automatic retry is forbidden from `uncertain`; only reconciliation can resolve it.

### 5.5 Reconciliation
- Scheduled reconciliation reads provider by `provider_idempotency_key`/`provider_ref`.
- Resolves `uncertain` to `reconciled_executed` or `reconciled_failed`; writes audit evidence.
- Daily ledger check compares `external_actions`, provider records, and (when enabled) `spend_events`/budget counters.
- Duplicate or unexplained external effects raise an incident; tenant execution is frozen until resolved.
- All reconciliation actions are append-only and auditable.

## 6. PostgreSQL job queue (ADR-012)

`FOR UPDATE SKIP LOCKED`, lease (`locked_by`, `locked_at`, `heartbeat_at`), `run_at`, `attempt_count`/`max_attempts`, exponential backoff with full jitter, idempotency, dead-letter, monitoring, concurrency 2. Revisit Redis+Celery at sustained >100 jobs/min or >10k backlog via stable `JobDispatcher` + outbox + shadow run.

## 7. Multi-tenancy, locale, currency

- Shared schema; every tenant-owned table has `tenant_id` + RLS (`USING`/`WITH CHECK`). System tables admin-only.
- UI `ar` default/RTL, `fr` secondary; content styles `ar` (MSA), `ar-DZ` (Darija), `fr`.
- Money stored as `numeric(14,2)` + currency, displayed as DZD + USD using **immutable `fx_rate_snapshots`**. FX source is an unresolved configuration decision.

## 8. Extension points kept outside MVP

`external_actions`, outbox, approval kinds (`ad_activation`, `ad_budget_change`, `social_publish`), `social_connections`, `ad_accounts`, `ad_campaigns`, `ad_budget_limits`, `spend_events`. They are documented, not implemented. When enabled later they must pass the same owner approval, exact ceiling, idempotency, outbox, and reconciliation rules.

## 9. Non-goals

Android, complex CRM, advanced optimization, multi-platform ad automation, advanced analytics, billing, per-tenant DBs, microservices, Redis in MVP, direct social publishing in MVP.

## 10. Cross-references

DB `03`, API `04`, security `05`, audit `11`, ADRs `10`, final report `12`.
