# Phase 0 — Architecture Decision Log (post-audit)

Superseded decisions remain for traceability; a superseding ADR always wins.

## ADR-001 — Single private repository / monorepo
**Status:** Accepted. Context: shared contracts. Decision: all work in `ai-growth-operator`. Consequence: simple CI; larger repo later.

## ADR-002 — Arena branch, PRs to `main`, no merge without review
**Status:** Accepted by user. Decision: develop on `arena/5dc98770-ai-growth-operator`; target `main`; never merge without approval.

## ADR-003 — Shared-schema multi-tenancy with RLS
**Status:** Accepted, extended. Decision: every tenant-owned entity carries `tenant_id` and RLS with `USING`/`WITH CHECK`; app checks remain mandatory. System tables (users, FX, provider config) are admin-only.

## ADR-004 — FastAPI backend, responsive Next.js web
**Status:** Accepted, corrected. Web is an **MVP** deliverable, not Phase 3-only. API/worker Python; web TypeScript.

## ADR-005 — Postgres-backed job queue
**Status:** Amended by ADR-012. Original decision retained (no Redis for MVP), with mandatory hardening.

## ADR-006 — Argon2id sessions with CSRF
**Status:** Accepted. Revisit managed IdP only if PRD requires SSO/MFA.

## ADR-007 — Single provider adapter
**Status:** Superseded by ADR-013. A single active provider is allowed, but the design is now a gateway, not a one-provider adapter.

## ADR-008 — Deferred billing, direct publishing, Android
**Status:** Accepted, clarified. Billing, direct social publishing, and Android deferred. Responsive web is **not** deferred.

## ADR-009 — French-first data model
**Status:** **Superseded by ADR-011.** Recorded only to show the corrected assumption.

## ADR-010 — Documentation-only Phase 0
**Status:** Accepted. No application code in Phase 0.

## ADR-011 — Arabic-first product with Darija support
**Status:** Accepted (audit correction). Context: approved product decision. Decision: UI default `ar`, `fr` secondary; copy locales `ar`, `ar-DZ`, `fr`; RTL-ready from first screen. Consequences: locale-aware prompts and tests; no French-only defaults. Supersedes ADR-009.

## ADR-012 — Hardened Postgres queue + defined Celery migration path
**Status:** Accepted (audit correction). Context: Redis not added for complexity. Decision: job table with `FOR UPDATE SKIP LOCKED`, leases, `run_at`, retries/backoff/jitter, idempotency, dead-letter, monitoring, concurrency 2. Migration: stable `JobDispatcher`, Celery+Redis behind it, outbox, shadow run. Consequences: low dependencies; measured scaling threshold required. Amends ADR-005.

## ADR-013 — Provider-independent AI gateway
**Status:** Accepted. Decision: `TextProvider` + `ImageProvider` protocols; `ai_provider_configs`/`ai_models` for model config, price, priority, fallback, residency; usage/cost records; rate limits; circuit breaker; policy-gated fallback. Consequences: no lock-in; more config surface but no provider-specific business columns. Supersedes ADR-007.

## ADR-014 — Fail-closed approval and financial safety
**Status:** Accepted. Decision: unified `approval_requests` + immutable `approval_snapshots` + `external_actions`/attempts; explicit approval for publish and ad activation; exact budget ceiling + FX snapshot; budget edits supersede approvals; no automatic increases; no external call on validation failure. Consequences: extra write path, strong auditability.

## ADR-015 — Dual currency display with FX snapshots
**Status:** Accepted. Decision: DZD base, DZD+USD display from `fx_rates` snapshots; approvals store native ceiling, USD display, snapshot ID; clients cannot submit rates. Consequences: FX source/rounding policy still open.

## ADR-016 — Corrected MVP scope and deferrals
**Status:** Accepted. Decision: MVP includes auth, organization, business profile, products, AI Studio, Arabic/Darija copy, creatives, calendar, approval center, basic landing pages, leads, usage limits, responsive web, dual currency. Deferred: Android, complex CRM, advanced optimization, multi-platform ads, advanced analytics, billing. Consequences: ad tables documented but not activated.
