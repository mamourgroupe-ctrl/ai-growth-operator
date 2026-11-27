# Phase 0 — Architecture Decision Log (final acceptance draft)

Superseded/amended decisions remain for traceability; the latest status wins.

## ADR-001 — Single private repository / monorepo
**Accepted.** All work stays in `ai-growth-operator`.

## ADR-002 — Arena branch, PRs to `main`, no merge without review
**Accepted by user.** Develop on `arena/5dc98770-ai-growth-operator`; target `main`; never merge without approval.

## ADR-003 — Shared-schema multi-tenancy with RLS
**Accepted, extended.** Every tenant-owned entity has `tenant_id` + RLS `USING`/`WITH CHECK`; app membership/role checks remain mandatory. System tables admin-only.

## ADR-004 — FastAPI backend, responsive Next.js web
**Accepted, corrected.** Web is MVP, not deferred.

## ADR-005 — Postgres-backed job queue
**Amended by ADR-012.** No Redis for MVP.

## ADR-006 — Argon2id sessions with CSRF
**Accepted.** Managed IdP only if PRD later requires SSO/MFA.

## ADR-007 — Single provider adapter
**Superseded by ADR-013.** A gateway replaces the narrow adapter.

## ADR-008 — Deferred billing and Android
**Accepted, clarified.** Billing and Android deferred; direct social publishing and paid ad execution also deferred (see ADR-016). Web is not deferred.

## ADR-009 — French-first data model
**Superseded by ADR-011.** Kept only as traceability of the corrected assumption.

## ADR-010 — Documentation-only Phase 0
**Accepted.** No application code in Phase 0.

## ADR-011 — Arabic-first product with Darija style
**Accepted, refined by ADR-019.** UI default `ar` (MSA/RTL), `fr` secondary; content styles `msa` (`ar`), `darija` (`ar-DZ`), `fr`. Supersedes ADR-009.

## ADR-012 — Hardened Postgres queue + Celery migration path
**Accepted.** `FOR UPDATE SKIP LOCKED`, leases, `run_at`, bounded retries/backoff+jitter, idempotency, dead-letter, monitoring, concurrency 2. Migration via stable `JobDispatcher`, outbox, shadow run. Redis not added for complexity.

## ADR-013 — Provider-independent AI gateway
**Accepted.** `TextProvider`/`ImageProvider`, config-driven models/prices/fallback/residency, usage/cost tracking, rate limits, circuit breaker, policy-gated fallback.

## ADR-014 — Fail-closed approval and financial safety
**Accepted, extended by ADR-017.** Versioned approvals, immutable snapshots, exact ceiling + FX snapshot, no automatic increases, no external effect on validation failure.

## ADR-015 — Dual currency with immutable FX snapshots
**Accepted, amended.** DZD base, DZD+USD display from **immutable `fx_rate_snapshots`**; clients cannot submit rates. **FX source and rounding are an unresolved configuration decision**, not a selected vendor. Approvals store native ceiling, USD display, snapshot ID.

## ADR-016 — Corrected MVP scope
**Accepted, clarified.** MVP includes auth, organization, business profile, products, AI Studio, Arabic/Darija copy, human Arabic review, creatives, calendar, approval center, landing pages, leads, usage limits, responsive web, dual currency. **Direct social publishing and paid ad execution are outside MVP implementation**; extension points (`external_actions`, outbox, ad/social tables, approval kinds) and safety requirements are preserved. Android, CRM, advanced optimization/analytics, billing deferred.

## ADR-017 — Transactional outbox, external state machine, reconciliation
**Accepted.** Action authorization and outbox event commit in one transaction; deterministic provider idempotency key reused on retry; state machine includes `uncertain` with automatic retry forbidden; reconciliation resolves uncertain results by provider idempotency key/reference, detects duplicates, freezes tenant execution on unexplained effects, and appends audit evidence. Prevents duplicate publishing/spending on ambiguous external results.

## ADR-018 — Owner-only final approval authority
**Accepted.** Owner is the only role that can decide approvals. Editors prepare/submit; viewers read-only. Server-side role check on `/approvals/{id}/decide` and independent re-validation in execution handlers prevent API bypass. Arabic reviewer is an editor capability flag, never an approval authority.

## ADR-019 — Arabic quality human review
**Accepted.** `ar` (MSA) default UI/content locale; `ar-DZ` Darija distinct style; `fr` secondary. `ar`/`ar-DZ` drafts require an `arabic_reviews` approval by a flagged editor reviewer (grammar, Darija authenticity, brand voice, cultural fit, factual claims) before owner approval. Refines ADR-011.
