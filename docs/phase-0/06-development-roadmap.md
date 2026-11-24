# Phase 0 — Development Roadmap (post-audit)

**Status:** Corrected for approval. No phase beyond Phase 0 is authorized.

## Phase 0 — Planning (current)

Deliverables: corrected PRD, architecture audit, database, API, security, testing, deployment, backlog, ADR log.
Exit: explicit product-owner approval of corrections. No code written.

## Gate — Product-owner approval

Confirm corrected PRD decisions: Arabic-first + Darija, DZD+USD display, human approval model, responsive web MVP, Android deferred. Close issue #1 with approval evidence.

## Phase 1 — Foundation (2–3 weeks, after approval)

- Repo tooling, CI, branch protection (#2, #14).
- Alembic baseline: system tables + MVP tenant tables + RLS (#3).
- Auth, sessions, CSRF (#4).
- Organization membership and RBAC (#5).
- OpenAPI contract and error format (#6).
- Tenant-isolation security suite (#7).

**Exit:** register → create organization → RLS denial test passes → CI green.

## Phase 2 — Business core + AI Studio (3–4 weeks)

- Business profile + brand assets (#16).
- Product catalog (#17).
- AI Gateway with text + image providers, model config, usage/cost records (#18).
- Content items, creative assets, content calendar view (#19).
- Job queue hardening: retry/backoff/scheduling/idempotency/dead-letter/monitoring (#20).
- Subscriptions lite, usage counters, AI limits (#21).
- FX snapshots + dual DZD/USD display (#22).

**Exit:** Arabic/Darija copy and creative can be generated, tracked, limited, and displayed in both currencies.

## Phase 3 — Approval center + web MVP (3–4 weeks)

- Approval requests, immutable snapshots, external-action gate, budget validation (#23).
- Landing pages + leads (#24).
- Responsive Arabic-first web app: studio, calendar, approval center, landing pages, leads (#25).
- Publishing approval flow tested end-to-end.

**Exit:** no external publish without approval; pilot user can review and approve in Arabic.

## Phase 4 — Pilot readiness

- Staging/production deployment, backups, restore drill (#13).
- Playwright smoke, provider cost alerts, monitoring dashboards.
- Pilot with 3–5 Algerian small businesses.

## Explicitly deferred (not scheduled)

Android app; complex CRM; advanced automated campaign optimization; multi-platform ad automation; advanced analytics; billing; direct social publishing. Ad tables documented but not activated until a new approved phase.

## Sequencing rules

1. Approval gate before any implementation.
2. Schema before endpoints; approval gate before any external action.
3. Security tests land in Phase 1, not later.
4. PRs to `main` only after review; no merge without approval.
5. New scope requires a new PRD decision and backlog issue.
