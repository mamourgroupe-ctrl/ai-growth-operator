# Phase 0 — GitHub Development Backlog (final acceptance draft)

**Status:** Corrected backlog in `mamourgroupe-ctrl/ai-growth-operator`.
**Rule:** No implementation issue starts until #1 is closed by explicit product-owner approval. PR #15 stays draft; no merge without review.

## Gate

| Issue | Title | Depends on |
|---|---|---|
| [#1](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/1) | [Audit] Confirm corrected PRD and close approval gate | — |

Closes when Arabic default + Darija style + human review, DZD/USD with unresolved FX source, owner-only approval, outbox/reconciliation, responsive web MVP, Android deferral, and social/ad deferral are explicitly approved.

## Phase 1 — Foundation

| Issue | Title | Depends on |
|---|---|---|
| [#2](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/2) | Bootstrap repo tooling and CI | #1 |
| [#14](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/14) | Enable branch protection and required checks | #2 |
| [#3](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/3) | Add Alembic baseline and RLS policies | #1, #2 |
| [#6](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/6) | Publish OpenAPI contract and error format | #2 |
| [#4](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/4) | Implement auth, sessions, and CSRF | #2, #3 |
| [#5](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/5) | Implement owner-only RBAC and membership | #4 |
| [#7](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/7) | Add tenant isolation and approval-bypass tests | #3, #5 |

## Phase 2 — Business core + AI Studio

| Issue | Title | Depends on |
|---|---|---|
| [#16](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/16) | Business profile and brand assets | #3, #5 |
| [#17](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/17) | Product catalog | #3, #5 |
| [#9](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/9) | Provider-independent AI gateway | #3, #6 |
| [#18](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/18) | AI model config, usage, and cost tracking | #9 |
| [#8](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/8) | Content studio APIs | #5, #6 |
| [#27](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/27) | Human Arabic quality review | #5, #8 |
| [#19](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/19) | Creative assets and content calendar | #8, #9 |
| [#20](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/20) | Harden Postgres job queue | #3, #9 |
| [#21](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/21) | AI usage limits from subscriptions | #9 |
| [#22](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/22) | Immutable FX snapshots and dual display | #3 |

## Phase 3 — Approval + web MVP

| Issue | Title | Depends on |
|---|---|---|
| [#23](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/23) | Owner-only approval center and fail-closed gate | #7, #22, #27 |
| [#26](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/26) | Transactional outbox, idempotency, and reconciliation | #3, #7, #23 |
| [#24](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/24) | Basic landing pages and leads | #3, #5, #23 |
| [#12](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/12) | Responsive web MVP screens and navigation | Phase 2, #23, #24 |
| [#25](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/25) | Arabic RTL, Darija style, dual-currency UI | #12, #22, #27 |
| [#13](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/13) | Staging/production deployment and backups | #2, #14 |

## Deferred — no issue scheduled

Android; complex CRM; advanced optimization; multi-platform ad automation; paid ad execution; direct social publishing; advanced analytics; billing. Extension points are documented but not activated.

## Support items

#10 (usage/rate-limit/audit logging) and #11 (basic usage/metrics view) remain Phase 2 support issues.

## Hygiene

One reviewable outcome per issue; no auto-close on merge; new scope requires PRD decision + new issue.
