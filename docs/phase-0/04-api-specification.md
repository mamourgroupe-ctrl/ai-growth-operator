# Phase 0 — API Specification

**Status:** Proposed contract for approval. No routes are implemented in Phase 0.
**Version:** `v1`
**Base URL:** `https://api.<domain>/v1` (domain to be confirmed)

## 1. Conventions

- JSON request/response bodies; `Content-Type: application/json`.
- Auth: HttpOnly session cookie; every mutation also requires `X-CSRF-Token`.
- Dates: ISO-8601 (`2026-11-24T14:31:45Z`); dates without time use `YYYY-MM-DD`.
- IDs: UUID strings.
- Pagination: `limit` (default 20, max 100) and opaque `cursor`.
- Errors: RFC 7807 `application/problem+json`.
- Idempotency: `Idempotency-Key` required on `POST /campaigns` and `POST /ai/generate`.
- Rate limits: 100 requests/minute per user; AI generation quota per plan (default 10/hour, configurable).
- Breaking changes require `/v2`; additive fields are allowed in `/v1`.

## 2. Endpoint inventory

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/healthz` | none | Liveness |
| GET | `/readyz` | none | DB + worker readiness |
| POST | `/auth/register` | none | Create user + first tenant |
| POST | `/auth/login` | none | Start session |
| POST | `/auth/logout` | session | Revoke session |
| GET | `/auth/me` | session | Current user + memberships |
| GET | `/tenants` | session | Tenants for current user |
| POST | `/tenants` | session | Create additional tenant (owner) |
| GET | `/tenants/{tenant_id}` | member | Tenant detail |
| PATCH | `/tenants/{tenant_id}` | owner | Update tenant settings |
| GET | `/tenants/{tenant_id}/members` | member | List members |
| POST | `/tenants/{tenant_id}/members` | owner | Invite/add member |
| PATCH | `/tenants/{tenant_id}/members/{user_id}` | owner | Change role/status |
| GET | `/tenants/{tenant_id}/campaigns` | member | List campaigns |
| POST | `/tenants/{tenant_id}/campaigns` | editor+ | Create campaign |
| GET | `/tenants/{tenant_id}/campaigns/{id}` | member | Campaign detail |
| PATCH | `/tenants/{tenant_id}/campaigns/{id}` | editor+ | Update campaign |
| GET | `/tenants/{tenant_id}/content` | member | List content drafts |
| POST | `/tenants/{tenant_id}/content` | editor+ | Create/edit content manually |
| GET | `/tenants/{tenant_id}/content/{id}` | member | Content detail |
| PATCH | `/tenants/{tenant_id}/content/{id}` | editor+ | Update content |
| POST | `/tenants/{tenant_id}/content/{id}/approve` | editor+ | Mark approved |
| POST | `/tenants/{tenant_id}/ai/generate` | editor+ | Enqueue generation job |
| GET | `/tenants/{tenant_id}/ai/jobs/{job_id}` | member | Job status/result |
| GET | `/tenants/{tenant_id}/analytics/summary` | member | Aggregated metrics |
| POST | `/tenants/{tenant_id}/analytics/import` | editor+ | Manual metrics import |

Role shorthand: `member` = owner/editor/viewer; `editor+` = owner/editor.

## 3. Representative schemas

### `Tenant`
```json
{
  "id": "5e1f...",
  "name": "Café El Madania",
  "slug": "cafe-el-madania",
  "locale": "fr",
  "timezone": "Africa/Algiers",
  "currency": "DZD",
  "plan": "free"
}
```

### `Campaign`
```json
{
  "id": "9a3c...",
  "tenant_id": "5e1f...",
  "name": "Ramadan launch",
  "goal": "awareness",
  "status": "draft",
  "starts_on": "2026-12-01",
  "ends_on": "2026-12-31",
  "created_by": "7b2d...",
  "created_at": "2026-11-24T14:31:45Z"
}
```

### `ContentItem`
```json
{
  "id": "c41d...",
  "tenant_id": "5e1f...",
  "campaign_id": "9a3c...",
  "kind": "social_post",
  "locale": "fr",
  "title": null,
  "body": "Découvrez notre nouvelle carte...",
  "status": "in_review",
  "source": "ai_edited",
  "approved_by": null
}
```

### `GenerationJob`
```json
{
  "id": "f0a9...",
  "tenant_id": "5e1f...",
  "status": "succeeded",
  "kind": "social_post",
  "locale": "fr",
  "result_body": "Découvrez notre nouvelle carte...",
  "error_code": null,
  "created_at": "2026-11-24T14:31:45Z",
  "finished_at": "2026-11-24T14:31:49Z"
}
```

### Problem response
```json
{
  "type": "https://api.<domain>/problems/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "Your role cannot perform this action.",
  "instance": "/v1/tenants/5e1f.../content"
}
```

## 4. AI generation request

```json
POST /v1/tenants/{tenant_id}/ai/generate
Idempotency-Key: 6f1b...
X-CSRF-Token: ...

{
  "kind": "social_post",
  "locale": "fr",
  "campaign_id": "9a3c...",
  "brief": "Short post about a new mint tea special",
  "tone": "friendly"
}
```

Responses: `202 Accepted` with job representation; `409` for duplicate idempotency key with different payload; `429` when quota exceeded; `422` for validation failure.

Rules:
- `brief` max 2000 characters; server truncates or rejects longer input (reject preferred).
- Generated text max 4000 characters.
- The worker never receives credentials or tenant data except the brief and campaign name.
- Polling endpoint returns terminal state and result; no long-lived streaming in v1.

## 5. Analytics import

Phase 1 uses a manual JSON/CSV import with columns: `date`, `channel`, `impressions`, `clicks`, `conversions`, `spend`, `campaign_id` (optional). Imports are idempotent by `source_ref`. No external platform OAuth is part of v1.

## 6. Contract governance

- OpenAPI JSON is generated from FastAPI and committed as a schema artifact once Phase 1 starts.
- Contract tests validate example requests/responses against the schema.
- Any breaking change is rejected in CI unless the version path is bumped.
