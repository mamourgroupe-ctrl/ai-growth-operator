# Phase 0 — API Specification (post-audit)

**Status:** Corrected for approval. No routes implemented in Phase 0.
**Version:** `v1` · Base: `https://api.<domain>/v1`

## 1. Conventions

- JSON; RFC 7807 `application/problem+json` errors.
- Auth: HttpOnly session cookie + `X-CSRF-Token` on every mutation.
- "Organization" is the product term; path segment `{org_id}` is the technical tenant UUID.
- Locale header `Accept-Language`: `ar` default, `fr` secondary; content locale stored per item (`ar`, `ar-DZ`, `fr`).
- Money responses include dual display: `{"amount":"12000.00","currency":"DZD","display":{"DZD":"12,000.00 DZD","USD":"... USD"}}`.
- Pagination `limit`/`cursor`; idempotency header required on generation and approval creation.
- Rate limits: 100 req/min/user; AI limits from `subscriptions`.

## 2. Endpoint inventory

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/healthz`, `/readyz` | none | Liveness/readiness |
| POST | `/auth/register`, `/auth/login`, `/auth/logout` | —/—/session | Auth |
| GET | `/auth/me` | session | User + memberships |
| GET/POST | `/organizations` | session | List/create organizations |
| GET/PATCH | `/organizations/{org_id}` | member/owner | Settings incl. locales + display currencies |
| GET/POST | `/organizations/{org_id}/members` | member/owner | Members |
| PATCH | `/organizations/{org_id}/members/{user_id}` | owner | Role change |
| GET/PATCH | `/organizations/{org_id}/profile` | member/editor | Business profile + brand voice |
| GET/POST/PATCH | `/organizations/{org_id}/products` | member/editor | Product catalog |
| GET/POST/PATCH | `/organizations/{org_id}/content` | member/editor | Marketing copy drafts, locale-aware |
| POST | `/organizations/{org_id}/content/{id}/approve` | editor+ | Create approval request (not publish) |
| GET | `/organizations/{org_id}/calendar?from&to` | member | Scheduled content |
| GET/POST | `/organizations/{org_id}/creatives` | member/editor | Creative assets |
| POST | `/organizations/{org_id}/ai/generate` | editor+ | Text or image generation job |
| GET | `/organizations/{org_id}/ai/jobs/{job_id}` | member | Job status/result |
| GET | `/organizations/{org_id}/usage` | member | AI usage, limits, cost |
| GET/POST | `/organizations/{org_id}/approvals` | member/editor | Approval center |
| POST | `/organizations/{org_id}/approvals/{id}/decide` | approver | approve/reject with snapshot hash |
| POST | `/organizations/{org_id}/content/{id}/publish` | editor+ | Requires `approval_id`; fail-closed |
| GET/POST | `/organizations/{org_id}/landing-pages` | member/editor | Basic landing pages |
| POST | `/organizations/{org_id}/landing-pages/{id}/publish` | editor+ | Requires `approval_id` |
| GET/POST | `/organizations/{org_id}/leads` | member/editor | Lead management |
| GET | `/organizations/{org_id}/money/display` | member | DZD/USD display using snapshot |
| POST | `/organizations/{org_id}/ads/activate` | owner (deferred) | Reserved; requires approval + exact ceiling |

## 3. Key schemas

### Approval request
```json
{
  "id": "a91c...",
  "kind": "ad_activation",
  "target_type": "ad_campaign",
  "target_id": "c33f...",
  "target_version": 2,
  "status": "approved",
  "budget": {"amount": "25000.00", "currency": "DZD", "usd_display": "...", "fx_snapshot_id": "f77..."},
  "snapshot_id": "s12...",
  "decided_by": "7b2d...",
  "decided_at": "2026-11-24T14:40:00Z"
}
```

### Generation request
```json
POST /organizations/{org_id}/ai/generate
Idempotency-Key: 6f1b...
{
  "capability": "text",
  "kind": "social_post",
  "locale": "ar-DZ",
  "brief": "إعلان قصير عن عرض جديد",
  "brand_voice_ref": "b10..."
}
```
Image requests use `capability: "image"` with `brand_assets` context; provider/model selected by gateway config, not by client.

### Approval-gated publish
```json
POST /organizations/{org_id}/content/{id}/publish
{"approval_id": "a91c...", "expected_snapshot_hash": "sha256:..."}
```
Server verifies approval is `approved`, not expired/superseded, version and hash match, then records `external_actions` before calling any provider. Missing/invalid approval → `409`/`403`, no external call.

## 4. Money and FX

All monetary responses show both DZD and USD. USD uses `fx_rates` snapshot chosen by the server; clients cannot submit a rate. Approval budgets store native amount, USD display amount, and FX snapshot ID. No spend decision uses an unsnapshotted rate.

## 5. Contract governance

OpenAPI generated from FastAPI and committed once Phase 1 starts. Contract tests block breaking changes without a `/v2` bump. Deferred ad endpoints are documented but return `501` until implemented.
