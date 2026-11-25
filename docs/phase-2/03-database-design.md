# Phase 2 — Updated Database Design and Entity Relationships

**Status:** Proposed. No migrations created in this planning task.  
**Baseline:** Phase 1 tables `users`, `sessions`, `tenants`, `tenant_memberships`, `ai_generation_jobs`, `outbox_events`, `audit_logs` plus Alembic `0001_initial`, `0002_audit_log_tenant_fk`.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Shared schema, UUID IDs, `timestamptz`, RLS `USING`/`WITH CHECK` on tenant-owned tables, `ago_app` runtime role, append-only audit/outbox, immutable snapshots. |
| Proposed decisions | New tables listed below; asset registry; validation results; onboarding sessions; product images. |
| Open questions | Exact retention periods, FX source, plan quotas, whether approval/landing tables move into Phase 2. |
| External dependencies | Legal review for lead/PII retention and provider transfer; storage provider selection. |
| Risks | Over-normalization; nullable tenant FK; unscanned assets; stale price snapshots. |

## 1. Tenant-owned tables (must have RLS)

Every table below: `tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT/ CASCADE per policy`, `ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY`, policy `tenant_isolation` with:

```sql
USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
```

Exception: `tenants` and `tenant_memberships` keep Phase 1 membership-aware policies.

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
| `ai_generation_jobs` | Existing job table | extend `style`, `locale`, `kind`, `result_ref`, `provider_request_id`, `estimated_cost`, `currency`, `price_snapshot_id` |
| `ai_usage_records` | Per-request usage/cost | tenant_id, user_id, job_id, provider, model, input_tokens, output_tokens, image_count, unit_price_amount/currency, computed_cost_amount/currency, occurred_at |
| `usage_counters` | Atomic quota counters | tenant_id, period_start, text_used, image_used, updated_at; unique `(tenant_id, period_start)` |
| `content_items` | Drafts/approved content version | kind, locale/style, body, status, version, source, scheduled_for, validation_status, content_hash |
| `content_versions` | Immutable version history | FK content_item, version, body, snapshot_hash, created_by; unique `(tenant_id, content_item_id, version)` |
| `content_validations` | Automated validation results | content_version_id, rule_code, severity, passed, evidence jsonb, created_at |
| `arabic_reviews` | Human Arabic quality | content_version_id, reviewer_user_id, status, notes, reviewed_at; reviewer must be flagged editor |
| `creative_assets` | Generated image metadata | job_id, asset_id, prompt, provider, model, status, content_item_id nullable |
| `approval_requests` | Owner decision requests | kind, target_type/id/version, payload_hash, snapshot_id, status, decided_by, decided_at, requested_by, idempotency_key |
| `approval_snapshots` | Immutable request snapshots | approval_request_id, version, payload jsonb, hash; append-only |
| `landing_pages` | Basic internal pages | slug unique per tenant, blocks jsonb, seo jsonb, status, approved_version_id |
| `leads` | Captured contacts | landing_page_id, name, email, phone, message, source, status, submitted_at |
| `audit_logs` | Existing tenant-scoped log | tenant_id FK RESTRICT; actor, action, target, request_id, metadata jsonb |

## 2. System tables (admin-only, no tenant RLS)

| Table | Purpose |
|---|---|
| `users`, `sessions` | Identity (Phase 1) |
| `ai_provider_configs` | provider_code, enabled, priority, residency_tag, rate limits, cost caps |
| `ai_models` | provider_id, model_code, capability, price_amount/currency, max_tokens, supports_darija, enabled, license_evidence_ref |
| `fx_rate_snapshots` | Immutable money snapshots; source unresolved |
| `prompt_templates` | Versioned, locale/style-aware templates; no secrets |

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
tenants ─< landing_pages ─< leads
tenants ─< audit_logs
```

## 4. Integrity rules

1. All tenant FKs include the tenant id in composite FKs where practical, e.g. `FOREIGN KEY (tenant_id, product_id) REFERENCES products(tenant_id, id)`, preventing cross-tenant references even before RLS.
2. `tenant_assets.storage_ref` unique; consumers must check `tenant_id` and `scan_status`.
3. `ai_usage_records` unique on `(tenant_id, idempotency_key, provider_request_id)` where provider request id exists; otherwise job id is the stable key.
4. `approval_snapshots` and `content_versions` are append-only; no UPDATE path.
5. Material changes to approved content insert a new version and supersede old approval; never mutate approved row.
6. `audit_logs.tenant_id` remains nullable for system events; tenant rows are RLS-scoped and FK-protected.
7. Money `numeric(14,2)` + currency; USD amount only from immutable FX snapshot (source still unresolved).

## 5. Indexes proposed

- `products(tenant_id, status, category_id)`, `products(tenant_id, lower(name))`
- `content_items(tenant_id, status, scheduled_for)`, `(tenant_id, locale, style)`
- `content_versions(tenant_id, content_item_id, version)` unique
- `ai_usage_records(tenant_id, occurred_at desc)`, `(tenant_id, provider, model)`
- `leads(tenant_id, landing_page_id, submitted_at desc)`
- `tenant_assets(tenant_id, kind, created_at desc)`
- `approval_requests(tenant_id, status, created_at desc)`, unique `(tenant_id, idempotency_key)`

## 6. Retention and privacy

| Data | Proposed handling | Open question |
|---|---|---|
| Leads | Keep while tenant active; deletion on explicit tenant request subject to legal retention | Retention period / erasure workflow |
| Audit logs | Append-only; RESTRICT tenant hard delete | Retention period |
| AI usage | Retain for quota/cost reporting | Financial audit period |
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
