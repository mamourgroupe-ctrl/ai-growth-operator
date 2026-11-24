# Phase 0 — Technical Architecture

**Status:** Proposed for approval. No implementation is authorized by this document.
**Design principles:** smallest system that supports the product hypothesis; one source of truth; strong tenant isolation; testable without external services; no premature distribution.

## 1. System shape

```text
Browser (Next.js, later phase)
        |
        | HTTPS / JSON
        v
API (FastAPI, Python)  -----> PostgreSQL 16 (shared schema, RLS)
        |                          ^
        | enqueue job              | read/write
        v                          |
ai_generation_jobs table           |
        |                          |
        v                          |
Worker (same Python package) ----> LLM provider adapter (one provider)
```

There are three deployable processes at most: web, API, worker. Phase 1 may ship API + worker only.

## 2. Components

| Component | Choice | Rationale |
|---|---|---|
| API | Python 3.12 + FastAPI + Pydantic v2 | Typed validation and generated OpenAPI with little boilerplate |
| Web client | Next.js + TypeScript (Phase 3) | Server-rendered dashboard, one frontend codebase |
| Database | PostgreSQL 16 | RLS, JSONB, maturity, transactional integrity |
| DB access | SQLAlchemy 2.0 + Alembic | Explicit migrations, no magic schema sync |
| Background work | Postgres-backed job table with `FOR UPDATE SKIP LOCKED` | Avoids Redis/Kafka for low initial volume |
| LLM access | One provider via a thin `ContentGenerator` protocol | Swappable without a multi-provider framework |
| File storage | None in Phase 1 | Content is text in Postgres |
| Email | Adapter interface; no provider chosen until invites are needed | Avoids an early external dependency |
| Observability | Structured JSON logs + health endpoints | Enough for pilot; error tracking added later |

## 3. Request and job flows

**Standard request**
1. Browser sends session cookie plus CSRF header on mutations.
2. API authenticates session, resolves tenant membership and role.
3. A transaction sets `app.current_tenant_id` with `SET LOCAL`.
4. Query executes under Postgres RLS.
5. Response is serialized through a Pydantic response model.

**AI generation**
1. `POST /v1/ai/generate` validates input, checks quota, inserts a job with an idempotency key, returns `202`.
2. Worker claims one job with `SELECT ... FOR UPDATE SKIP LOCKED`.
3. Worker calls the configured provider adapter with a bounded prompt and timeout.
4. Result is validated against an expected JSON/text shape and stored on the job.
5. Client polls `GET /v1/ai/jobs/{job_id}` until terminal state.

No live LLM call is made in CI; tests use a fake adapter.

## 4. Multi-tenancy model

- Shared database, shared schema.
- Every tenant-scoped table has `tenant_id uuid NOT NULL`.
- RLS is enabled on every tenant-scoped table with a policy comparing `tenant_id` to `current_setting('app.current_tenant_id')::uuid`.
- Application-level authorization still checks membership and role; RLS is defense in depth, not the only check.
- `users` is global; access is mediated by `tenant_memberships`.

## 5. Proposed repository layout (documentation only today)

```text
docs/phase-0/        Phase 0 deliverables
apps/api/            FastAPI application, Alembic migrations, worker
apps/web/            Next.js dashboard (later)
tests/               Unit, integration, security, contract tests
infra/               Container and deployment manifests
.github/             Actions and issue templates
```

A monorepo is used because the API, worker, web app, and migrations share contracts and must version together.

## 6. Non-goals / deliberate omissions

- No microservices, message broker, or Kubernetes in Phase 1.
- No per-tenant database provisioning.
- No Redis cache.
- No billing service.
- No broad provider abstraction or plugin system.
- No direct social-network publishing APIs.

## 7. Cross-references

- Database details: `03-database-design.md`
- API details: `04-api-specification.md`
- Security details: `05-security-architecture.md`
- Decisions and rationale: `10-architecture-decision-log.md`
