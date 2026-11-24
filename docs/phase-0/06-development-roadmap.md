# Phase 0 — Development Roadmap

**Status:** Proposed sequencing for approval. Dates are relative durations, not committed deadlines.

## 0. Phase 0 — Planning (current)

**Deliverables:** PRD review, architecture, DB design, API spec, security architecture, roadmap, testing strategy, deployment strategy, GitHub backlog, decision log.
**Exit criterion:** user approval of Phase 0 and confirmation of the PRD gaps in `01-prd-review.md`.
**Constraint:** no application code.

## 0.5 PRD confirmation gate (blocking)

**Work:** supply canonical PRD or written answers to the 10 open questions.
**Exit criterion:** review document updated from conditional to confirmed.

## 1. Phase 1 — Foundation (estimated 2–3 weeks)

- Repo structure, Python/Next.js tooling, Alembic baseline, CI checks.
- Auth: register, login, logout, session handling, CSRF.
- Tenant model, memberships, RLS enforcement, role checks.
- OpenAPI contract, error format, health endpoints.
- Test harness with ephemeral Postgres and fake LLM adapter.
- Branch protection and required checks on `main`.

**Exit criterion:** a test can register a user, create a tenant, and prove cross-tenant reads fail; CI is green; no app secrets in repo.

## 2. Phase 2 — Core MVP backend (estimated 3–4 weeks)

- Campaign CRUD and content item CRUD.
- AI generation job worker with single provider adapter.
- Quotas and rate limiting.
- Manual metrics import and summary endpoint.
- Audit logging for mutations.

**Exit criterion:** end-to-end API flow produces an approved draft from a brief and shows a metrics summary.

## 3. Phase 3 — Dashboard and pilot readiness (estimated 2–3 weeks)

- Minimal Next.js dashboard: login, workspace, campaigns, drafts, job status, metrics summary.
- Invite flow (email provider decision required).
- Staging deployment, restore drill, basic error reporting.
- Playwright smoke tests and light load test.

**Exit criterion:** 3–5 pilot businesses can use the workflow with observed support load.

## 4. Phase 4 — Post-pilot candidates (not committed)

- Direct publishing integrations, Arabic/Darija UI, billing, advanced analytics, provider failover.
- Each item requires its own PRD decision and phase approval.

## Dependencies and sequencing rules

1. PRD confirmation gates all implementation.
2. DB migrations land before endpoints that depend on them.
3. Security tests for tenant isolation land in Phase 1, not later.
4. No merge to `main` without review and passing checks.
5. No phase starts without explicit approval.
