# Phase 2 — API Contracts / OpenAPI Changes (proposed)

**Status:** Proposed. No endpoints added in this planning task.

## Decision status

| Category | Summary |
|---|---|
| `OWNER_APPROVED` / `FROZEN` baseline | FastAPI OpenAPI as contract source; bearer/cookie session from Phase 1; tenant context set server-side; owner-only approval; no external publishing. |
| `OWNER_PROPOSED` decisions | D-01–D-05, D-07, D-08; REST + idempotency and async job polls are `FROZEN` engineering baselines. |
| `BLOCKED` / `DEFERRED` | Numeric quota headers/caps and French UI locale `BLOCKED`; lead APIs and publishing endpoints `DEFERRED`. |
| External dependencies | Provider caps; legal review; owner authorization for issue/document amendments. |
| Confirmed boundary | No advertising approval, ad-spend, FX, paid execution, external action, outbox, or campaign-launch endpoint exists in Phase 2. |
| Risks | Unsafe client-controlled provider selection; leaking lead PII; ambiguous job state. |

## 1. Conventions

- All **new Phase 2** endpoints use prefix `/api/v1`; JSON only; `tenant_id` never in request path/body (resolved from session membership). Existing Phase 1 routes are root-level (`/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me`, `/healthz`, `/readyz`, `/organizations/...`) and are a confirmed legacy baseline; do not silently rewrite them. Consolidation under `/api/v1` requires change control (D-18).
- Pagination: `limit` (1–100, default 20), `cursor`; deterministic `created_at,id` ordering.
- Mutations that create external cost or decision side effects require `Idempotency-Key` header (UUID).
- Errors use Phase 1 `{"detail": ...}` or `{"error": {"code": ..., "message": ...}}`; never leak provider errors/secrets.
- Roles: `owner`, `editor`, `viewer`; `is_arabic_reviewer` boolean on `tenant_memberships` (existing canonical field in `0001_initial`, documented in `03-database-design.md §1`). It grants review capability only. D-01 `OWNER_PROPOSED` records owner-only final approval; editor submits, Arabic reviewer reports, viewer reads.
- No endpoint accepts advertising budget, spending ceiling, FX rate, external platform target, or campaign-launch instruction in Phase 2.

## 2. Proposed endpoint groups

### Business foundation (2A)
| Method & path | Roles | Notes |
|---|---|---|
| `GET/PATCH /api/v1/business/profile` | owner, editor (GET viewer) | One per tenant; `PATCH` validates known fields only |
| `POST /api/v1/business/onboarding/conversations` | owner, editor | Create conversation session |
| `POST /api/v1/business/onboarding/conversations/{id}/messages` | owner, editor | Returns `proposed_fields`, `confidence`, `missing_fields`; **no DB fact write** |
| `POST /api/v1/business/onboarding/conversations/{id}/confirm` | owner, editor | Writes only explicitly confirmed fields; emits audit |
| `GET/POST/PATCH/DELETE /api/v1/catalog/products` | owner, editor; viewer GET | Soft delete; price+currency required |
| `GET/POST /api/v1/catalog/categories` | owner, editor; viewer GET | |
| `GET/POST /api/v1/brand/assets` | owner, editor; viewer GET | Upload via signed URL flow |
| `POST /api/v1/assets/uploads` | owner, editor | Issues short-lived signed upload URL with server-generated key |
| `GET/PATCH /api/v1/brand/guidelines` | owner, editor; viewer GET | Banned claims/disclaimers |

### AI and content (2B/2C)
| Method & path | Roles | Notes |
|---|---|---|
| `POST /api/v1/ai/generations` | owner, editor | Body: `capability` (`text`/`image`), `kind`, `style` (`msa`/`darija`/`fr`), `brief`, `product_ids`, `asset_ids`; returns 202 + job id |
| `GET /api/v1/ai/generations/{job_id}` | owner, editor (viewer status only if allowed) | `queued|running|succeeded|failed|dead_letter|uncertain` |
| `GET /api/v1/ai/usage` | owner | Per-tenant usage/cost snapshot; no secrets |
| `GET/POST /api/v1/content/items` | owner, editor; viewer GET | `locale`, `style`, `status`, `scheduled_for` |
| `POST /api/v1/content/items/{id}/versions` | owner, editor | Creates immutable version |
| `POST /api/v1/content/versions/{id}/validate` | owner, editor | Deterministic validations; returns findings |
| `POST /api/v1/content/versions/{id}/arabic-review` | editor with reviewer flag | Never grants final approval |
| `POST /api/v1/content/versions/{id}/submit-for-approval` | owner, editor | Requires validation and Arabic review where applicable |
| `GET /api/v1/approval/requests` | owner, editor, viewer | Status-filtered |
| `POST /api/v1/approval/requests/{id}/decide` | **owner only** | `approve|reject|request_changes`; reason required for reject/changes |

### Creative, calendar, conversion
| Method & path | Roles | Notes |
|---|---|---|
| `GET /api/v1/calendar/items?from=&to=` | all roles | Internal status only; no publish action |
| `POST /api/v1/creative/images` | owner, editor | 202 job; product references ownership-checked |
| `GET /api/v1/creative/images/{id}` | owner, editor; viewer GET | Signed read URL, no public URL |
| `POST /api/v1/landing/pages` | owner, editor | Internal create/edit/preview scope; version state only |
| `GET/POST /api/v1/landing/pages/{id}/versions` | owner, editor; viewer GET proposed | Creates immutable `landing_page_versions` row; approval status lives on the version; page has no approved-version FK |
| `POST /api/v1/landing/pages/{id}/internal-publish` | — | Phase 3+ `DEFERRED`; no Phase 2 endpoint |
| `POST /api/v1/public/leads` | — | Phase 3+ `DEFERRED`; no Phase 2 route or schema |
| `GET /api/v1/leads` | — | Phase 3+ `DEFERRED`; no Phase 2 route or UI |

## 3. Representative schemas

```jsonc
// POST /api/v1/ai/generations
{
  "capability": "text",
  "kind": "social_post",
  "style": "darija",       // msa | darija | fr
  "brief": "Arabic text with no unapproved price claims",
  "product_ids": ["uuid"],  // optional, tenant-owned
  "asset_ids": ["uuid"]     // optional, tenant-owned
}
// 202
{ "job_id": "uuid", "status": "queued", "idempotency_key": "uuid" }
```
`Idempotency-Key` is required. One job and one `ai_usage_records` row per `(tenant_id, idempotency_key)`; AI cost evidence references `ai_price_snapshots` (USD pricing), never advertising FX.

```jsonc
// POST /api/v1/content/versions/{id}/validate
{
  "findings": [
    {"rule_code": "price_mismatch", "severity": "block", "passed": false,
     "evidence": {"expected": "DZD 1200", "found": "DZD 1000"}}
  ],
  "overall": "blocked"
}
```

```jsonc
// POST /api/v1/approval/requests/{id}/decide
{ "decision": "approve", "reason": null }
// 403 for owner-less tenants or non-owner roles
```
`@override_reason` may be supplied only for `warn` findings by the owner. `block` findings (`schema_invalid`, `price_mismatch`, `currency_missing`, `banned_claim`, `tool_instruction_leak`, `asset_unscanned`, `asset_cross_tenant`) are non-overridable and must be corrected before submit. Canonical rules are in `11-automated-content-validation-spec.md §5`.

## 4. State machines

- Generation job: `queued → running → succeeded|failed|dead_letter|uncertain`. Only worker transitions to `succeeded`; ambiguous provider result → `uncertain`, never blind retry.
- Content version: `draft → validating → review_required → reviewed → submitted → approved|rejected|changes_requested`. Editing approved content creates new version.
- Approval request: `pending → approved|rejected|changes_requested`.
- Landing page: `draft → approved_version` for internal preview/draft history. Publish execution (`internally_published`, `externally_published`) is `DEFERRED`; no Phase 2 publishing endpoint exists.

## 5. OpenAPI governance

- FastAPI generates schema; commit generated `openapi.json` only if CI already does so (do not introduce new generated artifacts without owner approval).
- Proposed CI contract test (not implemented by this documentation task) verifies: all tenant endpoints require auth; mutation roles enforced; `POST /api/v1/approval/requests/{id}/decide` denies editor/viewer; no endpoint accepts `provider`, `model`, `tenant_id`, `storage_url`, advertising budget, FX rate, or campaign-launch input from the client.
- No secrets, prompt text, or provider raw error appears in schema examples.
