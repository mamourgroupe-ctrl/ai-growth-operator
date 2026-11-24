# Phase 0 — Development Roadmap (final acceptance draft)

**Status:** Corrected for final approval. No phase beyond Phase 0 authorized.

## Phase 0 — Planning (current)

Deliverables: PRD, architecture audit, DB/API/security design, testing/deployment, backlog, ADRs, final report. Exit: explicit product-owner approval. No code.

## Gate — Product-owner approval

Confirm Arabic default + Darija style + human review, DZD/USD with unresolved FX source, owner-only approval, outbox/reconciliation safety, responsive web MVP, Android deferral, and external publishing/ads out of MVP. Close #1 with approval evidence.

## Phase 1 — Foundation (2–3 weeks after approval)

#2 tooling/CI → #14 branch protection → #3 baseline + RLS → #6 OpenAPI → #4 auth/CSRF → #5 RBAC (owner/editor/viewer) → #7 isolation + approval-bypass security tests.

**Exit:** register → organization → RLS denial + editor-cannot-approve test pass → CI green.

## Phase 2 — Business core + AI Studio (3–4 weeks)

#16 profile/brand, #17 products, #9 gateway, #18 model config/usage/cost, #8 content studio, #19 creatives/calendar, #20 hardened queue, #21 limits, #22 FX snapshots + dual display (source still config pending), #27 Arabic human review workflow.

**Exit:** `ar`/MSA and `ar-DZ` drafts are human-reviewed, generated, tracked, limited, displayed in both currencies.

## Phase 3 — Approval + web MVP (3–4 weeks)

#23 approval center (owner-only decisions) + fail-closed gate, #26 outbox/idempotency/state machine/reconciliation, #24 landing pages/leads, #12 web screens, #25 Arabic RTL + dual-currency UI, #13 staging/deploy/backups.

**Exit:** no external/internal publish without owner approval; ambiguous provider result never auto-retried; Arabic pilot workflow verified.

## Deferred (no issue scheduled)

Android; complex CRM; advanced campaign optimization; multi-platform ad automation; paid ad execution; direct social publishing; advanced analytics; billing. Extension points and safety contracts remain documented.

## Sequencing rules

1. Approval gate first.
2. Schema before endpoints; approval and outbox before any external effect.
3. Security tests in Phase 1, not later.
4. PRs to `main` only after review; no merge without approval.
5. New scope requires PRD decision + new issue.
