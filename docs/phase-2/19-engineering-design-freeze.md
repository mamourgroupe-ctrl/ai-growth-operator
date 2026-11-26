# Phase 2.6 — Engineering Design Freeze

**Freeze objective:** produce a single, traceable specification that lets implementation begin without inventing product decisions or resolving major architectural contradictions during coding.  
**Freeze date:** 2026-11-24 UTC  
**Status:** Engineering baseline frozen for owner review. **Phase 2 implementation has NOT started and is NOT authorized by this document.**  
**Decision register:** `20-owner-decision-register.md`  
**Baseline documents:** `01-product-requirements-document.md` through `18-final-engineering-report.md`, as modified in the working tree by Phase 2.5 remediation.

## Status labels used in this document

| Label | Meaning |
|---|---|
| `OWNER_PROPOSED` | Preliminary owner choice recorded for review; not finally approved and not frozen. |
| `OWNER_APPROVED` | Final owner approval already recorded in Phase 0/1 or by explicit owner decision. |
| `FROZEN` | Technical baseline fixed for implementation planning; does not grant owner approval to a preliminary decision. |
| `DEFERRED` | Explicitly assigned to Phase 3 or later. |
| `BLOCKED` | Cannot be closed without external evidence or final owner confirmation. |

---

## 1. Freeze objective and scope

This document is the authoritative reconciliation layer for Phase 2. It does not replace the 18 baseline documents; it resolves cross-document ambiguity by assigning a status to each contested item. Where a baseline document uses “proposed”, “open” or historical wording, this freeze records the governing status.

No provider, storage vendor, pilot sector, numeric quota, FX source, or approval-authority change is approved here. The seven Phase 2.6 owner choices are recorded as `OWNER_PROPOSED`; `FROZEN` applies only to the technical baseline.

## 2. Repository baseline and branch

| Item | Value / status |
|---|---|
| Repository | `mamourgroupe-ctrl/ai-growth-operator` |
| Origin | `https://github.com/mamourgroupe-ctrl/ai-growth-operator.git` |
| Branch | `arena/5dc98770-ai-growth-operator` |
| Branch base | `main` commit `7820f29893815562613dd9c72ea4b0e51b956df3` |
| Initial HEAD for Phase 2.6 | `8da2f9aa161070ab2f4af7beca54b9bd41345e23` |
| Working tree at preflight | Dirty: 18 Phase 2.5 remediation edits under `docs/phase-2/`; preserved, not reset |
| PR #15 | OPEN, DRAFT, unmerged, head `8da2f9a`, base `main`, MERGEABLE; not modified |
| Issues #23/#24/#25 | OPEN, `[Phase 3]` titles, no milestone; inspected read-only, not modified |
| `main` branch protection | NOT VERIFIED (API 403); issue #14 remains open |

## 3. Product vision and confirmed scope

**Vision.** An Algerian SME describes its business once, generates Arabic/Darija/French marketing material with AI, validates it automatically and humanly, obtains approval, organizes approved work in an internal calendar, and prepares conversion material without external publishing or paid execution.

### Confirmed Phase 2 scope

| Capability | Status | Notes |
|---|---|---|
| Authentication and tenant management | `FROZEN` | Phase 1 foundation; existing root-level routes preserved |
| Tenant membership and roles | `FROZEN` | `owner`, `editor`, `viewer`; existing `is_arabic_reviewer` flag |
| Business profile | `FROZEN` | One profile per tenant |
| Product catalog | `OWNER_APPROVED` | DZD-only user-facing prices; no original foreign-currency display; offers and availability |
| Brand assets and guidelines | `FROZEN` | Minimal brand kit; private storage refs |
| Marketing strategy workspace | `FROZEN` | Internal strategy outputs only |
| AI marketing content generation | `FROZEN` | Provider-independent gateway; fake adapters until legal/benchmark gate |
| `ar`, `ar-DZ`, `fr` support | `FROZEN` | Language policy D-06 preserved from Phase 0/1 |
| Responsive Arabic RTL web interface | `FROZEN` | Web first; Android excluded |
| Image generation and editing abstraction | `FROZEN` | Capability through provider abstraction; provider not selected |
| Automated content validation | `FROZEN` | `block` findings non-overridable; `warn` overrides audited |
| Human Arabic content review | `FROZEN` | Review capability exists; staffing `BLOCKED` externally |
| Content approval and audit history | `FROZEN` | D-01 `OWNER_PROPOSED` owner-only baseline; final confirmation pending |
| Immutable/versioned approval snapshots | `FROZEN` | Append-only; invalidation on material change |
| Content calendar / content management | `FROZEN` | Internal dates only; no external publish |
| AI usage tracking and SaaS cost accounting | `FROZEN` | USD price snapshots are internal evidence; numeric limits `BLOCKED` pending administrator proposal and owner approval |

## 4. Phase 2 exclusions

All items below are `DEFERRED` from Phase 2. Their presence in a schema or utility column is not authorization to implement behavior.

- Android application.
- Advanced CRM.
- Direct social publishing.
- Paid advertising execution and ad expenditure.
- Advertising budget approval or budget increases.
- External advertising platform campaign execution.
- Automatic campaign launching.
- Paid-action outbox and reconciliation behavior.
- Advertising FX snapshots and conversion display.
- Automated ad optimization.
- Advanced analytics.
- Full subscription billing.
- Public landing-page hosting, custom domains and public lead ingestion.
- External notifications and reminder channels.
- Any external side effect created by AI output.

## 5. Phase 3 boundary

| Phase 3 item | Phase 2 treatment |
|---|---|
| Ad-spend approval / FX ceiling | No endpoint, table, state or UI |
| Advertising FX snapshots | Migration identifier `0010` reserved only; not in Phase 2 chain |
| External actions / state machines | No execution state machine; existing `outbox_events` remains legacy baseline |
| Paid-action outbox/reconciliation | Reserved deployment concept only; not used |
| Campaign launch / social publish | Explicit UI and API omission |
| Full responsive UI work beyond approved web subset | Deferred |
| Public landing pages, public lead capture, lead management and all lead tables/APIs/UI | `DEFERRED` to Phase 3 or later under preliminary D-02 |
| Billing and subscription enforcement | Deferred pending product decision |

## 6. Owner decision register

Full workshop detail is in `20-owner-decision-register.md`. The governing status table is repeated here so this freeze is self-contained.

| ID | Decision | Status | Owner confirmation | Frozen default / note |
|---|---|---|---|---|
| D-01 | Final content approval authority | `OWNER_PROPOSED` | Final confirmation pending | Owner only; editor prepares/submits; Arabic reviewer reports findings; viewer read-only; validation/review/approval remain distinct |
| D-02 | Landing pages and leads scope | `OWNER_PROPOSED` | Final confirmation pending | Internal create/edit/preview and existing draft/version history only; no public/external publishing; public lead ingestion, lead tables/APIs/UI and lead management `DEFERRED` |
| D-03 | Currency policy | `OWNER_PROPOSED` | Final confirmation pending | DZD-only user-facing; USD AI cost evidence internally; no conversion, no FX source; advertising FX `DEFERRED` |
| D-04 | AI usage quotas | `OWNER_PROPOSED` | Final confirmation pending | Configurable tenant quotas; system administrator proposes numbers, owner approves; no enforcement until approved values exist |
| D-05 | Pilot sector | `OWNER_PROPOSED` | Final confirmation pending | No sector selected; sectors are research hypotheses; sector-neutral foundations may proceed with synthetic fixtures |
| D-06 | Language policy | `OWNER_APPROVED` | Approved in Phase 0/1 requirements | MSA default, Darija distinct, French secondary, RTL; reviewer staffing `BLOCKED` externally |
| D-07 | AI provider selection | `OWNER_PROPOSED` | Final confirmation pending | No winner; selection only after documented quality/cost/latency/reliability/language/privacy/retention benchmark |
| D-08 | Storage provider selection | `OWNER_PROPOSED` | Final confirmation pending | No winner; selection after residency/security/encryption/backup/DPA/retention/egress/total-cost comparison |
| D-09 | Landing-page version representation | `FROZEN` | Engineering baseline | `landing_page_versions` owns approval status; no circular FK |
| D-10 | French UI breadth | `BLOCKED` | Owner input pending | Secondary locale/content style preserved; breadth undefined |
| D-11 | Viewer lead-PII redaction | `DEFERRED` | Lead functionality deferred | No Phase 2 lead data; redaction policy revisited with Phase 3 leads |
| D-12 | Arabic review for `fr` | `BLOCKED` | Owner input pending | Not required by default |
| D-13 | Image provenance/watermark | `BLOCKED` | Owner/licensing input pending | Metadata + UI badge now; external-use policy pending |
| D-14 | `main` branch protection | `BLOCKED` | API 403; issue #14 open | NOT VERIFIED; production gate only |
| D-15 | Cross-border transfer/legal position | `BLOCKED` | Counsel opinion pending | No compliance claim |
| D-16 | Non-material edit definition | `FROZEN` | Engineering baseline | Only internal labels non-material; body edits supersede |
| D-17 | Notification/SLA subsystem | `DEFERRED` | Not owner-confirmed as requirement | No notification component in MVP |
| D-18 | API version-prefix consolidation | `FROZEN` | Engineering baseline | Phase 1 root routes preserved; new Phase 2 routes under `/api/v1` |

## 7. Unresolved decisions

These must not be silently closed during implementation:

1. Final owner confirmation is still required for D-01–D-05, D-07 and D-08; their recorded status is `OWNER_PROPOSED`.
2. D-04 numeric quota values remain `BLOCKED` until system-administrator proposals receive owner approval.
3. D-05 sector selection remains `BLOCKED` until comparative evidence exists; sector-neutral foundations are not blocked.
4. D-07/D-08 provider and storage winners remain `BLOCKED` until benchmark/comparison evidence and legal review exist.
5. D-10, D-12 and D-13 remain `BLOCKED` on owner/licensing input.
6. D-14/D-15 remain `BLOCKED` on platform/legal evidence.
7. Lead functionality is `DEFERRED`; D-11 is revisited in Phase 3.

## 8. Architecture baseline

| Decision | Status | Frozen statement |
|---|---|---|
| System shape | `FROZEN` | Next.js web + FastAPI modular monolith + worker; one codebase and one PostgreSQL database |
| Module boundaries | `FROZEN` | `business`, `catalog`, `brand`, `onboarding`, `ai_gateway`, `content`, `validation`, `review`, `approval`, `creative`, `assets`, `landing_pages`, `usage`; `leads` module `DEFERRED` |
| Cross-module calls | `FROZEN` | In-process service interfaces and DB transactions; no service-to-service HTTP |
| AI gateway | `FROZEN` | `TextProvider`/`ImageProvider` abstraction, config-driven registry, fake adapters, no client provider selection |
| Job queue | `FROZEN` | Reuse Phase 1 `ai_generation_jobs` with `SKIP LOCKED`, leases, bounded retry, dead-letter, `uncertain` |
| Object storage | `FROZEN` | S3-compatible `ObjectStorage` abstraction; private by default; server-generated keys |
| Tenancy | `FROZEN` | Shared schema, transaction-local tenant context, RLS, composite FKs |
| External effects | `FROZEN` | No publishing, spend, approval-by-AI, or paid action in Phase 2 |

## 9. Canonical database design

### 9.1 Verified baseline facts

- `tenant_memberships.is_arabic_reviewer boolean NOT NULL DEFAULT false` already exists in `0001_initial`; no new column is required.
- `ai_generation_jobs.idempotency_key` and `uq_jobs_tenant_idempotency` already exist in `0001_initial`; do not recreate them.
- `tenants.base_currency`, `display_currencies`, locale and style fields already exist. Under preliminary D-03 they do not authorize conversion or foreign-currency display; user-facing display is DZD only.
- `audit_logs` already contains `approval_request_id`, `external_action_id` and `outbox_event_id`; the latter two are reserved columns, not Phase 2 behavior.
- `audit_logs.tenant_id` is retention-safe via `0002_audit_log_tenant_fk` with `ON DELETE RESTRICT`.

### 9.2 Canonical entity and relationship inventory

Status applies to the design statement, not to owner approval of a product decision.

| Logical entity | Status | Physical object | PK | Tenant ownership | Key columns / constraints | Indexes, FKs and uniqueness | Deletion / audit |
|---|---|---|---|---|---|---|---|
| Tenant | `FROZEN` | `tenants` | `id` uuid | Root object | `slug`, `base_currency`, `display_currencies`, locale/style fields, `deleted_at` | Unique `slug`; soft delete | Hard delete blocked while audit history exists; admin changes audited |
| User | `FROZEN` | `users` | `id` uuid | Global identity | `email`, `password_hash`, `full_name` | Unique `email` | Identity changes audited; no tenant business data |
| Membership | `FROZEN` | `tenant_memberships` | composite `(tenant_id, user_id)` | Tenant-scoped | `role`, `status`, existing `is_arabic_reviewer` | Membership-aware RLS; FKs to tenant/user | Soft/hard policy per Phase 1; role changes audited |
| Role permissions | `FROZEN` | Authorization policy over `role` + `is_arabic_reviewer` | N/A | Tenant membership-derived | Owner/editor/viewer/reviewer matrix | No client-supplied role; server-resolved | Every decision denial audited |
| Business profile | `FROZEN` | `business_profiles` | `id` uuid | `tenant_id NOT NULL` | One profile per tenant; audience/objectives/usps jsonb | Unique `tenant_id`; composite FK pattern; FORCE RLS | RESTRICT while referenced; tenant-edit audit |
| Product category | `FROZEN` | `product_categories` | `id` uuid | `tenant_id NOT NULL` | `slug` | Unique `(tenant_id, slug)`; RLS | Soft delete preferred; tenant-edit audit |
| Product | `FROZEN` | `products` | `id` uuid | `tenant_id NOT NULL` | `price_amount`, `currency`, offers, availability, `deleted_at` | Composite FK to category; index `(tenant_id,status,category_id)` | Soft delete; price/currency edits audited |
| Product image | `FROZEN` | `product_images` | `id` uuid | `tenant_id NOT NULL` | `product_id`, `asset_id` | Unique `(tenant_id,product_id,asset_id)`; FKs | Remove link before asset deletion; audit attachment |
| Brand asset | `FROZEN` | `brand_assets` | `id` uuid | `tenant_id NOT NULL` | `kind`, `asset_id`, `text_value` | FK to `tenant_assets`; RLS | Remove link before asset deletion; audit |
| Brand guideline | `FROZEN` | `brand_guidelines` | `id` uuid | `tenant_id NOT NULL` | `banned_claims`, disclaimers, tokens jsonb | One active row per tenant (proposed unique); RLS | Retain version history if added; audit changes |
| Onboarding session | `FROZEN` | `onboarding_sessions` | `id` uuid | `tenant_id NOT NULL` | `extracted_json`, `confidence_json`, `confirmed_json`, `status` | RLS; purge after confirmation or 30 days | Auto-purge per policy; confirmation events audited |
| Tenant asset | `FROZEN` | `tenant_assets` | `id` uuid | `tenant_id NOT NULL` | `storage_ref`, `mime_type`, `checksum_sha256`, `scan_status` | Unique `storage_ref`; index `(tenant_id,kind,created_at desc)` | Delete only after references removed; upload/use audited |
| Generation job | `FROZEN` | `ai_generation_jobs` | `id` uuid | `tenant_id NOT NULL` | Existing `idempotency_key`, locale/style/kind, status; add cost fields only if absent | Existing `uq_jobs_tenant_idempotency`; composite FKs; RLS | Retain for audit; no destructive delete |
| AI usage record | `FROZEN` | `ai_usage_records` | `id` uuid | `tenant_id NOT NULL` | `job_id`, `idempotency_key`, token/image counts, `status`, `price_snapshot_id` | One row per `(tenant_id,idempotency_key)`; FK to job/snapshot | Append/finalize only; cost audit retained |
| Usage counter | `FROZEN` | `usage_counters` | `id` uuid | `tenant_id NOT NULL` | `period_start`, counters, `updated_at` | Unique `(tenant_id,period_start)` | Retain for quota audit; no silent reset |
| AI model config | `FROZEN` | `ai_models`, `ai_provider_configs` | `id` uuid | System-admin only | `model_code`, capability, source/capture/revision, flags | No tenant write path; all changes audited | Disable rather than delete where referenced |
| AI price evidence | `FROZEN` | `ai_price_snapshots` | `id` uuid | System-admin only | USD unit prices, source URL, capture date, revision | Immutable; referenced by usage rows | Never mutate; retain for cost audit |
| Prompt template | `FROZEN` | `prompt_templates` | `id` uuid | System-admin only | `prompt_version`, `schema_version`, fixture version | Versioned; no secrets | Disable rather than delete where referenced |
| Content item | `FROZEN` | `content_items` | `id` uuid | `tenant_id NOT NULL` | metadata, `current_version_id`, `scheduled_for`, `validation_status`; no body | Index `(tenant_id,status,scheduled_for)` | Soft delete; status changes audited |
| Content version | `FROZEN` | `content_versions` | `id` uuid | `tenant_id NOT NULL` | **Canonical `body`**, `version`, `snapshot_hash` | Unique `(tenant_id,content_item_id,version)`; append-only | Never UPDATE/DELETE; supersession audited |
| Content validation | `FROZEN` | `content_validations` | `id` uuid | `tenant_id NOT NULL` | `content_version_id`, `rule_code`, severity, evidence | FK to version; index by version | Append-only evidence |
| Arabic review | `FROZEN` | `arabic_reviews` | `id` uuid | `tenant_id NOT NULL` | reviewer flag check, status, notes | FK to version and reviewer membership | Append-only; review status audited |
| Creative image metadata | `FROZEN` | `creative_assets` | `id` uuid | `tenant_id NOT NULL` | `job_id`, `asset_id`, prompt/model metadata | FKs; RLS | Remove link before asset deletion; audit |
| Content approval | `FROZEN` | `approval_requests` + `approval_snapshots` | request `id`, snapshot `id` | `tenant_id NOT NULL` | `kind='content'`, payload hash, decision fields; snapshot request FK only | Unique `(tenant_id,idempotency_key)` on request; unique `(tenant_id,approval_request_id,version)` on snapshot | Append-only snapshots; decisions audited |
| Approval audit events | `FROZEN` | `audit_logs` filtered to `approval.*` actions | `audit_logs.id` bigint | Tenant row or system event | actor, action, target, request id, metadata | Index `(tenant_id,action,created_at desc)` | Append-only; RESTRICT tenant hard delete |
| Content calendar entry | `FROZEN` | Logical view over `content_items.scheduled_for` | content item `id` | `tenant_id NOT NULL` | internal date/status only | No duplicate scheduling table | No separate deletion policy; item deletion applies |
| Landing page | `OWNER_PROPOSED` internal-only | `landing_pages` | `id` uuid | `tenant_id NOT NULL` | slug, seo, status, non-authoritative `current_version_id` | Unique `(tenant_id,slug)`; **no approved-version FK** | Conditional on D-02; audit events cover draft creation/editing, version creation, preview where appropriate, approval/rejection and approval invalidation. Publishing events and publication execution are `DEFERRED` to Phase 3 or later |
| Landing page version | `OWNER_PROPOSED` internal-only | `landing_page_versions` | `id` uuid | `tenant_id NOT NULL` | FK to page, `version`, `body jsonb`, `status` | Unique `(tenant_id,page_id,version)`; partial unique approved per page; append-only | Approval truth lives here; supersession audited |
| Lead | `DEFERRED` to Phase 3 or later | No Phase 2 table | N/A | N/A | Future lead fields are out of Phase 2 scope | No Phase 2 FK, index, API or UI | No Phase 2 retention decision required |
| Outbox event | `FROZEN` legacy | `outbox_events` | `id` uuid | `tenant_id NOT NULL` | existing aggregate/event type; Phase 3 reserved | Existing unique `(tenant_id,aggregate_id,event_type)` | No Phase 2 paid-action use |

### 9.3 Relationship matrix

| Parent | Child | Cardinality | Tenant-safe FK | Cycle status |
|---|---|---|---|---|
| `tenants` | `tenant_memberships` | 1:N | Composite tenant FKs | None |
| `tenants` | `business_profiles` | 1:1 | `tenant_id` unique | None |
| `product_categories` | `products` | 1:N | `(tenant_id, category_id)` | None |
| `products` | `product_images` | 1:N | `(tenant_id, product_id)` | None |
| `tenant_assets` | `product_images`, `brand_assets`, `creative_assets` | 1:N | `(tenant_id, asset_id)` | None |
| `business_profiles` | `onboarding_sessions` | 1:N | `(tenant_id, profile_id)` where applicable | None |
| `ai_generation_jobs` | `ai_usage_records` | 1:N | `(tenant_id, job_id)` | None |
| `ai_price_snapshots` | `ai_usage_records` | 1:N | `(tenant_id, snapshot_id)` or system snapshot id | None |
| `content_items` | `content_versions` | 1:N | `(tenant_id, content_item_id)` | None |
| `content_versions` | `content_validations`, `arabic_reviews` | 1:N | `(tenant_id, content_version_id)` | None |
| `approval_requests` | `approval_snapshots` | 1:N | `(tenant_id, approval_request_id)` | One-directional; no request→snapshot FK |
| `landing_pages` | `landing_page_versions` | 1:N | `(tenant_id, page_id)` | One-directional; no page→approved-version FK |
| `landing_pages` | `leads` | N/A | No Phase 2 lead table or FK | `DEFERRED` |
| `tenants` | `audit_logs` | 1:N | FK with `ON DELETE RESTRICT` | None |

### 9.4 Migration dependency order

| Order | Revision | Phase | Dependency |
|---|---|---|---|
| Existing | `0001_initial` | Phase 1 | Base identity, tenants, membership, job queue, outbox, audit |
| Existing | `0002_audit_log_tenant_fk` | Phase 1 | Depends on `0001_initial` |
| 1 | `0003_business_catalog_brand` | Phase 2 | Depends on `0002`; tenant tables + RLS in same revision |
| 2 | `0004_assets_and_onboarding` | Phase 2 | Depends on `0003`; adds FKs to business/brand tables |
| 3 | `0005_ai_gateway_usage` | Phase 2 | Depends on `0004`; reuses existing job idempotency |
| 4 | `0006_content_and_validation` | Phase 2 | Depends on `0005`; canonical content body |
| 5 | `0007_approval` | Phase 2 | Depends on `0006`; snapshot FK one-directional |
| 6 | `0008_landing_pages_internal` | Phase 2 `OWNER_PROPOSED` scope | Depends on `0007`; page versions own approval status; no `leads` table |
| 7 | `0009_indexes_and_constraints` | Phase 2 | Depends on prior applied revisions; last Phase 2 revision |
| Deferred | `0010_advertising_fx` | Phase 3 | Not in the Phase 2 upgrade chain |

**Downgrade honesty.** CI target is `upgrade head`, `downgrade -1`, `upgrade head` on a clean DB with `ago_app`. A verified full `downgrade base` is not claimed. The Phase 2 chain contains no lead data; destructive rollback of snapshots requires an owner-approved backup procedure.

### 9.5 Remaining schema risks

- Landing page tables are `OWNER_PROPOSED`; all lead tables, APIs and UI are `DEFERRED` and must not be implemented in Phase 2.
- Numeric quota values remain `BLOCKED` until system-administrator proposal and owner approval; counters can be defined but not enabled with invented values.
- Audit and usage retention periods remain external legal decisions; lead retention is `DEFERRED` with lead functionality.
- `ai_price_snapshots` accuracy depends on re-verified official price pages; no live benchmark was run.
- RLS catalog verification and migration cycle are future implementation gates, not executed tests.
- `tenants.display_currencies` exists but no conversion or FX source is authorized in Phase 2.

## 10. API contract baseline

### 10.1 Common contract applied to every endpoint below

| Dimension | Frozen rule |
|---|---|
| Prefix | New Phase 2 endpoints use `/api/v1`; existing Phase 1 root routes remain unchanged (D-18) |
| Authentication | Session cookie + CSRF for browser clients; Phase 1 auth baseline; public endpoints only if D-02 approves |
| Tenant context | Resolved server-side from membership/session; `tenant_id` never accepted from client input |
| Role permission | Explicit per endpoint in the tables below; server-side dependency check; no client role escalation |
| Request schema | Pydantic allowlists; no provider/model/URL/budget/FX/campaign fields from clients |
| Response schema | JSON only; no raw provider error, secret, prompt text or unnecessary PII |
| Errors | Stable codes: `400 validation_error`, `401 unauthenticated`, `403 forbidden`, `404 not_found`, `409 conflict/invalid_state`, `422 schema_invalid`, `429 rate_limited/quota_exceeded`, `503 provider_unavailable` |
| Idempotency | `Idempotency-Key` header required on cost-generating or decision-side-effect requests; replay returns original result without a second side effect |
| Validation | `block` findings cannot be overridden; `warn` overrides require owner reason and audit evidence |
| Audit | Decisions, generation, uploads, asset use, config changes and publish eligibility events append-only |
| Pagination | `limit` 1–100 default 20; `cursor`; deterministic `created_at,id` ordering |
| Clock | UTC `timestamptz`; no client-supplied timestamps for audit rows |

### 10.2 Existing Phase 1 endpoints — `FROZEN`, unchanged

| Method and path | Auth | Tenant context | Role | Notes |
|---|---|---|---|---|
| `POST /auth/register` | No | Creates tenant/member | N/A | Phase 1 baseline |
| `POST /auth/login` | No | Session established | N/A | Phase 1 baseline |
| `POST /auth/logout` | Yes | Session-scoped | Any authenticated | Phase 1 baseline |
| `GET /auth/me` | Yes | Session-scoped | Any authenticated | Phase 1 baseline |
| `GET/POST/PATCH /organizations/{org_id}/...` | Yes | Server-resolved membership | Per Phase 1 RBAC | Includes members and `is_arabic_reviewer` management |
| `GET /healthz`, `GET /readyz` | No | None | N/A | Config-free health only |

### 10.3 Phase 2 endpoints — `FROZEN` engineering baseline

| Method and path | Auth | Role | Idempotency | Validation / audit behavior |
|---|---|---|---|---|
| `GET/PATCH /api/v1/business/profile` | Yes | Owner/editor; viewer GET | No | Known fields only; audit PATCH |
| `POST /api/v1/business/onboarding/conversations` | Yes | Owner/editor | No | Creates session; audit creation |
| `POST /api/v1/business/onboarding/conversations/{id}/messages` | Yes | Owner/editor | No | Returns proposals/confidence/missing fields; no fact write |
| `POST /api/v1/business/onboarding/conversations/{id}/confirm` | Yes | Owner/editor | Yes | Writes only confirmed fields; audit each field |
| `GET/POST/PATCH/DELETE /api/v1/catalog/products` | Yes | Owner/editor; viewer GET | POST yes | Price/currency required; soft delete; audit mutations |
| `GET/POST /api/v1/catalog/categories` | Yes | Owner/editor; viewer GET | POST yes | Unique slug per tenant; audit |
| `GET/POST /api/v1/brand/assets` | Yes | Owner/editor; viewer GET | POST yes | Signed URL flow; scan gate; audit upload/use |
| `POST /api/v1/assets/uploads` | Yes | Owner/editor | Yes | Server-generated key; short signed URL; audit |
| `GET/PATCH /api/v1/brand/guidelines` | Yes | Owner/editor; viewer GET | No | Banned claims/disclaimers; audit changes |
| `POST /api/v1/ai/generations` | Yes | Owner/editor | **Required** | Tenant-owned refs; quota reservation; audit job creation |
| `GET /api/v1/ai/generations/{job_id}` | Yes | Owner/editor; viewer status only if allowed | No | Job state; no raw provider error |
| `GET /api/v1/ai/usage` | Yes | Owner | No | Usage/cost from snapshots; no secrets |
| `GET/POST /api/v1/content/items` | Yes | Owner/editor; viewer GET | POST yes | Metadata only; audit status changes |
| `POST /api/v1/content/items/{id}/versions` | Yes | Owner/editor | Yes | Canonical body inserted; append-only audit |
| `POST /api/v1/content/versions/{id}/validate` | Yes | Owner/editor | No | Immutable validation row; block/warn semantics |
| `POST /api/v1/content/versions/{id}/arabic-review` | Yes | Editor with reviewer flag | Yes | Review findings only; never final approval |
| `POST /api/v1/content/versions/{id}/submit-for-approval` | Yes | Owner/editor | Yes | Requires no blocks and required review; snapshot request |
| `GET /api/v1/approval/requests` | Yes | Owner/editor/viewer | No | Status-filtered; viewer sees metadata only |
| `POST /api/v1/approval/requests/{id}/decide` | Yes | **Owner-only baseline** | **Required** | Reason required for reject/changes; audit decision |
| `GET /api/v1/calendar/items?from=&to=` | Yes | All roles | No | Internal dates/status only; no publish action |
| `POST /api/v1/creative/images` | Yes | Owner/editor | **Required** | Ownership/scan checks; cost reservation; audit |
| `GET /api/v1/creative/images/{id}` | Yes | Owner/editor; viewer GET | No | Short signed read URL |
| `OWNER_PROPOSED` `GET/POST /api/v1/landing/pages` | Yes | Owner/editor; viewer GET | POST yes | Internal create/edit only; audit |
| `OWNER_PROPOSED` `GET/POST /api/v1/landing/pages/{id}/versions` | Yes | Owner/editor; viewer GET | POST yes | Backed by `landing_page_versions`; draft/version history only |
| `DEFERRED` `POST /api/v1/landing/pages/{id}/internal-publish` | Future only | Future owner decision | N/A | Not a Phase 2 executable endpoint |
| `DEFERRED` `POST /api/v1/public/leads` | Future only | N/A | N/A | No Phase 2 public lead ingestion |
| `DEFERRED` `GET /api/v1/leads` | Future only | N/A | N/A | No Phase 2 lead management API |

No endpoint accepts advertising budget, FX rate, external platform target, campaign launch, provider, model, `tenant_id` or storage URL from client input.

## 11. Security and privacy baseline

### 11.1 Frozen technical controls

| Control | Status | Frozen statement |
|---|---|---|
| RLS | `FROZEN` | Every tenant-owned table uses `ENABLE` + `FORCE ROW LEVEL SECURITY` with `USING` and `WITH CHECK` |
| Policy combination | `FROZEN` | Policies are `PERMISSIVE` by default and OR-combine; `RESTRICTIVE` policies AND-combine |
| Runtime role | `FROZEN` | `ago_app` is non-superuser, `NOBYPASSRLS`, and explicitly granted privileges; grants are separate from policies |
| Tenant context | `FROZEN` | Server-derived transaction-local `set_config('app.current_tenant_id', ..., true)` |
| RBAC | `FROZEN` | Owner/editor/viewer + existing reviewer flag; D-01 `OWNER_PROPOSED`, final confirmation pending |
| Authentication | `FROZEN` | Phase 1 sessions, password hashing, CSRF; no new auth scheme in Phase 2 |
| Secrets | `FROZEN` | Secret manager / GitHub Environments only; no secrets in repo, logs or OpenAPI examples |
| Transport | `FROZEN` | HTTPS; short-lived signed URLs; no public object URLs |
| Encryption at rest | `FROZEN` | Provider-managed at-rest encryption expected; provider-specific evidence `BLOCKED` |
| File upload | `FROZEN` | MIME + magic-byte allowlist, checksum, size cap, scan status gate |
| Input validation | `FROZEN` | Pydantic allowlists, locale/style enums, numeric price validation |
| Prompt injection | `FROZEN` | Untrusted data delimiting, no tools, schema validation, adversarial tests |
| Audit | `FROZEN` | Append-only events for decisions, jobs, uploads, config and publish eligibility |
| Logging | `FROZEN` | No secrets, raw prompts, provider errors or unnecessary user PII; no lead PII exists in Phase 2 |
| Backup/recovery | `FROZEN` | Tenant-scoped restore test and runbook required before production |
| Synthetic data | `FROZEN` | Local, CI and staging use synthetic fixtures only |
| Scanning | `FROZEN` | Existing CI bandit + secret scanner; dependency/vulnerability scanning remains a proposed enhancement |
| Rate limiting | `FROZEN` | Per-tenant endpoint limits and AI quota checks; numeric values `BLOCKED` until system-administrator proposal and owner approval |

### 11.2 Privacy readiness checklist

- [ ] Legal counsel position recorded for Law 25-11 and Law 18-07 as amended.
- [ ] DPO / processing-register / automated-log obligations determined.
- [ ] Provider DPA, subprocessors, retention and ZDR evidence recorded.
- [ ] Cross-border transfer authorization position recorded for each provider.
- [ ] Data categories allowed to leave tenant DB explicitly listed.
- [ ] Lead retention, lead-PII redaction and public lead privacy notice are `DEFERRED` with lead functionality; no Phase 2 artifact required.
- [ ] Backup/restore runbook tested before production.
- [ ] Branch protection verified before production (D-14).

**No legal compliance claim is made.** These are technical controls and open legal gates.

## 12. AI provider strategy

| Requirement | Status | Freeze statement |
|---|---|---|
| Provider selection | `OWNER_PROPOSED` / `BLOCKED` | No winner selected; select only after documented benchmark and legal review |
| Model identifiers | `FROZEN` | Candidate IDs and exact API identifiers must be confirmed before benchmark; aliases are not revisions |
| Prompt/schema versioning | `FROZEN` | Every generation records prompt template version and schema version |
| Input/output accounting | `FROZEN` | Actual token counts recorded; no assumed token parity across providers |
| Cache normalization | `FROZEN` | Record `none`/implicit/explicit, write/read tokens; do not compare mismatched cache states |
| Latency/error rate | `FROZEN` | Same harness, same network location; record p50/p95, 429/5xx/timeouts/retries |
| Structured outputs | `FROZEN` | JSON Schema requested and locally re-validated; provider support verified before run |
| Arabic MSA quality | `FROZEN` | Mandatory benchmark criterion with blind review; no winner before run |
| Darija quality | `FROZEN` | Mandatory benchmark criterion; distinct `ar-DZ` scoring; no MSA-only output accepted |
| French quality | `FROZEN` | Mandatory benchmark criterion; measured separately; review requirement D-12 `BLOCKED` |
| Fallback | `FROZEN` | Only to benchmarked models in same locale/style; otherwise fail closed |
| Real personal data | `FROZEN` | Blocked until legal/provider gate; synthetic only now |

**Benchmark execution plan (not executed).** Freeze fixture version, hashes, prompt/schema/validator versions, exact model IDs and dated revisions; run identical `T1`–`T5` tasks with three repeats; record output quality, Arabic MSA, Algerian Darija, French, cost, latency, reliability, privacy and data-retention evidence with tokens, cache state, errors and dated price snapshots; blind-review language outputs; publish results before any selection. No paid API call or benchmark is authorized in Phase 2.6. No winner is declared.

## 13. Image provider strategy

| Capability | Status | Freeze statement |
|---|---|---|
| Provider selection | `OWNER_PROPOSED` / `BLOCKED` | No winner selected; same D-07 benchmark criteria apply |
| Generation vs editing | `FROZEN` | Separate `G` and `E` task families and scores; no cross-capability claim |
| Reference fidelity | `FROZEN` | Owned synthetic reference only; product shape/label preserved |
| Brand consistency | `FROZEN` | Palette/style rubric scored separately |
| Product fidelity | `FROZEN` | No misleading product depiction; banned-claim scan |
| Arabic text rendering | `FROZEN` | Separate banner task; unsupported capability may be documented, not assumed |
| Commercial licensing | `BLOCKED` | License and indemnity review required; BFL Kommunity License not yet approved |
| Retention / ZDR | `BLOCKED` | Per-model evidence required; `GPT-Image-2.6` ZDR eligibility unresolved |
| Provenance | `BLOCKED` | Metadata + UI badge baseline; watermark/external-use policy D-13 open |
| Output safety | `FROZEN` | Scan + validation + human approval before any landing-page use |

## 14. Storage strategy

| Requirement | Status | Freeze statement |
|---|---|---|
| Abstraction | `FROZEN` | S3-compatible `ObjectStorage`; provider-neutral `storage_ref` |
| Private by default | `FROZEN` | Private buckets, no public ACL, short signed URLs |
| Server-generated keys | `FROZEN` | `tenant/{tenant_id}/{kind}/{uuid}`; clients never choose keys or buckets |
| Encryption | `FROZEN` / `BLOCKED` | TLS in transit and provider at-rest encryption required; key ownership/DPA evidence pending |
| Tenant isolation | `FROZEN` | Ownership check + RLS before any asset use |
| Backup / recovery | `FROZEN` / `BLOCKED` | Versioning/lifecycle/restore behavior must be mapped before production |
| Lifecycle | `FROZEN` | IA/Glacier retrieval and minimum-duration costs separated from storage price |
| File size / transforms | `FROZEN` | 10 MB image cap baseline; transform limits require owner/CI approval |
| Monitoring | `FROZEN` | Object count, bytes, signed-URL errors, scan failures, egress trends |
| Residency / DPA | `BLOCKED` | Blocking; no provider selected |

Pricing is separated into storage, requests, retrieval and egress. Selection requires data residency, security, encryption, backup/recovery, DPA, retention, egress cost and total operating cost evidence. Corrected estimates remain illustrative; no provider assessment or winner is asserted.

## 15. Deployment strategy

| Item | Status | Freeze statement |
|---|---|---|
| Responsive web first | `FROZEN` | Next.js web; no Android in Phase 2 |
| Deployables | `FROZEN` | `web`, `api`, `worker`; reconciliation reserved for Phase 3 |
| Environments | `FROZEN` | local, CI, staging, production separated |
| Data policy | `FROZEN` | Synthetic only below production; no production-derived data without separate approval |
| Secrets | `FROZEN` | Outside source control; rotation policy proposed |
| Migration | `FROZEN` | Controlled step; backup and rollback plan before production |
| Feature flags | `FROZEN` | Default-off; no advertising or paid-outbox flags in Phase 2 |
| Hosting outside Algeria | `BLOCKED` | Subject to legal/privacy approval |
| Production deployment | `DEFERRED` | No production deployment in Phase 2.6 |
| Observability | `FROZEN` | Job depth/age, error rate, p95 latency, quota counters, cost counters |

## 16. Testing and QA baseline

| Layer | Status | Required evidence before implementation is accepted |
|---|---|---|
| Unit | `FROZEN` | Validators, cost math, prompt builders, state machines |
| API/contract | `FROZEN` | Role matrix, OpenAPI schema, stable error codes |
| DB/RLS | `FROZEN` | RLS catalog check, composite FK checks, `ago_app` cross-tenant negatives |
| Migration | `FROZEN` | `upgrade head`, `downgrade -1`, `upgrade head`; no claimed full downgrade |
| Worker | `FROZEN` | Leases, retry bounds, dead-letter, idempotency, `uncertain` |
| Fake provider integration | `FROZEN` | Success, schema failure, timeout, rate limit, missing usage |
| Validation/approval negatives | `FROZEN` | No block override, no editor decide, no stale approval reuse |
| Prompt injection | `FROZEN` | Approval/publish/spend strings never trigger actions |
| Privacy | `FROZEN` | No user PII in prompts/logs; no lead PII in Phase 2; synthetic fixtures only |
| Benchmark | `FROZEN` | Corrected fixtures; no result claimed yet |
| CI current state | `FROZEN` | Existing `lint`, `test`, `security` jobs only; run `45565465339` on `8da2f9a` reported success |
| Local pytest | `NOT RUN` | pytest unavailable in audit environment; no local test claim |

Current CI does **not** include RLS catalog, OpenAPI role matrix, migration cycle or fake-provider integration; these are proposed future gates.

## 17. Phase 2 acceptance matrix

| Area | Testable acceptance criterion | Status | Evidence method |
|---|---|---|---|
| Product | Every confirmed feature maps to a documented endpoint/schema and test | `FROZEN` | Traceability in §3, §9, §10 |
| Product | Landing pages are internal-only; lead and publish features are `DEFERRED` pending final D-02 confirmation | `FROZEN` | Feature-flag + API negative tests |
| Product | Every exclusion has no endpoint, table behavior or UI affordance | `FROZEN` | Static scan + UI review |
| Architecture | One FastAPI modular monolith, one PostgreSQL DB, separate worker | `FROZEN` | Architecture review |
| Architecture | Provider abstraction supports fake adapters and no client selection | `FROZEN` | Gateway tests |
| Database | `content_versions.body` is the only canonical body | `FROZEN` | Schema check + code review |
| Database | No approval snapshot or landing-page circular FK | `FROZEN` | Schema catalog test |
| Database | Tenant isolation testable on every tenant table | `FROZEN` | RLS catalog + cross-tenant tests |
| Database | Migration order coherent through `0009`; `0010` absent | `FROZEN` | Alembic cycle |
| API | Endpoints match frozen tables and roles | `FROZEN` | OpenAPI contract tests |
| API | Idempotent generation/decision replay creates no second side effect | `FROZEN` | Integration tests |
| API | Error codes stable and secret-free | `FROZEN` | Contract tests |
| Security | PERMISSIVE/RESTRICTIVE and FORCE RLS semantics implemented as documented | `FROZEN` | Policy SQL review + tests |
| Security | Tenant context server-derived and transaction-local | `FROZEN` | Negative tests |
| Security | Synthetic-only data below production | `FROZEN` | CI/staging audit |
| AI | Usage accounting records reservation, actual usage and snapshot price | `FROZEN` | Fake-provider tests |
| AI | Provider selection only after benchmark + legal evidence | `FROZEN` | ADR gate |
| Operations | Backup/restore runbook and monitoring exist before production | `FROZEN` | Runbook review |

`FROZEN` means testable criteria exist. It does **not** mean tests have been executed.

## 18. External dependencies

1. D-07 benchmark results and exact model revisions: quality, MSA, Darija, French, cost, latency, reliability, privacy and retention.
2. D-08 storage comparison evidence: residency, security, encryption, backup/recovery, DPA, retention, egress and total cost.
3. Algerian legal counsel opinion on Law 25-11, Law 18-07 as amended, ANPDP and transfers.
4. Provider DPA, subprocessor lists, retention/ZDR and commercial-use terms.
5. Human Arabic/Darija reviewer availability and approved rubric.
6. Final owner confirmation for D-01–D-05, D-07 and D-08; owner input for D-10, D-12 and D-13.
7. `main` branch protection verification (D-14, issue #14).
8. System-administrator numeric quota proposals and owner approval (D-04).
9. Pilot evidence if a sector is later selected; not required for sector-neutral foundations.
10. Malware-scanning integration choice and production secret management.

## 19. Known risks

| Risk | Status | Mitigation |
|---|---|---|
| Owner authority ambiguity | `OWNER_PROPOSED` | D-01; owner-only baseline unchanged pending final confirmation |
| Landing scope creep | `OWNER_PROPOSED` | D-02; internal create/edit/preview only; leads and publishing `DEFERRED` |
| Misleading currency display | `OWNER_PROPOSED` | D-03; DZD only user-facing; no conversions or invented rates |
| Cost overrun | `BLOCKED` | D-04 reservation/finalization; numeric caps blocked until owner approval |
| Unproven Darija quality | `BLOCKED` | D-07 benchmark + blind native review before locale enablement |
| Unselected providers | `BLOCKED` | Fake adapters; D-07 benchmark and legal gates |
| Unresolved residency | `BLOCKED` | D-08 blocking criterion for production/public launch |
| Branch protection unverified | `BLOCKED` | Production gate; issue #14 |
| Conditional schema shipped early | `DEFERRED` | Migration `0008` contains landing pages only; leads excluded |
| Circular FK regression | `FROZEN` | Version-owned approval status; catalog test |
| Stale approval | `FROZEN` | Version supersession + snapshot hash |
| Prompt injection | `FROZEN` | No tools, schema validation, adversarial tests |
| Local test evidence absent | `BLOCKED` | CI evidence distinguished; local pytest not run |

## 20. Implementation entry criteria

### 20.1 Mandatory before Phase 2 implementation begins

The gate uses four distinct states. `DOCUMENTED` means the requirement exists in these documents. `EVIDENCE AVAILABLE` means objective supporting evidence is present. `OWNER APPROVED` means a final owner decision is recorded. `ENGINEERING VERIFIED` means an implementation acceptance check has actually passed. A preliminary owner choice is `OWNER_PROPOSED`; it is **not** `OWNER APPROVED`.

1. **Freeze and decision register final approval** — `BLOCKED`: not recorded; seven decisions remain `OWNER_PROPOSED`.
2. **Phase 2/Phase 3 boundary final confirmation** — `BLOCKED`: §3–§5 document the boundary, including D-02 lead/publish `DEFERRED` scope, but final owner confirmation is pending.
3. **D-01 final approval authority** — `BLOCKED`: D-01 is `OWNER_PROPOSED`; no code may encode an editor-final-approval variant.
4. **D-02 preliminary scope recorded** — `DOCUMENTED`: internal create/edit/preview and `DEFERRED` leads/publishing are recorded; this is not owner approval.
5. **D-03 preliminary currency rule recorded** — `DOCUMENTED`: DZD user-facing display, internal USD cost evidence and no conversion/FX source are recorded; this is not owner approval.
6. **D-04 quota policy recorded** — `DOCUMENTED`; numeric values `BLOCKED` until system-administrator proposal and owner approval. No live enforcement is permitted before approval.
7. **D-05 sector approach recorded** — `DOCUMENTED`; sector-neutral foundations may proceed with synthetic fixtures, while sector-specific rules are `BLOCKED` pending selection.
8. **Database design internally consistent** — `DOCUMENTED`: single canonical body, no circular FKs and coherent `0003`–`0009` chain; no migration execution is claimed.
9. **API contracts internally consistent** — `DOCUMENTED`: path prefixes, roles, idempotency and stable errors; OpenAPI contract tests are not executed.
10. **Security controls documented** — `DOCUMENTED` for §11; security tests are future acceptance evidence, not current proof.
11. **Privacy/legal blockers** — `BLOCKED`: explicitly classified as `BLOCKED`; no compliance claim is made.
12. **Provider-neutral strategy** — `DOCUMENTED` / `FROZEN`: no provider is selected; benchmark and evidence gates are `BLOCKED`.
13. **Storage/deployment requirements** — `BLOCKED`: requirements are documented, but production residency and DPA evidence remain external.
14. **Acceptance criteria in §17** — `DOCUMENTED`: criteria are testable; tests have not been executed.
15. **No critical unresolved architecture contradiction** — `DOCUMENTED`: known open items are owner decisions or external gates, not silent contradictions.

| # | Criterion | Required evidence or decision | Current status | Blocks implementation? |
|---|---|---|---|---|
| 1 | Freeze/register approval | Explicit owner approval of docs 19 and 20 | `BLOCKED` — not recorded | Yes |
| 2 | Phase 2/Phase 3 boundary | Final owner confirmation of §3–§5 | `BLOCKED` — preliminary only | Yes |
| 3 | D-01 authority | Final owner confirmation of owner-only decision | `BLOCKED` — `OWNER_PROPOSED` | Yes |
| 4 | D-02 documented scope | Register entry plus Phase 2 docs | `DOCUMENTED` — not approval | No by itself; item 2 gates |
| 5 | D-03 documented currency rule | Register entry plus Phase 2 docs | `DOCUMENTED` — not approval | No by itself; item 2 gates |
| 6 | D-04 numeric limits | Administrator proposal and owner approval | `BLOCKED` — values absent | Yes |
| 7 | D-05 sector-neutral path | Register entry; no sector-specific rules enabled | `DOCUMENTED`; sector-specific rules `BLOCKED` | No for sector-neutral work; Yes for sector-specific work |
| 8 | Database consistency | Design review; later migration tests | `DOCUMENTED` — not code-verified | Yes (implementation acceptance) |
| 9 | API consistency | Design review; later contract tests | `DOCUMENTED` — not code-verified | Yes (implementation acceptance) |
| 10 | Security controls | Design review; later negative tests | `DOCUMENTED` — not code-verified | Yes (implementation acceptance) |
| 11 | Privacy/legal evidence | Counsel/transfer/retention evidence | `BLOCKED` — external | Yes |
| 12 | Provider evidence | Benchmark, privacy, retention and legal evidence | `BLOCKED` — no winner | Yes for real provider integration |
| 13 | Storage evidence | Residency, DPA and operating-cost comparison | `BLOCKED` — external | Yes for production/public launch |
| 14 | Acceptance criteria | Executed §17 test evidence | `DOCUMENTED` — not executed | Yes (implementation acceptance) |
| 15 | Architecture contradiction check | Completed documentation review | `DOCUMENTED` — no critical contradiction found | No |

External blockers also include provider benchmark/ZDR/DPA evidence, storage residency/DPA evidence, numeric quota approval and `main` branch protection verification (#14), as detailed in §20.2–§20.4.

**Current result:** criteria 1, 2, 3, 6, 11 and 13 are `BLOCKED`; criteria 4, 5, 7–10, 14 and 15 are `DOCUMENTED` only and do not constitute owner approval or engineering verification; criterion 12 has a documented `FROZEN` strategy but remains `BLOCKED` for real provider integration. Implementation is therefore not authorized.

### 20.2 Mandatory before production

- Legal/transfer position, DPAs and retention approvals.
- Storage residency and backup/restore runbook.
- Numeric quota configuration and cost monitoring.
- `main` branch protection verification (#14).
- Real provider keys in secret manager; no keys in source.
- Release gates in §16 green with real evidence, not proposed status.

### 20.3 Mandatory before external provider integration

- Benchmark evidence for the exact model/revision and locale.
- Legal review of data categories, retention, ZDR and transfers.
- DPA/subprocessor inventory.
- Rate-limit and cost controls configured.
- No real personal data before all above are complete.

### 20.4 Mandatory before public launch

- D-02 public-publishing approval and security review.
- Abuse protection, CAPTCHA/spam policy and rate limits.
- Privacy notice, consent and retention rules.
- Tenant-safe public slug resolution tests.
- Monitoring and incident runbook.

### 20.5 Can be deferred beyond MVP

- Public landing pages and custom domains.
- Pilot-sector final selection if MVP uses synthetic validation only.
- Provider and storage selection if only fake adapters are enabled.
- Notification/SLA subsystem.
- Watermark policy for external image use.
- Full subscription billing and all advertising/FX capabilities.

## 21. Change-control procedure

Any change to product scope, database schema, API contracts, tenant isolation, approval authority, financial governance or external integrations requires:

1. A written change request with ID and date.
2. Reason and evidence.
3. Impact analysis across product, architecture, DB, API, security and operations.
4. Affected documents listed, including this freeze and the decision register.
5. Migration impact, including upgrade/downgrade and data-safety effects.
6. Security impact, including RLS, audit and PII effects.
7. Backward-compatibility impact, including existing Phase 1 root routes.
8. Owner approval where product, approval-authority or financial decisions are affected.
9. A new decision-register entry or supersession note; frozen decisions must not be silently edited.
10. Re-run of §17 acceptance matrix and updated readiness verdict.

## 22. Final readiness verdict

**Engineering reconciliation:** complete. The 18 baseline documents are reconciled by this freeze; verified baseline facts from `0001_initial` and the API implementation were incorporated; the landing-page version inconsistency, migration-chain ordering and API prefix coexistence are resolved in documentation.

**Owner decisions:** seven preliminary choices are recorded as `OWNER_PROPOSED`. None is `OWNER_APPROVED` or `FROZEN`; final owner confirmation remains required.

**Implementation:** not authorized. This document freezes only the technical baseline; it does not grant owner approval and does not claim Phase 2 implementation readiness.

**Verdict:** technical baseline `FROZEN`; owner decisions `OWNER_PROPOSED` pending final approval.
