# Phase 0 — Architecture Decision Log

Each decision is reversible only by a new ADR that supersedes it.

---

## ADR-001 — Single private repository, monorepo layout
- **Status:** Accepted (Phase 0 proposal)
- **Context:** API, worker, web, and migrations share contracts; repo must stay isolated from other projects.
- **Decision:** Keep everything in `mamourgroupe-ctrl/ai-growth-operator`.
- **Consequences:** Simpler CI and versioning; larger repo later; no cross-repo coordination.

## ADR-002 — Arena-managed development branch, PRs to `main`
- **Status:** Accepted by user authorization
- **Context:** User approved temporary use of `arena/5dc98770-ai-growth-operator` while requiring isolation from `main`.
- **Decision:** Develop only on that branch; open PRs targeting `main`; never merge without review and approval.
- **Consequences:** Branch is temporary; final state must land via reviewed PR.

## ADR-003 — Shared-schema multi-tenancy with PostgreSQL RLS
- **Status:** Proposed
- **Context:** Need strong isolation without per-tenant DB overhead.
- **Decision:** `tenant_id` on all tenant tables plus RLS with `app.current_tenant_id`; application checks remain mandatory.
- **Consequences:** Strong defense in depth; requires disciplined transaction setup and RLS tests.

## ADR-004 — FastAPI backend, Next.js web client
- **Status:** Proposed
- **Context:** Need typed validation, generated OpenAPI, and a maintainable dashboard.
- **Decision:** Python/FastAPI for API + worker; TypeScript/Next.js for web in later phase.
- **Consequences:** Two runtimes, but standard and productive; no new framework experiments.

## ADR-005 — Postgres-backed job queue, no Redis/Kafka
- **Status:** Proposed
- **Context:** AI generation is asynchronous but volume is initially low.
- **Decision:** Use `ai_generation_jobs` with `FOR UPDATE SKIP LOCKED` and bounded concurrency.
- **Consequences:** Fewer dependencies; queue not suitable for high throughput, revisit after pilot.

## ADR-006 — Application-managed session auth with Argon2id
- **Status:** Proposed, revisit after PRD confirmation
- **Context:** Need secure auth without an external identity vendor dependency.
- **Decision:** Email/password, hashed with Argon2id, opaque sessions stored as hashes in Postgres, CSRF tokens on mutations.
- **Consequences:** Full control and no vendor lock; team owns session security; revisit if SSO/MFA becomes required.

## ADR-007 — One LLM provider behind a thin adapter
- **Status:** Proposed
- **Context:** Avoid provider abstraction overhead while preserving future flexibility.
- **Decision:** Define a small `ContentGenerator` protocol; implement one provider now; no user-facing provider selector.
- **Consequences:** Low complexity; provider switch requires a small code change.

## ADR-008 — Defer billing, publishing integrations, and mobile
- **Status:** Proposed
- **Context:** No confirmed PRD requirement and small initial scope.
- **Decision:** Keep `plan` as metadata; draft-only workflow; web only.
- **Consequences:** Faster pilot; monetization and channel expansion need future approval.

## ADR-009 — French-first, Arabic-ready data model
- **Status:** Proposed assumption (PRD confirmation required)
- **Context:** Algerian SMB context suggests French/Arabic usage; no confirmed locale list.
- **Decision:** Store `locale` on tenant and content; default `fr`; allow `ar`; do not build Darija UI yet.
- **Consequences:** Avoids destructive schema change later; actual locale set may change after PRD review.

## ADR-010 — Documentation-only Phase 0
- **Status:** Accepted
- **Context:** User explicitly forbade application implementation.
- **Decision:** Phase 0 changes are Markdown documentation only; no code, dependencies, or infra manifests.
- **Consequences:** No runnable product yet; Phase 1 begins only after approval.
