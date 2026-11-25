# Phase 2 — Deployment and Environment Strategy

**Status:** Proposed. No infrastructure changed, no deployment performed.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | No production deployment in this task; no production credentials in repo; no production data in dev/test; modular monolith deployables web/API/worker. |
| Proposed decisions | Four environments (local, CI, staging, production) with identical migration process and feature flags; secrets in GitHub Environments/host secret manager. |
| Open questions | Hosting provider/region; domain; backup retention; provider key ownership; staging data policy; branch protection #14. |
| External dependencies | Owner infrastructure decision; legal review for data residency; provider accounts. |
| Risks | Config drift; secret leak; cost runaway; accidental external side effects; unverified `main` protection. |

## 1. Environments

| Environment | Data | Provider access | Purpose |
|---|---|---|---|
| Local developer | synthetic fixtures only | fake adapters by default | development |
| CI | synthetic fixtures only | fake adapters only | lint/test/security/migration cycle |
| Staging | synthetic or explicitly approved anonymized data; no live tenant PII | sandbox/fake providers, zero or capped spend | integration/QA/demo |
| Production | real tenant data, only after legal/security gate | real provider keys via secret manager | tenant use |

## 2. Configuration principles

- Single config module with strict validation; no secrets in `.env` committed to repo.
- Feature flags default-off for Phase 2 packages: `business_foundation`, `ai_text`, `ai_image`, `onboarding_assistant`, `content_validation`, `approval`, `landing_leads`.
- Provider/model values are DB registry config, not client input. Same registry behavior in all environments; staging uses fake codes.
- Object storage buckets: separate per environment; private by default; signed URL TTL short.
- Migrations run as a controlled deployment step with backup; runtime role `ago_app` with NOBYPASSRLS.
- Health/readiness endpoints report DB/queue/storage connectivity without leaking config.

## 3. Secret management

| Secret | Storage | Rotation |
|---|---|---|
| DB URLs / runtime role password | GitHub Environment secret or host secret manager | proposed every 90 days |
| AI provider keys | same; never in repo/logs | per provider policy |
| Object storage keys | same | per provider policy |
| Signed URL signing secret | same, if applicable | rotation invalidates old URLs |

CI secret scanning must remain enabled; provider error responses sanitized before logs.

## 4. Deployment units

- `web`: Next.js static/SSR app, HTTPS; talks only to API relative URL or configured public API URL preview proxy.
- `api`: FastAPI modular monolith; runs migrations as separate job, not on every replica.
- `worker`: same package, consumes `ai_generation_jobs`; concurrency 2 initially.
- `reconciliation`: reserved only if external actions are later approved; not used in Phase 2.

## 5. Preview environment note (Arena)

If a live preview is started during a later authorized implementation task: bind to `0.0.0.0`, allow proxy host/origin `{port}-{sandboxId}.e2b.app`, use relative API URLs, and keep fake providers. No live preview is started in this planning task.

## 6. Deployment checklist (future)

- [ ] Owner-approved provider/storage/residency decisions recorded in ADRs.
- [ ] Legal gate for provider transfer satisfied or gateway disabled for real data.
- [ ] Secrets configured in target environment; scanner clean.
- [ ] `alembic upgrade head` verified with backup and rollback plan.
- [ ] Feature flags reviewed; all external publishing/spend flags absent or off.
- [ ] RLS/role/approval negative suites green.
- [ ] Observability: job depth/oldest age, cost counters, error rate, p95 latency.
- [ ] `main` branch protection verified and issue #14 closed by owner before production release.

## 7. Rollback

- Application rollback: previous image/tag; DB migrations additive wherever possible.
- Provider rollback: feature flag/disabled registry entry; no blind retry of ambiguous jobs.
- Storage rollback: abstraction switch requires config change only; no client-visible URL change.
- Data rollback: no destructive migration in Phase 2; restore runbook required before production.
