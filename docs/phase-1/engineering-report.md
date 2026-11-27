# Phase 1 — Engineering Report

**Status:** Phase 1 Engineering Acceptance: **CONDITIONALLY ACCEPTED**.
**Branch:** `arena/5dc98770-ai-growth-operator`
**PR:** #15 — open draft, targeting `main`, **not merged**
**Phase 2:** not started.

## 0. Engineering acceptance decision

**Phase 1 Engineering Acceptance: CONDITIONALLY ACCEPTED** (engineering review, 2026-11-24).

Evidence accepted:

- PostgreSQL runtime uses the non-privileged `ago_app` role.
- RLS and cross-tenant API isolation tests passed.
- Migration `upgrade → downgrade → upgrade` passed from a clean database.
- Authentication, session expiration and revocation tests passed.
- Audit-log integrity and secrets scanner checks passed.
- CI passed on code HEAD `562575a`; working tree was clean.
- PR #15 remains OPEN and DRAFT; `main` remains unchanged at `7820f29`.

Outstanding conditions:

1. The repository owner must enable and verify branch protection on `main` (Issue #14). It is **NOT VERIFIED**; do not close the issue or merge PR #15 until verified.
2. Production environment security and operational readiness must be verified before deployment.

The independent audit (`docs/phase-1/independent-acceptance-audit.md`) and remediation evidence (`docs/phase-1/remediation-report.md`) remain preserved and unchanged. CI evidence refers to the code HEAD `562575a`; this decision entry is documentation-only and adds no application changes.

## 1. Issue-by-issue delivery

### Issue #2 — Repository tooling and CI
**Implemented:** Python packaging (`pyproject.toml`), `.gitignore`, `.env.example`, Makefile, FastAPI skeleton, Next.js 15 + TypeScript responsive foundation, GitHub Actions CI with jobs `lint`, `test`, `security`.
**Changed files:** `pyproject.toml`, `.gitignore`, `.env.example`, `Makefile`, `.github/workflows/ci.yml`, `apps/api/app/{__init__,config,main}.py`, `apps/web/*`, `tests/*`.
**Commit:** `242d260fd40c138ca5d907c79c2b7dbb1f551ce0`
**Commands:** `npm --prefix apps/web run typecheck`, `npm --prefix apps/web run build`, `.venv/bin/pytest -q`, `.venv/bin/ruff check apps/api tests`.
**Result:** typecheck passed; production Next.js build passed; API tests passed; lint passed.
**Unresolved:** GitHub Actions emits a non-blocking Node.js 20 deprecation warning for checkout/setup actions.

### Issue #14 — Branch protection
**Implemented:** Documented required settings and attempted to apply them through the GitHub API.
**Changed files:** `docs/phase-1/branch-protection.md`.
**Commit:** `6739ca2b5adafee87c199caffb8711d0bebb8bc8`
**Command:** `gh api -X PUT repos/mamourgroupe-ctrl/ai-growth-operator/branches/main/protection ...`
**Result:** `403 Resource not accessible by integration`. Settings were **not** applied; issue remains open.
**Unresolved:** A repository admin with `administration:write` scope must apply protection. Do not merge until then.

### Issue #3 — PostgreSQL and Alembic baseline
**Implemented:** SQLAlchemy models, Alembic baseline `0001_initial`, RLS policies for all tenant-owned tables, Postgres-backed job table with `SKIP LOCKED` claiming and idempotency key, outbox and audit tables.
**Changed files:** `alembic.ini`, `apps/api/migrations/*`, `apps/api/app/{db,models,jobs}.py`, `tests/conftest.py`, `tests/test_database_baseline.py`.
**Commit:** `a0bf0a2e01e5a45ced09d7d973c4a956a752a7d4`
**Commands:** `pytest -q tests/test_database_baseline.py`, full `pytest -q`.
**Result:** 3 baseline tests passed; migration executed on ephemeral Postgres via `command.upgrade(..., "head")`; RLS exercised with non-superuser role `ago_app`; two sequential claims returned distinct jobs.
**Unresolved:** No production database/host provisioned; app-role credentials must be supplied by deployment environment.

### Issue #6 — OpenAPI contract and error handling
**Implemented:** RFC 7807 `application/problem+json` handlers for domain errors, validation errors, and HTTP errors; committed OpenAPI artifact with parity test.
**Changed files:** `apps/api/app/errors.py`, `apps/api/app/main.py`, `apps/api/openapi.json`, `scripts/dump_openapi.py`, `tests/test_api_contract.py`.
**Commit:** `e1fe9da43525faaf538060cf0db2398c04415862`
**Commands:** `PYTHONPATH=apps/api python scripts/dump_openapi.py`, `pytest -q`.
**Result:** OpenAPI generated and matches committed artifact; 404 and validation responses use problem format.
**Unresolved:** None.

### Issue #4 — Authentication and sessions
**Implemented:** Argon2id passwords, opaque SHA-256-hashed session tokens, CSRF tokens, secure cookies, register/login/logout/me, owner membership created on registration.
**Changed files:** `apps/api/app/{auth,security,schemas}.py`, `apps/api/app/routers/auth.py`, `apps/api/app/main.py`, `tests/test_auth.py`.
**Commit:** `40d784021e644c08a82c777d7019e4fa48da105c`
**Commands:** `pytest -q tests/test_auth.py`, full `pytest -q`.
**Result:** Registration, login, logout, CSRF rejection, duplicate email conflict, validation errors, and session revocation all passed.
**Unresolved:** Email verification and MFA are outside Phase 1.

### Issue #5 — Organization and RBAC
**Implemented:** Organization list/create/read/update, member list/add/update, owner-only mutation dependencies, editor submission role, viewer read-only, Darija reviewer flag restricted to owner/editor.
**Changed files:** `apps/api/app/auth.py`, `apps/api/app/routers/organizations.py`, `apps/api/app/schemas.py`, `apps/api/app/main.py`, `tests/test_rbac.py`.
**Commit:** `e67e02c1004bb11958f84927a527b447bc532130`
**Commands:** `pytest -q tests/test_rbac.py`, full `pytest -q`.
**Result:** Owner management, editor/viewer denial, cross-tenant 404, and reviewer-flag rules passed.
**Unresolved:** None in Phase 1.

### Issue #7 — Tenant isolation tests
**Implemented:** Dedicated security suite verifying app role privileges, RLS visibility, RLS `WITH CHECK`, cross-tenant API denial, and member-role bypass prevention.
**Changed files:** `tests/test_tenant_isolation.py`.
**Commit:** `5d9a5392e52f63538eb3d4fbe7e6959f87897f4d`
**Commands:** `pytest -q tests/test_tenant_isolation.py`.
**Result:** All isolation tests passed using `ago_app` (non-superuser, `NOBYPASSRLS`).
**Unresolved:** None in Phase 1.

### CI correction
**Implemented:** Replaced a brittle secret grep with a source-only scanner to avoid flagging test fixtures.
**Changed files:** `.github/workflows/ci.yml`, `scripts/check_no_secrets.py`.
**Commit:** `dff00f9b14de710af726a1beb737fb78dc811e45`
**Result:** CI runs `#45424877575` and `#45424864636` completed with **success** for all three jobs (`lint`, `test`, `security`).

## 2. Verification performed

| Check | Command / evidence | Result |
|---|---|---|
| Application starts | `uvicorn app.main:app --app-dir apps/api --host 0.0.0.0 --port 8000` | Started; `/healthz` returned `{"status":"ok"}` |
| Web foundation starts | `npm --prefix apps/web run dev -- -p 3000` | Ready; `/` returned HTTP 200 |
| Migrations execute | Alembic `upgrade head` in test fixture | Passed on real Postgres |
| Registration/auth | `pytest -q tests/test_auth.py` | Passed |
| Organization creation | `pytest -q tests/test_rbac.py` | Passed |
| RBAC owner/editor/viewer | `pytest -q tests/test_rbac.py` | Passed |
| Cross-tenant rejection | `pytest -q tests/test_tenant_isolation.py` | Passed |
| RLS via app role | `pytest -q tests/test_tenant_isolation.py` | Passed with `rolsuper=false`, `rolbypassrls=false` |
| CI executes tests | GitHub Actions run IDs above | `test` job passed |
| No secrets in source | `python scripts/check_no_secrets.py` | No patterns found |
| Lint / types / SAST | `ruff`, `mypy`, `bandit` | All clean |
| Full suite | `.venv/bin/pytest -q` | **18 passed** |

## 3. Security and financial safeguards in Phase 1

- Passwords hashed with Argon2id; raw session tokens never stored.
- CSRF required on every mutation; owner-only approval/management dependencies enforced server-side.
- RLS enabled and forced on every tenant-owned table; verified with a non-privileged application role.
- Outbox table and idempotency keys created in the baseline for later approval/financial workflows.
- No external publishing, ad execution, FX snapshots, or AI provider calls exist in Phase 1.

## 4. Remaining risks

1. **Branch protection not applied** (#14) — GitHub integration lacks `administration:write`. Do not merge PR #15.
2. No production Postgres, secrets, or host configured; deployment is Phase 3+ work.
3. `pgserver` is a test-only embedded Postgres; production DB provisioning remains external.
4. GitHub Actions Node.js 20 deprecation warning is non-blocking.
5. Starlette/httpx emits a deprecation warning from `TestClient`; non-blocking.
6. Phase 2 features (AI studio, Arabic review, approval center, FX display) are intentionally absent.

## 5. Stop condition

Phase 1 implementation and verification are complete. Phase 2 is **not started**. PR #15 remains draft and unmerged; no commit was made to `main`.
