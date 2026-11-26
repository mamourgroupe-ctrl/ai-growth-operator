# Phase 2 — Updated Database Design and Entity Relationships

**Status:** Proposed. No migrations created in this planning task.  
**Baseline:** Phase 1 tables `users`, `sessions`, `tenants`, `tenant_memberships`, `ai_generation_jobs`, `outbox_events`, `audit_logs` plus Alembic `0001_initial`, `0002_audit_log_tenant_fk`.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Shared schema, UUID IDs, `timestamptz`, RLS `USING`/`WITH CHECK` on tenant-owned tables, `ago_app` runtime role, append-only audit/outbox, immutable snapshots. |
| Proposed decisions | New tables listed below; asset registry; validation results; onboarding sessions; product images. |
| `BLOCKED` / `DEFERRED` | Final owner confirmation for D-01–D-05, D-07, D-08; exact retention, D-04 numeric values and storage/legal evidence; lead/PII redaction `DEFERRED`. |
| External dependencies | Legal review for lead/PII retention and provider transfer; storage provider selection; owner authorization for issue amendments. |
| Confirmed boundary | Advertising FX snapshots, paid outbox/reconciliation, external execution state machines and advertising financial authorization are Phase 3 only. AI price snapshots in this document are SaaS cost evidence, not advertising FX. |
| Risks | Over-normalization; nullable tenant FK; unscanned assets; stale price snapshots. |

## 1. Tenant-owned tables (must have RLS)

Every table below: `tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT/ CASCADE per policy`, `ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY`, policy `tenant_isolation` with:

```sql
USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
```

Exception: `tenants` and `tenant_memberships` keep Phase 1 membership-aware policies. `tenant_memberships.is_arabic_reviewer boolean NOT NULL DEFAULT false` **already exists in `0001_initial`** and is the canonical location for the reviewer flag referenced by `05-api-contracts.md §1` and `12-approval-workflow-spec.md §1`. It grants review capability only, never final approval. No new migration column is needed for this flag.

**RLS semantics (verification correction):** a policy created without `RESTRICTIVE` is `PERMISSIVE` by default; multiple permissive policies combine with OR, while restrictive policies combine with AND. `FORCE ROW LEVEL SECURITY` makes policies apply even to the table owner; it does **not** grant table privileges. The runtime role `ago_app` must be non-superuser, `NOBYPASSRLS`, and still receive explicit `GRANT`s. Tenant context is transaction-local via `set_config('app.current_tenant_id', <uuid>, true)`, not a client-supplied value.

| Table | Purpose | Key columns / constraints |
|---|---|---|
| `business_profiles` | One profile per tenant | `tenant_id` PK/unique; name, category, description, wilaya, city, address, phone, email, website, target_audience jsonb, objectives jsonb, usps jsonb, competitors jsonb, preferred_tone, brand_voice, default_content_style |
| `product_categories` | Optional categorization | unique `(tenant_id, slug)` |
| `products` | Catalog | price_amount `numeric(14,2)`, currency char(3), status, offer_price_amount, offer_currency, availability, category_id FK, deleted_at |
| `product_images` | Product image links | FK `product_id`, `asset_id`, unique `(tenant_id, product_id, asset_id)` |
| `brand_assets` | Minimal brand kit | kind (`logo`,`color_palette`,`font`,`tone_guide`), `asset_id`, `text_value`, label |
| `brand_guidelines` | Structured rules | banned_claims jsonb, required_disclaimers jsonb, color_tokens jsonb, typography jsonb |
| `onboarding_sessions` | Conversational onboarding state | status, extracted_json, confidence_json, missing_fields jsonb, confirmed_json, confirmed_at; inferred facts never auto-promoted |
| `tenant_assets` | Object storage registry | storage_ref, mime_type, size_bytes, checksum_sha256, scan_status, uploaded_by, kind; unique storage_ref |
| `ai_generation_jobs` | Existing job table from `0001_initial` | `style`, `locale`, `kind`, `result_ref`, `provider_request_id`, `idempotency_key` and unique `(tenant_id, idempotency_key)` **already exist**; add only `estimated_cost`, `currency`, `price_snapshot_id` where absent |
| `ai_usage_records` | Per-request usage/cost | tenant_id, user_id, job_id, `idempotency_key`, provider, model, input_tokens, cached_input_tokens, cache_write_tokens, output_tokens, image_count, `price_snapshot_id`, unit_price_amount/currency, computed_cost_amount/currency, status (`reserved`/`finalized`/`failed`/`uncertain`), occurred_at |
| `usage_counters` | Atomic quota counters | tenant_id, period_start, text_used, image_used, updated_at; unique `(tenant_id, period_start)` |
| `content_items` | Content metadata and current-version pointer only; backs the logical `content_calendar_entries` view | kind, locale/style, status, `current_version_id`, source, scheduled_for, validation_status; **no body column**; `current_version_id` is a non-authoritative pointer |
| `content_versions` | **Canonical immutable body store** | FK content_item, version, body, snapshot_hash, created_by; unique `(tenant_id, content_item_id, version)`; append-only; all rendering/validation/approval reads bodies from here |
| `content_validations` | Automated validation results | content_version_id, rule_code, severity, passed, evidence jsonb, created_at |
| `arabic_reviews` | Human Arabic quality | content_version_id, reviewer_user_id, status, notes, reviewed_at; reviewer must be flagged editor |
| `creative_assets` | Generated image metadata | job_id, asset_id, prompt, provider, model, status, content_item_id nullable |
| `approval_requests` | Content approval requests; logical `content_approvals` entity in `19-engineering-design-freeze.md §9` | kind = `content` only in Phase 2, target_type/id/version, payload_hash, status, decided_by, decided_at, requested_by, idempotency_key; **no `snapshot_id` FK** |
| `approval_snapshots` | Immutable request snapshots | `approval_request_id` FK to `approval_requests`, version, payload jsonb, hash; unique `(tenant_id, approval_request_id, version)`; append-only; current snapshot resolved by max version or non-FK pointer |
| `landing_pages` | Internal create/edit/preview and draft/version history (`OWNER_PROPOSED`) | slug unique per tenant, seo jsonb, status, `current_version_id` non-authoritative pointer; **no circular approved-version FK** |
| `landing_page_versions` | Immutable page versions (conditional) | FK `(tenant_id, page_id)`, version, body jsonb, snapshot_hash, status (`draft`/`approved`/`superseded`), created_by; unique `(tenant_id, page_id, version)`; at most one `approved` version per page |
| `leads` | Phase 3+ `DEFERRED` | Historical design only; table, public ingestion and management APIs/UI deferred |
| `audit_logs` | Existing tenant-scoped log; carries logical `approval_audit_events` namespace | tenant_id FK RESTRICT; actor, action, target, request_id, metadata jsonb |

## 2. System tables (admin-only, no tenant RLS)

| Table | Purpose |
|---|---|
| `users`, `sessions` | Identity (Phase 1) |
| `ai_provider_configs` | provider_code, enabled, priority, residency_tag, rate limits, cost caps |
| `ai_models` | provider_id, model_code, capability, price_amount/currency, max_tokens, supports_darija, enabled, license_evidence_ref, `source_url`, `captured_at`, model revision where supported |
| `ai_price_snapshots` | Immutable **AI cost evidence** per request: provider, model, USD input/cached/output unit prices, source URL, capture date, revision; distinct from FX |
| `fx_rate_snapshots` | **Phase 3 advertising FX** only. D-03 `OWNER_PROPOSED` permits no Phase 2 conversion, FX source or foreign-currency user display |
| `prompt_templates` | Versioned, locale/style-aware templates; `prompt_version`, `schema_version`, fixture version; no secrets |

System tables must not be writable through tenant APIs. Provider/model config changes are audited admin actions.

## 3. Entity relationships (simplified)

```text
tenants ─< tenant_memberships >─ users
tenants ─< business_profiles (1:1)
tenants ─< product_categories ─< products ─< product_images >─ tenant_assets
tenants ─< brand_assets >─ tenant_assets
tenants ─< onboarding_sessions
tenants ─< ai_generation_jobs ─< ai_usage_records
tenants ─< content_items ─< content_versions ─< content_validations
                         ├─< arabic_reviews
                         └─< creative_assets >─ tenant_assets
tenants ─< approval_requests ─< approval_snapshots
tenants ─< landing_pages ─< landing_page_versions

(`leads` is historical/Phase 3+ `DEFERRED`; not a Phase 2 object.)
tenants ─< audit_logs
```

## 4. Integrity rules

1. All tenant FKs include the tenant id in composite FKs where practical, e.g. `FOREIGN KEY (tenant_id, product_id) REFERENCES products(tenant_id, id)`, preventing cross-tenant references even before RLS.
2. `tenant_assets.storage_ref` unique; consumers must check `tenant_id` and `scan_status`.
3. `ai_generation_jobs` and `ai_usage_records` are unique on `(tenant_id, idempotency_key)`; provider request id, when present, is recorded but is not the sole idempotency key. Cost evidence references `ai_price_snapshots`, never advertising FX.
4. `approval_snapshots` and `content_versions` are append-only; no UPDATE path. The snapshot FK points from snapshot to request; no circular request→snapshot FK exists.
5. `content_versions.body` is the only canonical body. Material changes to approved content insert a new version and supersede old approval; never mutate approved row.
6. `audit_logs.tenant_id` remains nullable for system events; tenant rows are RLS-scoped and FK-protected.
7. Money `numeric(14,2)` + currency. AI/USD cost evidence uses `ai_price_snapshots`. User-facing amounts are DZD-only; no converted display, FX source or rate is invented for Phase 2. Advertising FX is `DEFERRED` to Phase 3.
8. Public lead submission is `DEFERRED` to Phase 3 or later. The historical resolver sketch (validate tenant slug → set transaction-local `app.current_tenant_id` → insert `leads` through `ago_app` with RLS WITH CHECK) is not a Phase 2 route. No client-supplied tenant id, privileged bypass or public bucket reference is part of Phase 2.
9. Approval API paths are `/api/v1/approval/...` only; validation override rules are defined in `11-automated-content-validation-spec.md §5`.
10. `landing_pages` has no FK to an approved version. `landing_page_versions` owns the approval status; a partial unique index permits at most one `approved` version per page. Internal draft/version state references that version id. This avoids a circular insert dependency. Publish execution is `DEFERRED`.
11. Logical entities in the freeze document map to physical tables without duplicating truth: `content_approvals` → `approval_requests` + `approval_snapshots`; `approval_audit_events` → `audit_logs` rows with `approval.*` actions; `content_calendar_entries` → view over `content_items.scheduled_for`.

## 5. Indexes proposed

- `products(tenant_id, status, category_id)`, `products(tenant_id, lower(name))`
- `content_items(tenant_id, status, scheduled_for)`, `(tenant_id, locale, style)`
- `content_versions(tenant_id, content_item_id, version)` unique
- `ai_usage_records(tenant_id, occurred_at desc)`, `(tenant_id, provider, model)`
- `leads(tenant_id, landing_page_id, submitted_at desc)` — Phase 3+ `DEFERRED`, not created in Phase 2
- `landing_page_versions(tenant_id, page_id, version)` unique; partial unique `(tenant_id, page_id)` where `status='approved'`
- `content_items(tenant_id, scheduled_for)` backed by the `content_calendar_entries` view filter
- `audit_logs(tenant_id, action, created_at desc)` for `approval.*` evidence
- `tenant_assets(tenant_id, kind, created_at desc)`
- `approval_requests(tenant_id, status, created_at desc)`, unique `(tenant_id, idempotency_key)`

## 6. Retention and privacy

| Data | Proposed handling | Open question |
|---|---|---|
| Leads | **DEFERRED — Phase 3 or later.** No Phase 2 `leads` table, endpoint, UI or active Leads data lifecycle exists. Retention period and erasure workflow remain future design considerations for the phase in which Leads are introduced; no period or legal basis is defined here. | Revisit when Leads are introduced; no Phase 2 decision required |
| Audit logs | Append-only; RESTRICT tenant hard delete | Retention period |
| AI usage and AI price snapshots | Retain for quota/cost reporting from immutable USD evidence | Financial audit period; no advertising FX in Phase 2 |
| Onboarding sessions | Delete after confirmation or 30 days | Owner confirmation policy |
| Provider prompts | Avoid storing full prompts; redact business personal data | Legal review |

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Unscanned asset used in content | `scan_status` gate + ownership check + RLS |
| Cross-tenant FK reference | Composite FKs + RLS + API tests with `ago_app` |
| Double billing on retry | Idempotency + usage reservation/finalization + provider request id |
| Stale cost data | Copy price at request time into usage record |
| Every tenant table forgotten | Migration checklist + automated catalog test asserting RLS on all tenant tables |
