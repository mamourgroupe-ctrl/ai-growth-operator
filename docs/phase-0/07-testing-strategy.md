# Phase 0 — Testing Strategy (post-audit)

**Status:** Corrected for approval. No tests created in Phase 0.

## 1. Test pyramid

| Layer | Scope | Gate |
|---|---|---|
| Unit | Domain rules, locale handling, FX display math, backoff calculation, quota math | Required Phase 1 |
| Integration | API + real Postgres, migrations, RLS, auth, approval flow | Required Phase 1 |
| Contract | OpenAPI schema and examples (`ar`, `ar-DZ`, `fr`, dual money display) | Required Phase 1 |
| Security | Tenant isolation, RBAC, CSRF, fail-closed external actions | Required Phase 1 |
| AI gateway | Fake text/image providers, price snapshot, fallback, rate limits | Required Phase 2 |
| Job queue | Claim concurrency, retry/backoff, scheduling, idempotency, dead-letter | Required Phase 2 |
| E2E smoke | Arabic UI → generate → approve → publish-ready → lead capture | Required Phase 3 |
| Performance | Light load, queue depth behavior | Manual pre-pilot |

## 2. Non-negotiable test cases

1. Tenant A cannot read/mutate tenant B resources by ID guessing.
2. RLS returns no tenant rows without `app.current_tenant_id`.
3. Viewer blocked on editor/owner endpoints; only owner can approve ad spend.
4. Mutation without CSRF token rejected.
5. Publish/ad activation without `approval_id` returns error and makes **no** provider call.
6. Approval with wrong version, expired, superseded, or hash mismatch is rejected.
7. Budget change marks previous approvals `superseded`; old approval cannot execute.
8. Ad spend blocked when approval missing, ceiling missing, FX snapshot missing, or `spent + requested > ceiling`.
9. No automatic budget increase: spend ledger cannot write a positive ceiling delta without a new approval.
10. Idempotency: duplicate generation key returns same job; different payload → `409`.
11. Job claim concurrency: two workers never claim the same row (`SKIP LOCKED` test).
12. Backoff follows `min(30s * 2^(n-1), 15m) + jitter`; max attempts enforced; dead-letter after exhaustion.
13. AI output malformed → `failed` with safe error code; no raw provider message leaked.
14. Fallback blocked when residency policy forbids target provider.
15. Money display shows both DZD and USD from a snapshot; client cannot submit FX rate.
16. Arabic/Darija copy stored with correct locale; RTL UI smoke passes.

## 3. Data and CI

- Deterministic factories; no production data; frozen clock for time tests.
- No live provider calls in CI; fake text/image adapters.
- Coverage ≥80% Phase 1; 100% branch coverage on approval/budget gate.
- `ruff`, `mypy`, Alembic head check, dependency audit required before merge.

## 4. Manual pre-pilot checks

- Restore backup into scratch DB and verify counts.
- Review audit redaction with sample payload.
- Verify provider cost caps and queue thresholds under bounded load.
- Confirm branch protection and required checks active.
