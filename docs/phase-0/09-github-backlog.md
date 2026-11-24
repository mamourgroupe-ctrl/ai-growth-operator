# Phase 0 — GitHub Development Backlog (post-audit)

**Status:** Corrected backlog in `mamourgroupe-ctrl/ai-growth-operator`.
**Rule:** No implementation issue starts until #1 is closed by explicit product-owner approval of the corrected Phase 0 docs. PR #15 stays draft; no merge without review.

## Gate

| Issue | Title | Depends on |
|---|---|---|
| [#1](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/1) | [Audit] Confirm corrected PRD and close approval gate | — |

Closes when Arabic-first/Darija, DZD+USD, approval model, responsive web MVP, and Android deferral are explicitly approved.

## Phase 1 — Foundation

| Issue | Title | Depends on |
|---|---|---|
| [#2](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/2) | Bootstrap repo tooling and CI | #1 |
| [#14](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/14) | Enable branch protection and required checks | #2 |
| [#3](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/3) | Add Alembic baseline and RLS policies | #1, #2 |
| [#6](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/6) | Publish OpenAPI contract and error format | #2 |
| [#4](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/4) | Implement auth, sessions, and CSRF | #2, #3 |
| [#5](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/5) | Implement tenant membership and RBAC | #4 |
| [#7](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/7) | Add tenant-isolation and approval security tests | #3, #5 |

**Exit:** register → create organization → RLS denial test passes → CI green.

## Phase 2 — Business core + AI Studio

| Issue | Title | Depends on |
|---|---|---|
| [#16](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/16) | Business profile and brand assets | #3, #5 |
| [#17](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/17) | Product catalog | #3, #5 |
| [#9](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/9) | Provider-independent AI gateway | #3, #6 |
| [#18](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/18) | AI model config, usage, and cost tracking | #9 |
| [#8](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/8) | Content studio APIs | #5, #6 |
| [#19](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/19) | Creative assets and content calendar | #8, #9 |
| [#20](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/20) | Harden Postgres job queue | #3, #9 |
| [#21](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/21) | AI usage limits from subscriptions | #9 |
| [#22](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/22) | FX snapshots and dual DZD/USD display | #3 |

**Exit:** Arabic/Darija copy + creative generated, tracked, limited, displayed in both currencies.

## Phase 3 — Approval center + web MVP

| Issue | Title | Depends on |
|---|---|---|
| [#23](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/23) | Approval center and fail-closed action gate | #7, #22 |
| [#24](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/24) | Basic landing pages and leads | #3, #5, #23 |
| [#12](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/12) | Responsive web MVP screens and navigation | Phase 2, #23, #24 |
| [#25](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/25) | Arabic RTL and dual-currency UI layer | #12, #22 |
| [#13](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/13) | Staging/production deployment and backups | #2, #14 |

**Exit:** no external publish without approval; Arabic-first pilot workflow verified.

## Explicitly deferred — no issue scheduled

Android app; complex CRM; advanced automated campaign optimization; multi-platform advertising automation; advanced analytics; billing; direct social publishing. Ad/social tables are documented but not activated.

## Backlog hygiene

- One issue = one reviewable outcome with acceptance criteria.
- New scope requires a PRD decision and a new issue.
- Issues are not auto-closed by merges.
- #10 (usage/rate-limit/audit log) and #11 (basic usage/metrics view) remain Phase 2 support items alongside the table above.
