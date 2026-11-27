# Phase 0 — PostgreSQL Database Design (final acceptance draft)

**Status:** Corrected for final approval. No migrations exist in Phase 0.
**Target:** PostgreSQL 16. UUID IDs, `timestamptz` UTC, `numeric(14,2)` money, check constraints over native enums.
**Tenant rule:** every tenant-owned table has `tenant_id uuid NOT NULL`, RLS enabled and forced.

## 1. Organization settings

`tenants` (product: Organization)

| Column | Type / default | Notes |
|---|---|---|
| id, name, slug | uuid PK, text, citext unique | |
| base_currency | char(3) `DZD` | Canonical money |
| display_currencies | jsonb `["DZD","USD"]` | Both displayed |
| default_ui_locale | text `ar` | Arabic/RTL default |
| supported_ui_locales | jsonb `["ar","fr"]` | Darija UI later, no schema change |
| default_content_style | text `msa` | `msa`, `darija`, `fr` |
| timezone | text `Africa/Algiers` | |
| plan_code | text `free` | From `subscriptions` |
| created_at/updated_at/deleted_at | timestamptz | |

## 2. System tables (admin-only, no RLS)

- `users`: id, email citext unique, password_hash, full_name, timestamps.
- `sessions`: id, user_id, token_hash unique, expires_at, absolute_expires_at, revoked_at, created_at.
- `fx_rate_snapshots`: id, base_currency, quote_currency, rate numeric(18,8), source text, observed_at, captured_at, snapshot_hash text. **Immutable**: inserts only; no update/delete path. Unique hash. FX source is an unresolved configuration decision; source records where the rate came from once selected.
- `ai_provider_configs`: provider_code unique, enabled, priority, fallback_group, residency_tag, rate_limit_per_minute, cost_cap_daily, timestamps.
- `ai_models`: provider_id, model_code, capability (`text`/`image`), enabled, unit_price_amount/currency, max_tokens, supports_darija, priority; unique `(provider_id, model_code)`.

## 3. Tenant-owned MVP tables

### `tenant_memberships`
PK `(tenant_id, user_id)`; `role` (`owner`,`editor`,`viewer`), `is_arabic_reviewer boolean default false` (capability, not role; viewer never), `status`, timestamps. Index `(user_id)`.

### `business_profiles`
tenant_id PK/FK, name, sector, description, city, wilaya, address, phone, email, website, brand_voice, default_content_style, timestamps.

### `brand_assets` (minimal)
id, tenant_id, kind (`logo`,`color_palette`,`font`,`tone_guide`), label, text_value, storage_ref, mime_type, created_by, timestamps. No full DAM/versioning.

### `products`
id, tenant_id, name, description, sku, price_amount, currency, status, timestamps, deleted_at.

### `content_items`
id, tenant_id, kind (`social_post`,`ad_copy`,`email_copy`,`landing_copy`), `locale` (`ar`,`ar-DZ`,`fr`), `style` (`msa`,`darija`,`fr`), body, status (`draft`,`in_review`,`arabic_review`,`ready_for_approval`,`approved`,`scheduled`,`published`,`archived`), source (`ai`,`human`,`ai_edited`), scheduled_for, channel_target, generation_job_id, created_by, timestamps, deleted_at.
Indexes `(tenant_id, scheduled_for)`, `(tenant_id, status)`, `(tenant_id, locale, style)`. Calendar = view over `scheduled_for`.

### `arabic_reviews`
id, tenant_id, content_item_id, reviewer_user_id, `locale`/`style`, `status` (`pending`,`approved`,`changes_requested`), notes, reviewed_at, created_at. Only rows with `status='approved'` allow content to be submitted for owner approval. Reviewer must be editor with `is_arabic_reviewer=true`.

### `creative_assets`
id, tenant_id, content_item_id nullable, kind (`image`,`poster`), storage_ref, prompt, provider, model, status, created_by, timestamps.

### `ai_generation_jobs`
id, tenant_id, requested_by, capability (`text`,`image`), kind, locale, style, prompt, status (`queued`,`running`,`succeeded`,`failed`,`dead_letter`,`cancelled`), run_at, attempt_count, max_attempts=3, next_retry_at, locked_by, locked_at, heartbeat_at, provider, model, provider_request_id, idempotency_key, result_ref, error_code, timestamps. Unique `(tenant_id, idempotency_key)`.

### `ai_usage_records`, `subscriptions`, `usage_counters`
As previously defined: usage/cost snapshots, plan quotas, atomic counters. No billing.

### `approval_requests`
id, tenant_id, kind (`content_publish`,`landing_page_publish`,`ad_activation`,`ad_budget_change`,`social_publish`), target_type, target_id, target_version, payload_hash, snapshot_id, requested_by, `decided_by` (must be owner), status (`pending`,`approved`,`rejected`,`expired`,`revoked`,`superseded`), decided_at, valid_until, budget_ceiling_amount, budget_ceiling_currency, budget_ceiling_usd_amount, `fx_rate_snapshot_id`, superseded_by, idempotency_key, timestamps.
Constraints: unique `(tenant_id, idempotency_key)`; ad kinds require ceiling + FX snapshot; `decided_by` must have owner role at decision time (service + trigger guard).

### `approval_snapshots`
id, tenant_id, approval_request_id, version, payload jsonb, hash text, created_at. Append-only; unique `(approval_request_id, version)`.

### `external_actions`
id, tenant_id, approval_request_id unique, kind, `state` (`created`,`authorized`,`queued`,`dispatching`,`uncertain`,`reconciled_executed`,`reconciled_failed`,`executed`,`failed`,`dead_letter`,`blocked`,`cancelled`), target_type, target_id, `provider_idempotency_key` unique (derived from action ID + approval version; reused on every retry), provider_ref, requested_amount, requested_currency, requested_usd_amount, fx_rate_snapshot_id, created_by, executed_by, executed_at, last_error_code, timestamps.

### `external_action_attempts`
id, tenant_id, external_action_id, attempt_no, status, provider, provider_request_ref, provider_idempotency_key, error_code, created_at. Immutable.

### `outbox_events`
id, tenant_id, aggregate_type (`external_action`), aggregate_id, event_type, payload jsonb, status (`pending`,`published`,`failed`,`dead`), available_at, attempts, locked_by, locked_at, created_at. Inserted in the **same transaction** as the authorized action. Dispatcher publishes without creating new side effects; replay with same aggregate_id/idempotency key is a no-op.

### `landing_pages`, `leads`, `audit_logs`
As previously defined. `audit_logs` additionally records approval_request_id, external_action_id, request_id, outbox_event_id, reconciliation run id.

## 4. Deferred extension points (documented, not in baseline migration)

| Table | Summary | Why deferred |
|---|---|---|
| `social_connections` | tenant_id, platform, account_ref, encrypted_token_ref, scopes, status | Direct social publishing outside MVP |
| `ad_accounts` | tenant_id, platform, external_account_id, currency, status | Paid ad execution outside MVP |
| `ad_campaigns` | tenant_id, ad_account_id, external_campaign_id, name, status | Same |
| `ad_budget_limits` | tenant_id, campaign_id, ceiling_amount, currency, ceiling_usd_amount, fx_rate_snapshot_id, version, superseded_at, approval_request_id, spent_amount | Safety contract fixed now |
| `spend_events` | tenant_id, budget_limit_id, amount, currency, fx_rate_snapshot_id, provider_ref, created_at | Activated with ad execution |

They reuse `approval_requests`, `external_actions`, outbox, idempotency, and reconciliation; later activation cannot bypass ceilings.

## 5. Explicit entity evaluation

| Requested entity | Verdict | Note |
|---|---|---|
| business_profiles | MVP | Included |
| products | MVP | Included |
| brand_assets | MVP minimal | Included; no DAM/versioning |
| content_approvals | MVP via `approval_requests` | Unified with publish/ad targets |
| social_connections | Deferred extension | Not implemented |
| landing_pages | MVP basic | Approval-gated |
| leads | MVP | Included |
| ad_accounts / ad_campaigns / ad_budget_limits | Deferred extension | Schema reserved |
| ai_provider_configs | MVP system table | Not tenant-owned |
| ai_usage_records | MVP | Included |
| subscriptions | MVP-lite | Quota state only |
| audit_logs | MVP | Append-only |
| Additional MVP: `arabic_reviews`, `outbox_events`, `fx_rate_snapshots`, `creative_assets` | MVP/system | Required by final corrections |

## 6. Tenant isolation matrix

| Tenant-owned (RLS) | System (admin-only) |
|---|---|
| tenants, tenant_memberships, business_profiles, brand_assets, products, content_items, arabic_reviews, creative_assets, ai_generation_jobs, ai_usage_records, usage_counters, subscriptions, approval_requests, approval_snapshots, external_actions, external_action_attempts, outbox_events, landing_pages, leads, audit_logs (tenant rows) | users, sessions, fx_rate_snapshots, ai_provider_configs, ai_models |

RLS policy on every tenant-owned table:

```sql
ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;
ALTER TABLE <table> FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON <table>
  USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
```

App sets `SET LOCAL app.current_tenant_id` per transaction and still checks membership/role. Migration roles bypass explicitly. Tests prove cross-tenant denial.

## 7. Lifecycle

- Phase 1 baseline creates system + MVP tables only; deferred tables excluded.
- Expand-then-contract; tested downgrade; no destructive drop in a forward release.
- `fx_rate_snapshots` and `approval_snapshots` immutable; audit/outbox retained per policy (pending).
- Daily backups + PITR; restore drill before pilot; no production data in lower environments.
