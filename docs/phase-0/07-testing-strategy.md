# Phase 0 — Testing Strategy

**Status:** Proposed for approval. No tests are created in Phase 0.

## 1. Test pyramid

| Layer | Scope | Tooling (planned) | CI gate |
|---|---|---|---|
| Unit | Domain rules, validators, quota math, prompt construction | `pytest` | Required from Phase 1 |
| Integration | API + real Postgres, migrations, RLS, auth flows | `pytest` + `httpx` + ephemeral Postgres service | Required from Phase 1 |
| Contract | OpenAPI schema and example payloads | schema snapshot check | Required from Phase 1 |
| Security | Cross-tenant access, RBAC matrix, CSRF, session expiry | `pytest` security suite | Required from Phase 1 |
| AI behavior | Fake provider adapter, output validation, idempotency | `pytest` fixtures | Required from Phase 2 |
| E2E smoke | Login → campaign → draft → approve → metrics | Playwright (Phase 3) | Required from Phase 3 |
| Performance | Light load on core endpoints | `k6` or equivalent | Manual pre-pilot |

## 2. Non-negotiable test cases

1. Tenant isolation: user in tenant A cannot read/update tenant B resources, including by guessing IDs.
2. RLS active: queries without `app.current_tenant_id` return no tenant rows.
3. RBAC: viewer gets `403` on every editor/owner endpoint.
4. CSRF: mutation without token is rejected even with a valid session cookie.
5. Idempotency: duplicate `Idempotency-Key` with same payload returns same job; different payload returns `409`.
6. Session security: logout revokes; expired tokens are rejected; token hash never equals raw token.
7. Migration safety: upgrade then downgrade succeeds on a clean DB; no data-destructive step in a forward release.
8. AI adapter: malformed provider output is rejected and marked `failed` with a safe error code.
9. Quota: generation beyond plan limit returns `429` and creates no job.
10. Import idempotency: replaying the same `source_ref` does not duplicate metrics.

## 3. Test data and isolation

- Deterministic factories; no production data copies.
- Each test gets a fresh database schema or transaction rollback.
- Live LLM calls are forbidden in CI; use recorded/fake responses.
- Time-dependent tests use a frozen clock.

## 4. Coverage and quality gates

- Phase 1: ≥ 80% line coverage on `apps/api`; critical security paths 100% branch coverage.
- `ruff` and `mypy` clean; Alembic head check clean.
- Dependency audit with no unresolved high/critical advisories.
- Required checks must pass before a PR to `main` can merge.

## 5. Manual checks before pilot

- Restore a backup into a scratch DB and verify row counts.
- Review audit log redaction with a sample payload.
- Confirm provider cost caps and tenant quotas with a bounded load test.
- Security review of branch protection, secrets, and deploy permissions.
