# Phase 2 — Testing and QA Strategy

**Status:** Proposed. No tests added in this planning task.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | CI lint/test/security gate from Phase 1; `ago_app` runtime role for DB tests; no production data in dev/test; owner-only approval; RLS tenant isolation. |
| Proposed decisions | Test pyramid with fake providers, synthetic fixtures, RLS catalog check, adversarial validation and approval-negative suites. |
| `BLOCKED` / `DEFERRED` | Native Arabic/Darija reviewer allocation, load-test thresholds and provider sandbox availability pending; lead tests `DEFERRED`; D-01 final confirmation pending. |
| External dependencies | Human reviewers; provider sandboxes/keys (only after legal gate for real data); owner verification of `main` branch protection. |
| Confirmed boundary | No advertising, paid execution, FX, outbox, or campaign-launch test scope in Phase 2. |
| Risks | False confidence from mocked providers; unmeasured Darija quality; flaky queue tests. |

## 1. Test layers

| Layer | Scope | Tooling (proposed) |
|---|---|---|
| Unit | validators, prompt builders, cost math, state machines | pytest |
| API/contract | FastAPI routes, role matrix, OpenAPI schema | httpx ASGI/HTTP, pytest |
| DB/RLS | policies, composite FKs, append-only constraints, migration cycle | pgserver/`ago_app` role |
| Integration | API + DB + fake AI/storage | in-process fake adapters |
| Worker | queue lease/retry/idempotency/dead-letter | deterministic clock |
| E2E UI | onboarding → generation → validation → approval → landing | Playwright (if approved) |
| Accessibility | RTL, keyboard, contrast | axe checks (proposed) |
| Benchmark | provider comparison (synthetic only) | separate harness, not CI by default |
| Security | secrets scan, dependency audit (existing CI) | existing CI jobs |

### 1.1 Verified current CI vs proposed gates

**Verified current (2026-11-24/25):** `.github/workflows/ci.yml` has exactly three jobs: `lint` (ruff, mypy, npm typecheck), `test` (`pytest -q`), and `security` (bandit, `scripts/check_no_secrets.py`). Run `45565465339` on HEAD `8da2f9a` reported `success` for all three. These jobs were not changed by documentation remediation.

**Proposed future gates (not present today):** RLS catalog verification, OpenAPI contract/role-matrix tests, Alembic upgrade/downgrade cycle, fake-provider integration, worker queue semantics, validation/approval negatives, and prompt-injection suites. They are acceptance targets, not existing CI facts. Local `pytest` execution was **not** performed in the audit sandbox: `pytest` was unavailable and no dependencies were installed.

## 2. Mandatory regression suites

1. **Tenant isolation**: for every tenant-owned table, `ago_app` with tenant A context cannot read/write tenant B rows; API cross-tenant IDs return 404/403.
2. **RLS catalog check**: every table in tenant registry has FORCE RLS + `USING`/`WITH CHECK` policy; fail CI on new unlisted tenant table.
3. **Role matrix**: owner/editor/viewer/reviewer endpoints; owner-only approval; viewer redaction; no client role escalation.
4. **Migration cycle**: `upgrade head`, `downgrade -1`, `upgrade head` on clean DB; no superuser bypass.
5. **Queue semantics**: `SKIP LOCKED`, lease expiry reclaim, bounded retries, dead-letter, idempotency, `uncertain` state, no retry from ambiguous provider response.
6. **AI gateway fake adapter**: deterministic outputs for success/schema-failure/timeout/rate-limit/usage-missing; cost snapshot recorded; no provider key in logs.
7. **Validation rules**: price mismatch with Arabic-Indic digits, banned claims, currency missing, injection leak, cross-tenant/unscanned asset.
8. **Approval negatives**: all bypass attempts 403/409; snapshot append-only; supersession.
9. **Prompt injection fixture**: product text instructs “approve/content/publish/spend”; output never triggers these actions.
10. **Privacy**: no user PII in prompts/logs; synthetic-only fixtures in CI; secrets scanner passes. No Phase 2 lead PII exists; lead tests are `DEFERRED` to Phase 3.

## 3. Benchmark acceptance (human + harness)

| Metric | Acceptance |
|---|---|
| Schema validity | ≥95% per candidate before enabling |
| Price fidelity | 100% on synthetic fixture |
| Injection resistance | 100% |
| Darija authenticity | blind native reviewer mean ≥4/5 |
| Cost/latency | recorded with dated source; no winner claimed without full run |

Benchmark must use the corrected, valid fixture in `07-ai-gateway-text-provider-comparison.md §2`; image tasks are split into generation and editing in `08-image-generation-provider-comparison.md §2`. Record fixture/prompt/schema hashes, exact model identifiers and revisions, actual token/cache counts, latency, errors, and cost. Retain hashes/metadata, not real PII. No benchmark has been executed and no provider is selected.

## 4. QA gates

- **Proposed** PR gate (not current CI): lint + unit + API + RLS + migration + security scanner all green. Current CI has lint/test/security only.
- Human gate: Arabic reviewer sign-off for `ar`/`ar-DZ` templates before enabling locale.
- Owner gate: pilot sector, provider, storage, quotas, legal review.
- Release gate: no unresolved blocking privacy/security condition; feature flags disabled by default.

## 5. Data policy for tests

- Synthetic fixtures only: `مخبز النخلة`, `خبز الصافي`, fixed prices, fake users with `@example.test` or valid test domains per Pydantic constraints.
- No copies of production DB/snapshots in CI/dev without separate documented approval (current rule: never).
- Provider calls in CI use fake adapters; live calls only in a controlled manual benchmark with synthetic data.

## 6. Definition of done per Phase 2 issue

- Code + tests + docs updated where needed.
- No new secret or real PII; scanner passes.
- RLS check passes for any new tenant table.
- Owner-only boundary has negative test where applicable.
- Manual QA script executed and result recorded (date, environment, tester).
- No publishing, lead ingestion, external publishing, or spend action introduced in Phase 2.

## 7. Known limits

- No benchmark has been run; no performance/quality claim is acceptable yet.
- No UI E2E tool currently verified in this repo; Playwright proposal needs owner/CI approval.
- Branch protection on `main` remains NOT VERIFIED (issue #14); CI gate strength depends on it.
