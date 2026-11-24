# Phase 0 — PostgreSQL Database Design (post-audit)

**Status:** Corrected for approval. No migrations are created in Phase 0.
**Target:** PostgreSQL 16. UUID IDs, `timestamptz` UTC, `numeric(14,2)` for money, check constraints over native enums.
**Tenant rule:** every tenant-owned table has `tenant_id uuid NOT NULL`, RLS enabled and forced.

## 1. Tenant settings and localization

`tenants` (product name: Organization)

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| name, slug | text, citext unique | |
| base_currency | char(3) NOT NULL DEFAULT 'DZD' | Canonical money currency |
| display_currencies | jsonb NOT NULL DEFAULT '["DZD","USD"]' | Both shown in UI |
| default_ui_locale | text NOT NULL DEFAULT 'ar' | Arabic first |
| supported_ui_locales | jsonb NOT NULL DEFAULT '["ar","fr"]' | |
| default_content_locale | text NOT NULL DEFAULT 'ar-DZ' | Darija-aware copy |
| timezone | text NOT NULL DEFAULT 'Africa/Algiers' | |
| plan_code | text NOT NULL DEFAULT 'free' | From `subscriptions` |
| created_at/updated_at/deleted_at | timestamptz | |

## 2. System tables (not tenant-owned)

- `users`: id, email citext unique, password_hash, full_name, timestamps.
- `sessions`: id, user_id, token_hash unique, expires_at, absolute_expires_at, revoked_at, created_at. No `tenant_id`; scoped by user and checked against memberships.
- `fx_rates`: id, base_currency, quote_currency, rate numeric(18,8), effective_on date, source text, captured_at. Unique `(base_currency, quote_currency, effective_on, source)`. Admin/system write only.
- `ai_provider_configs`: id, provider_code unique, display_name, enabled, priority, fallback_group, residency_tag, rate_limit_per_minute, cost_cap_daily, created_at/updated_at. Admin-only.
- `ai_models`: id, provider_id, model_code, capability (`text`/`image`), enabled, unit_price_amount, unit_price_currency, max_tokens, supports_darija boolean, priority, unique `(provider_id, model_code)`. Admin-only.

## 3. Tenant-owned MVP tables

### `tenant_memberships`
PK `(tenant_id, user_id)`; columns `role` (`owner`,`editor`,`viewer`), `status` (`active`,`invited`,`suspended`), timestamps. Index on `user_id`.

### `business_profiles`
`tenant_id` PK/FK, `name`, `sector`, `description`, `city`, `wilaya`, `address`, `phone`, `email`, `website`, `brand_voice`, `default_locale`, timestamps. One profile per tenant.

### `brand_assets` (minimal)
id, tenant_id, `kind` (`logo`,`color_palette`,`font`,`tone_guide`), `label`, `text_value`, `storage_ref`, `mime_type`, `created_by`, timestamps. No full DAM/versioning in MVP.

### `products`
id, tenant_id, `name`, `description`, `sku`, `price_amount`, `currency`, `status`, timestamps, `deleted_at`. Index `(tenant_id, status, name)`.

### `content_items`
id, tenant_id, `kind` (`social_post`,`ad_copy`,`email_copy`,`landing_copy`), `locale` (`ar`,`ar-DZ`,`fr`), `body`, `status` (`draft`,`in_review`,`approved`,`scheduled`,`published`,`archived`), `source` (`ai`,`human`,`ai_edited`), `scheduled_for timestamptz`, `channel_target`, `generation_job_id`, `created_by`, timestamps, `deleted_at`.
Indexes: `(tenant_id, scheduled_for)`, `(tenant_id, status)`, `(tenant_id, locale)`. The content calendar is a view over `scheduled_for`; no separate calendar table.

### `creative_assets`
id, tenant_id, `content_item_id` nullable, `kind` (`image`,`poster`), `storage_ref`, `prompt`, `provider`, `model`, `status`, `created_by`, timestamps. Supports creative generation without binary blobs in the DB.

### `ai_generation_jobs`
id, tenant_id, requested_by, `capability` (`text`,`image`), `kind`, `locale`, `prompt`, `status` (`queued`,`running`,`succeeded`,`failed`,`dead_letter`,`cancelled`), `run_at`, `attempt_count`, `max_attempts` default 3, `next_retry_at`, `locked_by`, `locked_at`, `heartbeat_at`, `provider`, `model`, `provider_request_id`, `idempotency_key`, `result_ref`, `error_code`, timestamps.
Constraints: `UNIQUE (tenant_id, idempotency_key)`, `attempt_count <= max_attempts`.
Indexes: partial on `status='queued' AND run_at <= now()`, `(tenant_id, status, created_at DESC)`.

### `ai_usage_records`
id, tenant_id, job_id, `capability`, provider, model, `tokens_in`, `tokens_out`, `images`, `unit_price_amount`, `unit_price_currency`, `computed_cost_amount`, `cost_currency`, `request_id`, created_at. Index `(tenant_id, created_at DESC)`. Price snapshot stored per record.

### `subscriptions` (lite)
tenant_id PK/FK, `plan_code`, `status`, `current_period_start`, `current_period_end`, `generation_limit`, `image_limit`, `overrides jsonb`, timestamps. No payment/billing integration.

### `usage_counters`
PK `(tenant_id, period_start)`, `generations_used`, `images_used`, `updated_at`. Atomic increment with job creation.

### `approval_requests`
id, tenant_id, `kind` (`content_publish`,`ad_activation`,`ad_budget_change`,`landing_page_publish`), `target_type`, `target_id`, `target_version`, `payload_hash`, `snapshot_id`, requested_by, `status` (`pending`,`approved`,`rejected`,`expired`,`revoked`,`superseded`), decided_by, decided_at, `valid_until`, `budget_ceiling_amount`, `budget_ceiling_currency`, `budget_ceiling_usd_amount`, `fx_rate_snapshot_id`, `superseded_by`, `idempotency_key`, created_at/updated_at.
Constraints: `UNIQUE (tenant_id, idempotency_key)`; check that ad kinds have non-null ceiling and FX snapshot.
Indexes: `(tenant_id, status, kind, created_at DESC)`.

### `approval_snapshots`
id, tenant_id, approval_request_id, `version`, `payload jsonb`, `hash text`, created_at. Append-only; `UNIQUE (approval_request_id, version)`. No update path; new edits create a new version and a new approval request.

### `external_actions`
id, tenant_id, `approval_request_id` UNIQUE, `kind`, `status` (`pending`,`executed`,`failed`,`blocked`), `target_type`, `target_id`, `provider_ref`, `requested_amount`, `requested_currency`, `requested_usd_amount`, `fx_rate_snapshot_id`, created_by, executed_by, executed_at, `last_error_code`.

### `external_action_attempts`
id, tenant_id, external_action_id, `attempt_no`, `status`, `provider`, `provider_request_ref`, `error_code`, created_at. Immutable provider-call log.

### `landing_pages`
id, tenant_id, `slug`, `title`, `blocks jsonb`, `status` (`draft`,`in_review`,`published`,`archived`), `published_at`, `created_by`, timestamps, `deleted_at`. Unique `(tenant_id, slug)`. Publish requires approval request.

### `leads`
id, tenant_id, `landing_page_id` nullable, `name`, `phone`, `email`, `notes`, `source`, `status` (`new`,`contacted`,`qualified`,`archived`), timestamps, `deleted_at`. Index `(tenant_id, created_at DESC)`.

### `audit_logs`
id bigserial, tenant_id nullable, actor_user_id, `action`, `target_type`, `target_id`, `approval_request_id`, `external_action_id`, `request_id`, `metadata jsonb`, created_at. Append-only; global auth events use null tenant_id.

## 4. Deferred tables (documented, excluded from Phase 1 migration)

| Table | Columns (summary) | Rationale for deferral |
|---|---|---|
| `social_connections` | tenant_id, platform, account_ref, encrypted_token_ref, scopes, status | Direct publishing deferred |
| `ad_accounts` | tenant_id, platform, external_account_id, currency, status | Multi-platform ad automation deferred |
| `ad_campaigns` | tenant_id, ad_account_id, external_campaign_id, name, status | Same |
| `ad_budget_limits` | tenant_id, ad_campaign_id, ceiling_amount, currency, ceiling_usd_amount, fx_snapshot_id, version, superseded_at, approval_request_id, spent_amount | Safety schema designed now; execution later |
| `spend_events` | tenant_id, budget_limit_id, amount, currency, fx_snapshot_id, provider_ref, created_at | Spend ledger activated with ad execution |

These tables reuse the approval model already defined, so later activation cannot bypass ceilings.

## 5. Entity evaluation (explicit)

| Requested entity | Verdict | Note |
|---|---|---|
| business_profiles | MVP | Included |
| products | MVP | Included |
| brand_assets | MVP minimal | Included; no versioning/DAM |
| content_approvals | MVP via `approval_requests` | Unified table covers content + other targets |
| social_connections | Deferred | Publishing deferred |
| landing_pages | MVP basic | Included; approval-gated |
| leads | MVP | Included |
| ad_accounts | Deferred | Schema reserved |
| ad_campaigns | Deferred | Schema reserved |
| ad_budget_limits | Deferred | Schema reserved; safety contract fixed |
| ai_provider_configs | MVP system table | Not tenant-owned |
| ai_usage_records | MVP | Included |
| subscriptions | MVP-lite | Quota state only |
| audit_logs | MVP | Included |

## 6. Tenant isolation matrix

| Tenant-owned (RLS) | System (admin-only, no RLS) |
|---|---|
| tenants, tenant_memberships, business_profiles, brand_assets, products, content_items, creative_assets, ai_generation_jobs, ai_usage_records, usage_counters, subscriptions, approval_requests, approval_snapshots, external_actions, external_action_attempts, landing_pages, leads, audit_logs (tenant rows) | users, sessions, fx_rates, ai_provider_configs, ai_models |

RLS policy applied to every tenant-owned table:

```sql
ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;
ALTER TABLE <table> FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON <table>
  USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
```

Application sets `SET LOCAL app.current_tenant_id` per transaction and still verifies membership/role. Migration roles bypass explicitly. Tests must prove cross-tenant denial.

## 7. Migration and lifecycle

- Phase 1 baseline creates only Section 2/3 tables plus RLS; deferred tables are documented, not created.
- Expand-then-contract; tested downgrade; no destructive drop in a forward release.
- Approval snapshots and provider prompts retained 30 days by default; audit logs longer (policy pending).
- Backups with PITR; restore drill before pilot.
- No production data in lower environments.
