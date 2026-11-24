# Phase 0 — Testing Strategy (final acceptance draft)

**Status:** Corrected for final approval. No tests created in Phase 0.

## 1. Test layers

| Layer | Scope | Gate |
|---|---|---|
| Unit | locale/style rules, backoff math, quotas, FX display math, idempotency key derivation | Phase 1 |
| Integration | API + real Postgres, migrations, RLS, auth, approval, outbox atomicity | Phase 1 |
| Contract | OpenAPI examples for `ar`/`ar-DZ`/`fr`, dual money display, 501 deferred routes | Phase 1 |
| Security | Tenant isolation, owner-only approval, bypass attempts, CSRF | Phase 1 |
| AI gateway | Fake text/image providers, price snapshots, fallback, rate limits | Phase 2 |
| Job queue | Concurrent claim, retry/backoff, scheduling, dead-letter, monitoring counters | Phase 2 |
| Execution safety | Outbox replay, idempotency, state machine `uncertain`, reconciliation | Phase 3 |
| E2E smoke | Arabic UI → generate → Arabic review → owner approval → publish-ready → lead | Phase 3 |

## 2. Non-negotiable cases

1. Tenant A cannot read/mutate tenant B by ID guessing.
2. RLS returns no rows without `app.current_tenant_id`.
3. Viewer blocked on all mutations; **editor calling `/approvals/{id}/decide` gets 403**; only owner decides.
4. Forged `approval_id`, wrong tenant, expired/superseded approval, or hash mismatch → no outbox row, no provider call.
5. Publish/execute without owner approval → blocked.
6. Budget change supersedes prior approval; no automatic increase; `spent + requested > ceiling` blocks before dispatch.
7. Outbox row committed in same transaction as authorized action; dispatcher replay with same aggregate/idempotency is a no-op.
8. Provider idempotency key stable across retries; duplicate provider call prevented.
9. Timeout with unknown provider result → state `uncertain`, **no automatic retry**, reconciliation required.
10. Reconciliation resolves `uncertain` to executed/failed with evidence; duplicates raise incident and freeze tenant execution.
11. Arabic `ar`/`ar-DZ` content without approved `arabic_reviews` cannot be submitted for approval.
12. Reviewer flag cannot be set by editor; viewer never reviewer.
13. Darija style stored distinctly from MSA and French; RTL smoke passes.
14. FX snapshots immutable; no update/delete path; approval references snapshot; client-submitted rate rejected.
15. Idempotency duplicate generation key returns same job; differing payload `409`.
16. Malformed AI output safe-coded; fallback blocked by residency policy.

## 3. Data and CI

Deterministic factories, frozen clock, no live provider calls in CI. Coverage ≥80% Phase 1; 100% branch coverage on approval/execution gate. `ruff`, `mypy`, Alembic head check, dependency audit required before merge.

## 4. Manual pre-pilot

Restore drill; audit redaction review; provider cost caps; queue threshold observation; reconciliation dry-run with fake provider; branch protection verification.
