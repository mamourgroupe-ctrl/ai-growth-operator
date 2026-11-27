# Phase 0 — API Specification (final acceptance draft)

**Status:** Corrected for final approval. No routes implemented in Phase 0.
**Version:** `v1` · Base `https://api.<domain>/v1`

## 1. Conventions

- JSON; RFC 7807 errors; session cookie + `X-CSRF-Token` on mutations.
- `{org_id}` = technical tenant UUID; product term "Organization".
- `Accept-Language`: `ar` default (MSA/RTL), `fr` secondary. Content styles: `ar` (MSA), `ar-DZ` (Darija), `fr`.
- Money responses: `{"amount":"12000.00","currency":"DZD","display":{"DZD":"...","USD":"..."}}`; USD from immutable `fx_rate_snapshots`; client cannot submit a rate. FX source is an unresolved config decision.
- Pagination `limit`/`cursor`; `Idempotency-Key` required on approval creation and action requests.
- Roles: owner (final approval), editor (prepare/submit), viewer (read-only).

## 2. Endpoint inventory

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/healthz`, `/readyz` | none | Liveness/readiness |
| POST | `/auth/register`, `/auth/login`, `/auth/logout` | —/—/session | Auth |
| GET | `/auth/me` | session | User + memberships |
| GET/POST | `/organizations` | session | List/create organizations |
| GET/PATCH | `/organizations/{org_id}` | member/owner | Settings, locales, display currencies |
| GET/POST | `/organizations/{org_id}/members` | member/owner | Members |
| PATCH | `/organizations/{org_id}/members/{user_id}` | owner | Role/reviewer flag |
| GET/PATCH | `/organizations/{org_id}/profile` | member/editor | Business profile |
| GET/POST/PATCH | `/organizations/{org_id}/products` | member/editor | Product catalog |
| GET/POST/PATCH | `/organizations/{org_id}/content` | member/editor | Marketing copy |
| POST | `/organizations/{org_id}/content/{id}/submit-arabic-review` | editor | Route `ar`/`ar-DZ` to human review |
| POST | `/organizations/{org_id}/arabic-reviews/{id}/decide` | flagged editor reviewer | approve / request changes |
| POST | `/organizations/{org_id}/content/{id}/submit-for-approval` | editor | Creates approval request (never decides) |
| GET | `/organizations/{org_id}/calendar?from&to` | member | Scheduled content |
| GET/POST | `/organizations/{org_id}/creatives` | member/editor | Creative assets |
| POST | `/organizations/{org_id}/ai/generate` | editor | Text/image job with `style` |
| GET | `/organizations/{org_id}/ai/jobs/{job_id}` | member | Job status |
| GET | `/organizations/{org_id}/usage` | member | Usage, limits, cost |
| GET | `/organizations/{org_id}/approvals` | member | Approval center |
| POST | `/organizations/{org_id}/approvals` | editor | Create request; `Idempotency-Key` |
| POST | `/organizations/{org_id}/approvals/{id}/decide` | **owner only** | approve/reject; snapshot hash check |
| POST | `/organizations/{org_id}/content/{id}/publish` | editor execution caller | Requires owner-approved `approval_id`; internal/landing publish only |
| GET/POST | `/organizations/{org_id}/landing-pages` | member/editor | Basic landing pages |
| POST | `/organizations/{org_id}/landing-pages/{id}/publish` | editor execution caller | Requires owner-approved `approval_id` |
| GET | `/organizations/{org_id}/external-actions/{id}` | member | State machine status incl. `uncertain` |
| GET | `/organizations/{org_id}/money/display` | member | DZD/USD display via snapshot |
| POST | `/organizations/{org_id}/social/publish` | — | Reserved `501` (deferred) |
| POST | `/organizations/{org_id}/ads/activate` | owner when enabled | Reserved `501` (deferred) |

A viewer receives `403` on every mutation route. An editor calling `/approvals/{id}/decide` receives `403` even with a valid session and valid approval ID; approval authority is never inferred from UI state.

## 3. Key schemas

### Approval request
```json
{
  "id": "a91c...",
  "kind": "landing_page_publish",
  "target_type": "landing_page",
  "target_id": "c33f...",
  "target_version": 2,
  "status": "approved",
  "decided_by": "owner-user-id",
  "snapshot_id": "s12...",
  "budget": null
}
```
Ad-kind approvals (deferred) include `budget` with native ceiling, USD display, and `fx_snapshot_id`.

### Generation request
```json
POST /organizations/{org_id}/ai/generate
Idempotency-Key: 6f1b...
{"capability":"text","kind":"social_post","style":"darija","brief":"إعلان قصير عن عرض جديد"}
```
`style` ∈ `msa` | `darija` | `fr`. Provider/model chosen by gateway config, never by client.

### Approval-gated execution
```json
POST /organizations/{org_id}/content/{id}/publish
{"approval_id":"a91c...","idempotency_key":"pub-2026-11-24-001","expected_snapshot_hash":"sha256:..."}
```
Server verifies: owner-made approval, status `approved`, not expired/superseded, version + hash match, Arabic review passed when required, then writes `external_actions` + `outbox_events` in one transaction. An uncertain provider result leaves state `uncertain`; no automatic retry.

## 4. Money, FX, and reconciliation

USD display uses an immutable server snapshot; source/rounding policy unresolved. External action responses expose `state` and `provider_ref`; `uncertain` requires reconciliation before any further attempt. Reconciliation endpoints are admin-only and append audit records.

## 5. Contract governance

OpenAPI generated from FastAPI. Contract tests block breaking changes without `/v2`. Deferred social/ad routes return `501` until a new approved phase.
