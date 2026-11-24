# Phase 0 — Technical Architecture (post-audit)

**Status:** Corrected for product-owner review. No implementation authorized.
**Principles:** Arabic-first, smallest sufficient system, tenant isolation by design, fail-closed external actions, provider independence.

## 1. System shape

```text
Responsive Web (Next.js, MVP)
        | HTTPS / JSON, ar default + fr, DZD + USD display
        v
API (FastAPI, Python)
        |-- Organization/RBAC/approval services
        |-- AI Gateway (TextProvider + ImageProvider protocols)
        |-- Job dispatcher (Postgres queue) --> Worker
        v
PostgreSQL 16 (shared schema, RLS, FX snapshots, usage records)
        |
        v
LLM / image providers (one active initially, swappable)
```

Deployables: web, API, worker. Phase 1 may land API + worker first, but responsive web is an MVP deliverable, not a later phase.

## 2. Product modules → technical components

| Module | Components |
|---|---|
| Authentication | sessions, CSRF, Argon2id passwords |
| Organization management | `tenants` (UI: Organization), memberships, RBAC |
| Business profile | `business_profiles`, `brand_assets` (minimal) |
| Product catalog | `products` |
| AI Marketing Studio | `content_items`, `creative_assets`, `ai_generation_jobs`, AI Gateway |
| Content calendar | `content_items.scheduled_for` indexed calendar view |
| Approval center | `approval_requests`, `approval_snapshots`, `external_actions` |
| Landing pages & leads | `landing_pages`, `leads` |
| Usage limits | `subscriptions` (lite), `usage_counters`, `ai_usage_records` |
| Financial safety | `approval_requests` budget fields, FX snapshots, deferred budget tables |

## 3. AI Gateway

- `TextProvider` and `ImageProvider` protocols with normalized requests/responses.
- `ai_provider_configs` + `ai_models` define capabilities, enabled flags, priority/fallback order, unit prices, rate limits, residency tags.
- One provider may be active initially; no provider-specific fields in business tables.
- Usage/cost recorded per request in `ai_usage_records` with price snapshot.
- Failure handling: timeout → bounded retry with jitter → circuit breaker → configured fallback provider, all logged.
- Fallback is blocked when target provider violates residency or cost policy (fail closed).
- Rate limits: per tenant, per provider, per model; counters in Postgres for MVP.

## 4. Approval and external-action flow

1. User requests publish or ad activation → `approval_requests` (pending) + immutable `approval_snapshots`.
2. Approver reviews snapshot; decision sets status `approved`/`rejected`; approval records actor and timestamp.
3. Execution gate loads approval, checks `approved`, not expired, not superseded, version match, snapshot hash match.
4. For ad actions: lock budget row, validate `spent + requested <= ceiling` with FX snapshot, then create `external_actions` row.
5. Provider call happens only after all validations pass; every attempt written to `external_action_attempts` and `audit_logs`.
6. Any validation failure stops before the provider call (no spend, no publish).

Budget edits or content edits increment `target_version` and mark prior approvals `superseded`. No in-place edits to approved snapshots. No automatic budget increases.

## 5. PostgreSQL-backed job queue (accepted with hardening)

| Concern | Implementation |
|---|---|
| Concurrent claiming | `SELECT ... FOR UPDATE SKIP LOCKED` in short transaction |
| Lease | `locked_by`, `locked_at`, `heartbeat_at`, stale lease reclaim |
| Scheduling | `run_at timestamptz`, partial index on due queued jobs |
| Retries | `attempt_count`, `max_attempts=3`, `next_retry_at` |
| Backoff | `min(30s * 2^(attempt-1), 15m) + full jitter` |
| Idempotency | `UNIQUE (tenant_id, idempotency_key)`, provider request ID stored |
| Failure | `failed`/`dead_letter` terminal states, safe `last_error_code`, manual replay as new job |
| Monitoring | queue depth, oldest age, success/failure/retry rates, dead-letter count, stale locks, DB load |
| Concurrency | 2 workers initially, configurable; per-tenant fairness deferred |
| Limits | Partial indexes, adaptive polling, no large payloads in queue; revisit >100 jobs/min or >10k backlog |

**Trade-off:** transactional consistency with tenant data and no Redis dependency, at the cost of polling load and no broker-native semantics.

**Migration path:** keep `JobDispatcher` and job API stable; add Celery + Redis behind the same interface; use an outbox table to avoid dual-write loss; shadow-run before cutover. Redis is not added merely for complexity.

## 6. Multi-tenancy

Shared database/schema. Every tenant-owned table has `tenant_id` and RLS with `USING`/`WITH CHECK` on `current_setting('app.current_tenant_id')`. Application-level membership/role checks remain mandatory. `users`, `fx_rates`, `ai_provider_configs`, `ai_models` are system tables with admin-only access.

## 7. Localization and currency in the stack

- UI strings: `ar` default, `fr` secondary; RTL-safe layout from the first screen.
- Generated copy: `ar`, `ar-DZ`, `fr`; locale stored on every content item.
- Money: stored as `numeric(14,2)` + currency; rendered as DZD + USD using `fx_rates` snapshots.
- Approval ceilings store native amount, USD display amount, and FX snapshot ID.

## 8. Non-goals

Android, complex CRM, advanced campaign optimization, multi-platform ad automation, advanced analytics, billing, per-tenant databases, microservices, Kubernetes, Redis in MVP.

## 9. Cross-references

Database `03`, API `04`, security `05`, audit `11`, ADRs `10`.
