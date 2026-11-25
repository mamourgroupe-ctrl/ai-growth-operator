# Phase 2 — Proposed Alembic Migration Plan

**Status:** Proposed. No migration files created in this planning task.  
**Baseline:** `0001_initial`, `0002_audit_log_tenant_fk` from Phase 1.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Alembic only; PostgreSQL; UUID ids; RLS+RBAC; append-only audit/outbox; non-destructive column additions. |
| Proposed decisions | Eight additive migrations with RLS verification tests embedded in CI. |
| Open questions | Approval/landing scope; FX table; retention columns; plan quota defaults. |
| External dependencies | Owner approval of roadmap re-baseline; legal review for lead retention. |
| Risks | Migration lock contention; RLS forgotten; production data migration of assets. |

## 1. Migration sequence (future work, not executed)

| Order | Migration name | Changes | Rollback strategy |
|---|---|---|---|
| `0003` | `business_catalog_brand` | `business_profiles`, `product_categories`, `products`, `product_images`, `brand_assets`, `brand_guidelines`; enable FORCE RLS; composite tenant FKs | Drop tables in reverse dependency order |
| `0004` | `assets_and_onboarding` | `tenant_assets`, `onboarding_sessions`; add `product_images`/`brand_assets` FKs | Drop tables/constraints |
| `0005` | `ai_gateway_usage` | Extend `ai_generation_jobs`; create `ai_usage_records`, `usage_counters`, `ai_provider_configs`, `ai_models`, `prompt_templates`; seed fake providers only in dev/test | Drop new tables/columns; seeded data is metadata only |
| `0006` | `content_and_validation` | `content_items`, `content_versions`, `content_validations`, `arabic_reviews`, `creative_assets` with RLS | Drop in reverse order |
| `0007` | `approval` | `approval_requests`, `approval_snapshots`; triggers/constraints preventing UPDATE/DELETE on snapshots | Drop constraints/tables (rollback would be destructive; require backup approval) |
| `0008` | `landing_and_leads` | `landing_pages`, `leads` with RLS | Drop tables (only if empty; otherwise require owner-approved data procedure) |
| `0009` | `fx_snapshots` | `fx_rate_snapshots`, `fx_source_config`; no live rate fetch | Drop tables |
| `0010` | `indexes_and_constraints` | Additional indexes, composite FKs, `CHECK` constraints for styles/locales/status | Drop constraints/indexes |

## 2. Migration safety rules

1. Additive by default; no destructive changes to `users`, `sessions`, `tenants`, `tenant_memberships`, `audit_logs`, `outbox_events`.
2. Every tenant-owned table created with `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY` in the same migration.
3. Policies explicitly use `USING` and `WITH CHECK`; no `PERMISSIVE` policy that accidentally allows cross-tenant writes.
4. Use `set_config('app.current_tenant_id', ..., true)` in tests, not parameter-bound `SET LOCAL`.
5. Do not use `now()` in partial index predicates (not IMMUTABLE). Use generated columns or full indexes.
6. Run `alembic upgrade head` and `alembic downgrade base` on clean DB in CI against non-superuser `ago_app` where possible; then upgrade back to head.
7. Production migrations with locked tenant writes and backup; no asset binary data in migrations (storage refs only).
8. Application code must not assume migration order at runtime; use feature flags/provider registry disabled by default.

## 3. Data seeding

- `ai_provider_configs`/`ai_models`: **fake/dev seeds only**. No live provider keys or real price assumptions in seed data. Prices sourced from official pages recorded in `07-ai-gateway-text-provider-comparison.md` and `08-image-generation-provider-comparison.md`, with `source_url`, `captured_at`, and model license/evidence.
- Prompt templates: versioned rows with placeholder text in test; real templates require owner approval.
- No real business content, products, leads, or assets seeded outside synthetic fixtures.

## 4. Verification checklist (future implementation acceptance)

- [ ] `alembic current` shows expected revision.
- [ ] `alembic upgrade head` and `downgrade -1` succeed on a clean DB.
- [ ] Every tenant-owned table appears in RLS catalog check with FORCE RLS and policy.
- [ ] `ago_app` cannot insert into another tenant's rows; cross-tenant FK insert fails.
- [ ] Append-only tables reject UPDATE/DELETE.
- [ ] No secret values or real PII in seeds.
- [ ] Migration plan reviewed against `docs/phase-0/03-database-design.md` and ADR-012.
