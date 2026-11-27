# Phase 2 — Detailed Technical Architecture

**Status:** Proposed. No implementation authorized.  
**Preserved decision:** modular monolith. No microservices without a documented, approved reason.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Phase 0/1 stack, RLS+RBAC, owner-only approval, provider-independent gateway, S3-compatible abstraction, no external publishing/spend. |
| Proposed decisions | Domain modules inside one FastAPI app; separate worker process sharing the codebase/DB; gateway policy engine; asset service; validation service. |
| `OWNER_PROPOSED` / `BLOCKED` | D-01 owner-only approval; D-02 internal landing pages only with leads `DEFERRED`; D-03 DZD-only user display; D-04 configurable quotas; D-05 study sectors; D-07 benchmark-based provider choice; D-08 comparison-based storage choice. Final confirmation and external evidence remain `BLOCKED`. |
| External dependencies | Legal/privacy review, benchmark outcomes, provider contracts, owner authorization for issue amendments. |
| Confirmed boundary | Phase 2 content approval core only; advertising execution, FX, paid outbox/reconciliation and external state machines are Phase 3. |
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
  ├── landing_pages (internal create/edit/preview only)
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
| `landing_pages` | Internal create/edit/preview and draft/version history | External publishing, lead capture, lead management, CRM and paid actions |
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
- Landing pages support internal drafts, version history and preview only. Publish execution, public URLs and lead capture are `DEFERRED`; no external side effect is created in Phase 2.

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
- Viewer is read-only; Arabic reviewer reports findings and is not final approver; editor prepares and submits. D-01 is `OWNER_PROPOSED` with owner-only final approval, matching the existing baseline; `12-approval-workflow-spec.md §1` contains the role matrix.
- Secrets only in GitHub Environments/host secret manager; no secrets in source/logs; signed URL tokens not logged.
- Logs redact prompts, tokens and provider keys. No lead PII exists in Phase 2. Audit logs record actor, action, target, request ID and decision evidence.
- No production data in dev/CI. Synthetic fixtures only.

## 8. Consequences of the confirmed Phase 2 boundary

**Confirmed:** the Phase 2 approval core is in scope. Ad-spend approval, FX snapshots for advertising, external paid-action authorization, outbox/reconciliation, external execution state machines, and automatic campaign launching remain Phase 3. No alternative naming may move them into Phase 2.

- `approval` module implements Phase 2 content approval core: validation gate, review evidence, owner-only decision under D-01 `OWNER_PROPOSED`, immutable versions/snapshots, audit, and supersession.
- `landing_pages` is `OWNER_PROPOSED` for internal create/edit/preview only. Lead tables, public lead ingestion, lead APIs, lead UI, publish execution, campaign integration and paid effects are `DEFERRED` to Phase 3 or later.
- Outbox dispatcher and reconciliation remain reserved for Phase 3; internal landing publish, if approved, writes no external action.
- Locale/RTL/style work is proposed for Phase 2 (#25 subset); D-03 `OWNER_PROPOSED` sets DZD-only user display and internally recorded USD AI cost, with no FX source or conversion. Advertising FX remains Phase 3.
- The Phase 1 `outbox_events` table may remain as existing baseline schema; this does not authorize Phase 2 paid-action outbox use.

## 9. Architecture risks

| Risk | Mitigation |
|---|---|
| DB queue load from AI jobs | Monitor depth/oldest age; keep concurrency 2; revisit Redis/Celery only at documented thresholds. |
| Provider cost overrun | Quota reservation, price snapshot, caps, fake providers in CI, no automatic retry from uncertain. |
| Prompt injection | Delimit untrusted data, schema validation, no tools, output sanitization. |
| Data residency/legal | Block real personal data to providers until legal review and ANPDP requirements addressed. |
| Scope creep | Explicit non-goals; new issues required for new features. |
