# Phase 2 — Proposed Alembic Migration Plan

**Status:** Proposed. No migration files created in this planning task.  
**Baseline:** `0001_initial`, `0002_audit_log_tenant_fk` from Phase 1.

## Decision status

| Category | Summary |
|---|---|
| `FROZEN` technical baseline | Alembic only; PostgreSQL; UUID ids; RLS+RBAC; append-only audit/outbox; non-destructive column additions. |
| `OWNER_PROPOSED` decisions | D-01–D-05, D-07, D-08 per `20-owner-decision-register.md`. Seven additive Phase 2 migrations remain a future engineering plan; `0010` reserved for Phase 3 advertising FX. |
| `BLOCKED` / `DEFERRED` | Final owner confirmation; numeric quota values; retention columns; storage/legal evidence. Lead tables/routes and publishing are `DEFERRED` to Phase 3 or later. |
| External dependencies | Final owner confirmation; legal review for any future lead retention in Phase 3. |
| Confirmed boundary | Advertising FX snapshots, paid outbox/reconciliation and external execution state machines are Phase 3. AI price snapshots are SaaS cost evidence only. |
| Risks | Migration lock contention; RLS forgotten; production data migration of assets. |

## 1. Migration sequence (future work, not executed)

| Order | Migration name | Changes | Rollback strategy |
|---|---|---|---|
| `0003` | `business_catalog_brand` | `business_profiles`, `product_categories`, `products`, `product_images`, `brand_assets`, `brand_guidelines`; enable FORCE RLS; composite tenant FKs | Drop tables in reverse dependency order |
| `0004` | `assets_and_onboarding` | `tenant_assets`, `onboarding_sessions`; add `product_images`/`brand_assets` FKs | Drop tables/constraints |
| `0005` | `ai_gateway_usage` | Reuse existing `ai_generation_jobs.idempotency_key` and `uq_jobs_tenant_idempotency` from `0001_initial`; add only missing cost fields (`estimated_cost`, `currency`, `price_snapshot_id`); create `ai_usage_records`, `usage_counters`, `ai_provider_configs`, `ai_models`, `ai_price_snapshots`, `prompt_templates`; fake seeds only | Drop new tables/columns; do not drop the existing job idempotency constraint |
| `0006` | `content_and_validation` | `content_items` metadata-only with `current_version_id`; canonical append-only `content_versions`; `content_validations`, `arabic_reviews`, `creative_assets` with RLS | Drop in reverse order |
| `0007` | `approval` | `approval_requests` (no snapshot FK); `approval_snapshots` with request FK + unique version; triggers/constraints preventing UPDATE/DELETE on snapshots. Phase 2 `kind='content'` only | Drop constraints/tables (rollback would be destructive; require backup approval) |
| `0008` | `landing_pages` (`OWNER_PROPOSED` internal scope) | `landing_pages` (no approved-version FK), `landing_page_versions` (append-only, unique version, partial unique approved) only. No `leads` table in Phase 2; lead work is `DEFERRED` to Phase 3 or later | Drop tables (only if empty; otherwise require owner-approved data procedure) |
| `0009` | `indexes_and_constraints` | Indexes, composite FKs, `CHECK` constraints for styles/locales/status; new idempotency unique constraints where absent. This is the last Phase 2 revision. | Drop constraints/indexes |
| `0010` | `advertising_fx` (deferred to Phase 3) | Reserved identifier for `fx_rate_snapshots`, `fx_source_config`; **not part of Phase 2**; no live rate fetch, no source selection | Drop tables if ever created |

## 2. Migration safety rules

1. Additive by default; no destructive changes to `users`, `sessions`, `tenants`, `tenant_memberships`, `audit_logs`, `outbox_events`.
2. Every tenant-owned table created with `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY` in the same migration.
3. Policies explicitly use `USING` and `WITH CHECK`. PostgreSQL policies are `PERMISSIVE` by default; multiple permissive policies are OR-combined. If restrictive policies are introduced they are AND-combined. The tenant-isolation policy must not be weakened by another permissive policy; grants and `FORCE ROW LEVEL SECURITY` are separate controls.
4. Use `set_config('app.current_tenant_id', ..., true)` in tests and runtime paths, not parameter-bound `SET LOCAL`. Tenant context is transaction-local and server-derived.
5. Do not use `now()` in partial index predicates (not IMMUTABLE). Use generated columns or full indexes.
6. Run `alembic upgrade head`, then `alembic downgrade -1` one revision at a time in CI against non-superuser `ago_app` where possible, then upgrade back to head. Do not claim a verified `downgrade base` path.
7. Production migrations with locked tenant writes and backup; no asset binary data in migrations (storage refs only). No advertising FX, outbox, paid-action, lead or publishing-execution tables in Phase 2.
8. Application code must not assume migration order at runtime; use feature flags/provider registry disabled by default. Public lead inserts are `DEFERRED` to Phase 3 or later; the resolver sketch in `03-database-design.md §4` is historical context, not a Phase 2 route.

## 3. Data seeding

- `ai_provider_configs`/`ai_models`/`ai_price_snapshots`: **fake/dev seeds only**. No live provider keys or real price assumptions in seed data. USD prices sourced from official pages recorded in `07-ai-gateway-text-provider-comparison.md` and `08-image-generation-provider-comparison.md`, with `source_url`, `captured_at`, and model revision/license evidence. These are AI operating-cost facts, not FX or advertising budgets.
- `fx_rate_snapshots`: no Phase 2 seed; no FX source/rate is invented. Advertising FX is `DEFERRED` to Phase 3; D-03 `OWNER_PROPOSED` sets DZD-only user display with no conversion.
- Prompt templates: versioned rows with placeholder text in test; real templates require owner approval.
- No real business content, products or assets seeded outside synthetic fixtures; no lead seed because the table is `DEFERRED`.

## 4. Verification checklist (future implementation acceptance)

- [ ] `alembic current` shows expected revision.
- [ ] `alembic upgrade head` and `downgrade -1` succeed on a clean DB.
- [ ] Every tenant-owned table appears in RLS catalog check with FORCE RLS and policy.
- [ ] `ago_app` cannot insert into another tenant's rows; cross-tenant FK insert fails.
- [ ] Append-only tables reject UPDATE/DELETE; `content_versions.body` is the only canonical body.
- [ ] Idempotency unique constraints prevent duplicate usage rows for the same `(tenant_id, idempotency_key)`.
- [ ] Approval snapshot FK is one-directional; no circular insert dependency.
- [ ] `landing_pages` has no approved-version FK; `landing_page_versions` enforces one approved version per page.
- [ ] No advertising FX/outbox/paid-action table exists in any Phase 2 migration.
- [ ] No secret values or real PII in seeds.
- [ ] Migration plan reviewed against `docs/phase-0/03-database-design.md` and ADR-012.
