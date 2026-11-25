# Phase 2 — Detailed Technical Architecture

**Status:** Proposed. No implementation authorized.  
**Preserved decision:** modular monolith. No microservices without a documented, approved reason.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Phase 0/1 stack, RLS+RBAC, owner-only approval, provider-independent gateway, S3-compatible abstraction, no external publishing/spend. |
| Proposed decisions | Domain modules inside one FastAPI app; separate worker process sharing the codebase/DB; gateway policy engine; asset service; validation service. |
| Open questions | Provider/model selection; storage provider; residency; whether approval/landing pages move into Phase 2. |
| External dependencies | Legal/privacy review, benchmark outcomes, provider contracts. |
| Risks | Worker/API DB contention; provider cost surprises; prompt injection; scope creep into CRM/billing. |

## 1. System shape

```text
Next.js web (ar/RTL, fr secondary)
        | HTTPS + session cookie + CSRF
        v
FastAPI modular monolith
  ├── organizations/auth (Phase 1)
  ├── business / catalog / brand / onboarding
  ├── content / validation / arabic_review / approval
  ├── creative / assets / calendar
  ├── landing / leads
  ├── ai_gateway (TextProvider, ImageProvider, policy, registry, usage)
  └── outbox dispatcher (reserved for future external effects)
        |
        v
PostgreSQL 16 (RLS, Alembic, hardened job queue, outbox, audit)
        |
        +--> Worker process (same package): AI jobs, image jobs, scheduled tasks
        +--> S3-compatible object storage (private by default)
        +--> External AI providers (synthetic data only until legal review)
```

Deployables remain web, API, worker, and reconciliation job (reconciliation only if external actions are activated later). This is not microservices: all modules are in one codebase and one database.

## 2. Module boundaries

| Module | Owns | Must not do |
|---|---|---|
| `business` | Business profile, objectives, USPs, competitors | Call AI provider directly |
| `catalog` | Products, offers, categories, product images | Bypass tenant ownership checks |
| `brand` | Brand assets and guidelines | Render untrusted SVG/HTML |
| `onboarding` | Manual wizard state, assistant session state | Confirm inferred facts without user action |
| `ai_gateway` | Provider abstraction, registry, policy, usage/cost | Decide approval or external actions |
| `content` | Content drafts, versions, locale/style, calendar | Publish externally |
| `validation` | Deterministic + model-assisted checks | Replace human approval |
| `review` | Arabic reviewer queue | Grant final approval |
| `approval` | Approval requests, snapshots, owner decision | Allow editor/viewer decision |
| `creative` | Image generation jobs, metadata | Use product image without ownership proof |
| `assets` | Object storage refs, signed URLs, scan status | Serve public URLs by default |
| `landing` / `leads` | Internal pages and lead capture | Advanced CRM features |
| `usage` | Quota snapshots, cost views | Expose secrets/provider keys |

Cross-module communication uses in-process service interfaces and DB transactions, not service-to-service HTTP.

## 3. Request and data flows

### 3.1 Generation flow
1. Editor requests generation with `capability`, `kind`, `style`, `brief`, optional product/asset IDs, and `Idempotency-Key`.
2. API verifies membership/role, tenant ownership of referenced records, quota availability, and idempotency.
3. In one transaction: reserve quota, create `ai_generation_jobs` row, write audit. Worker picks job with `FOR UPDATE SKIP LOCKED`.
4. Gateway selects provider/model from config, never from client input. Applies timeout, bounded retry, rate limit, residency/fallback policy.
5. Usage/cost finalized from token/image counts and **price snapshot at request time**. Ambiguous provider result → no blind retry; mark `uncertain` and require reconciliation/manual replay.
6. Output stored as untrusted draft. Validation runs before it can be submitted for review/approval.

### 3.2 Onboarding flow
- Manual: standard form with explicit save.
- Conversational: assistant returns structured JSON + confidence + missing fields. UI shows a reviewable summary. Only fields the user confirms are written to business facts; rejected fields remain in session history. No silent inference.

### 3.3 Approval flow
- Editor submits content version + validation result + Arabic review (when required) → approval request + immutable snapshot.
- Owner decides. Rejection/change request returns to draft. Editing an approved item creates a new version and supersedes prior approval.
- Landing page internal publish requires an approved page version. No external side effects are created in Phase 2.

## 4. AI Gateway design

```text
TextProvider protocol: generate(prompt_spec, schema, policy) -> ProviderResult
ImageProvider protocol: generate(brief, references, policy) -> ProviderResult
Gateway:
  - ModelRegistry (DB config, system-admin only)
  - PolicyEngine (tenant quota, rate limit, locale capability, residency, fallback)
  - Adapter per provider (no client-selectable URLs)
  - UsageRecorder (atomic reservation + finalization)
  - CircuitBreaker (per provider/process, DB-backed counters where needed)
  - RetryPolicy (max 2 attempts, full jitter, no retry from uncertain)
```

- Prompt templates are versioned, locale/style aware, and stored as config/data, not hard-coded per provider.
- Business data is passed as delimited untrusted content; model instructions cannot be changed by tenant content.
- Structured output is requested through JSON schema and re-validated locally. Invalid output is safe-coded, not rendered raw.
- Model output never calls tools that can publish, spend, approve, or modify approval state.

## 5. Object and asset design

- `ObjectStorage` protocol: `put`, `get_signed_url`, `stat`, `delete`. Private buckets by default; short-lived signed URLs (proposed 5–15 min).
- Keys generated server-side: `tenant/{tenant_id}/{kind}/{uuid}`; clients never choose keys.
- Upload validation: allowlisted MIME + magic bytes, size cap (proposed 10 MB image), checksum, scan status.
- Product/brand image usage requires DB ownership check `asset.tenant_id == org_id` and `scan_status='clean'` (or `not_required` in dev with explicit config).
- Malware scanning: design hook now; production provider must be selected before pilot. If no scanner is available, assets stay private and cannot be attached to published content.

## 6. Background jobs and queue

Reuse Phase 1 `ai_generation_jobs` with ADR-012 hardening (#20): `SKIP LOCKED`, leases, heartbeat, `run_at`, bounded retries with full jitter, dead-letter, idempotency, monitoring. Worker concurrency starts at 2. Cost-generating retries require provider idempotency or reconciliation; no infinite retry.

## 7. Security boundaries

- RLS on every tenant-owned table; app role `ago_app` non-superuser/NOBYPASSRLS; tests must use it.
- Authorization dependency resolves tenant membership/role from DB in the same tenant context; client cannot supply role.
- Viewer blocked on mutations; editor blocked on owner-only approval; Arabic reviewer is not approver.
- Secrets only in GitHub Environments/host secret manager; no secrets in source/logs; signed URL tokens not logged.
- Logs redact prompts, tokens, provider keys, lead contact details. Audit logs record actor, action, target, request ID, and decision evidence.
- No production data in dev/CI. Synthetic fixtures only.

## 8. Consequences of moving approval/landing pages into Phase 2

If owner approves re-baselining:
- `approval` module and `landing/leads` modules move from Phase 3 to Phase 2C/2D.
- Outbox remains reserved; internal landing publish writes no external action.
- UI work (#25) must be partially pulled forward for usable screens; otherwise Phase 2 APIs have no product surface.
If not approved:
- Phase 2C/2D deliver only draft schemas, contracts, and feature-flagged endpoints that cannot publish; approval and leads remain Phase 3.

## 9. Architecture risks

| Risk | Mitigation |
|---|---|
| DB queue load from AI jobs | Monitor depth/oldest age; keep concurrency 2; revisit Redis/Celery only at documented thresholds. |
| Provider cost overrun | Quota reservation, price snapshot, caps, fake providers in CI, no automatic retry from uncertain. |
| Prompt injection | Delimit untrusted data, schema validation, no tools, output sanitization. |
| Data residency/legal | Block real personal data to providers until legal review and ANPDP requirements addressed. |
| Scope creep | Explicit non-goals; new issues required for new features. |
