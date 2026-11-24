# Phase 0 — GitHub Development Backlog

**Status:** Created as GitHub issues in `mamourgroupe-ctrl/ai-growth-operator`.
**Rule:** No issue is implementation-authorized until the PRD gate (#1) is closed and Phase 1 is explicitly approved.

## Gate

| Issue | Title | Depends on |
|---|---|---|
| [#1](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/1) | [Gate] Confirm canonical PRD and product decisions | — |

## Phase 1 — Foundation

| Issue | Title | Depends on |
|---|---|---|
| [#2](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/2) | Bootstrap repo tooling and CI | #1 |
| [#3](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/3) | Add Alembic baseline and RLS policies | #1, #2 |
| [#4](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/4) | Implement auth, sessions, and CSRF | #2, #3 |
| [#5](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/5) | Implement tenant membership and RBAC | #4 |
| [#6](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/6) | Publish OpenAPI contract and error format | #2 |
| [#7](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/7) | Add tenant-isolation security test suite | #3, #5 |
| [#14](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/14) | Enable branch protection and required checks | #2 |

**Phase 1 exit:** register/login works, tenant creation works, RLS test passes, CI green, branch protection active.

## Phase 2 — Core MVP backend

| Issue | Title | Depends on |
|---|---|---|
| [#8](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/8) | Implement campaign and content APIs | #5, #6 |
| [#9](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/9) | Implement AI generation worker and adapter | #6, #8 |
| [#10](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/10) | Implement quotas, rate limits, and audit log | #5, #9 |
| [#11](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/11) | Implement manual metrics import and summary | #3, #8 |

**Phase 2 exit:** brief → job → approved draft → metrics summary works end-to-end through the API.

## Phase 3 — Pilot readiness

| Issue | Title | Depends on |
|---|---|---|
| [#12](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/12) | Build minimal dashboard smoke flow | Phase 2 complete |
| [#13](https://github.com/mamourgroupe-ctrl/ai-growth-operator/issues/13) | Configure staging/production deployment and backups | #2, #14 |

**Phase 3 exit:** pilot-ready staging environment and smoke-tested dashboard.

## Backlog hygiene

- One issue = one reviewable outcome with explicit acceptance criteria.
- No issue may be closed without evidence (test output, PR link, or recorded decision).
- New product scope requires a new issue and a PRD decision reference.
- Issues are never auto-closed by merges without review.
