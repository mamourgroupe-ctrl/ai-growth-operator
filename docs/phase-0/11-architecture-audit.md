# Phase 0 — Independent Architecture Audit

**Role:** Independent Principal Software Architect / CTO review.
**Date:** 2026-11-24
**Scope:** Documentation consistency audit only. No application code, no Phase 1 work, no merge of PR #15.
**Verdict:** **Corrections required before approval.** All findings below have been applied to the Phase 0 documents; final product-owner approval is still required.

## ملخص تنفيذي

وُجد أن وثائق Phase 0 غير متسقة مع القرارات المعتمدة في ثلاث نقاط جوهرية: أولوية اللغة (كانت تُفترض الفرنسية أولاً بينما العربية والدارجة هما الأولوية)، عرض العملة (DZD فقط بدلاً من DZD وUSD)، ونموذج الموافقة المالية (كان غائباً). كما تمت مراجعة قاعدة البيانات وتوسيعها بكيانات MVP الناقصة، وتأكيد مسار العمل في PostgreSQL مع شروط صارمة، وتصميم بوابة AI مستقلة عن المزوّد. لا توجد موافقة نهائية بعد.

---

## Section 1 — Product requirements verification

| Approved decision | Previous Phase 0 state | Finding | Correction applied |
|---|---|---|---|
| Market: Algeria | Implied by README | Partial | Explicit in corrected PRD; `Africa/Algiers`, DZD base |
| Customer: small businesses | Stated in README | Pass | Retained |
| Multi-tenant SaaS | Shared schema + RLS | Pass | Retained; product term "Organization" mapped to technical `tenant` |
| Human approval before external publishing or ad spend | Only "draft-only"; no approval model | **Fail** | Approval center + fail-closed external action gate + budget ceiling rules added |
| Currency display: DZD and USD | DZD only | **Fail** | Dual display with `display_currencies`, `fx_rates`, approval-time FX snapshots |
| Primary interface: responsive web | Web deferred to Phase 3 | **Fail** | Responsive web is MVP; Android explicitly future |
| Arabic first, incl. Algerian Darija, then French | ADR-009 said French-first | **Fail** | ADR-009 marked superseded by ADR-011; `ar` UI default, `ar-DZ` copy support, `fr` secondary |
| Android: future phase | Not stated | Gap | Explicitly deferred in PRD, roadmap, backlog |

**Correction to French-first assumption:** fully removed. Arabic is now the primary product language; Darija is a first-class content locale; French is secondary. ADR-009 remains in the log as a superseded decision for traceability.

---

## Section 2 — PostgreSQL-backed jobs vs Redis + Celery

**Verdict:** Acceptable for MVP **only with the explicit hardening recorded below**. Redis is not introduced for complexity.

| Required concern | Architecture response |
|---|---|
| Concurrent job claiming | Atomic `SELECT ... FOR UPDATE SKIP LOCKED` claim inside a short transaction; claimed rows get `locked_by`, `locked_at`, `heartbeat_at` |
| `FOR UPDATE SKIP LOCKED` | Explicit claim query documented in architecture and ADR-012 |
| Retry policies | `attempt_count`, `max_attempts = 3`, `next_retry_at`, bounded retries; no infinite loops |
| Exponential backoff | `delay = min(base * 2^(attempt-1), cap) + jitter`; base 30s, cap 15m, full jitter |
| Job scheduling | `run_at timestamptz` with partial index on queued/scheduled jobs; worker polls due jobs |
| Idempotency | `UNIQUE (tenant_id, idempotency_key)`; provider request ID stored; duplicate key returns original job or `409` on payload mismatch |
| Failed-job management | `failed` terminal state, `dead_letter` after retry exhaustion, `last_error_code` (safe, non-sensitive), manual replay creates a new job |
| Monitoring | Queue depth, oldest queued age, success/failure rate, retry rate, dead-letter count, stale lock count, worker heartbeat, DB load |
| Worker concurrency | Initial concurrency 2 processes, configurable; per-tenant fairness deferred; lease timeout with heartbeat reclaim |
| DB load/scalability limits | Partial indexes, adaptive polling, no large payloads in queue, payloads kept in referenced tables; revisit at sustained >100 jobs/min or >10k backlog |

**Trade-off:** Postgres keeps dependencies low and gives transactional consistency with tenant data; cost is polling load and没有 dedicated broker semantics. **Migration path:** keep the job API contract and `JobDispatcher` interface stable; when thresholds are hit, add Celery workers + Redis broker, switch dispatcher implementation, use an outbox table to avoid dual-write loss, and run both paths in shadow mode before cutover. No application-visible contract changes.

---

## Section 3 — Database completeness

| Entity | Decision | Rationale / isolation |
|---|---|---|
| `business_profiles` | **MVP** | Tenant-owned; required by business profile module; RLS |
| `products` | **MVP** | Tenant-owned; product catalog; RLS |
| `brand_assets` | **MVP (minimal)** | Tenant-owned; brand context for Arabic copy + creative generation; no full DAM/versioning |
| `content_approvals` | **MVP via unified `approval_requests`** | Standalone table rejected: one approval model must cover content, publishing, landing pages, and ad spend; `target_type='content_item'` covers this entity; RLS |
| `social_connections` | **Deferred** | Needed only when actual publishing is enabled; current MVP is draft/approval-only; design reserved |
| `landing_pages` | **MVP (basic)** | Tenant-owned; publish gated by approval; RLS |
| `leads` | **MVP** | Tenant-owned; captured from landing pages; RLS |
| `ad_accounts` | **Deferred implementation, schema specified** | Required by future advertising activation; no multi-platform automation in MVP |
| `ad_campaigns` | **Deferred implementation, schema specified** | Same; approval model already references it via `target_type` |
| `ad_budget_limits` | **Deferred implementation, schema specified** | Financial safety model defined now so later activation cannot be built without ceilings |
| `ai_provider_configs` | **MVP (system-owned, not tenant-owned)** | Gateway route/model/cost config; admin-only, no RLS because not tenant data |
| `ai_usage_records` | **MVP** | Tenant-owned usage + cost tracking; RLS; enforces AI limits |
| `subscriptions` | **MVP-lite** | Plan/quota state only; no payment processing (billing deferred) |
| `audit_logs` | **MVP** | Append-only; tenant-scoped rows plus global auth events |

Isolation rule: every table with `tenant_id` gets RLS with `USING`/`WITH CHECK` on `app.current_tenant_id`. `users`, `ai_provider_configs`, `ai_models`, `fx_rates` are system tables and are admin-only. `tenant_memberships` carries `tenant_id` and is RLS-protected. Deferred tables are documented but excluded from the Phase 1 baseline migration.

---

## Section 4 — Approval and financial safety model

**Invariant:** no external side effect (publish, activate ad, change budget) may execute without a currently valid, explicit approval and a passing budget check. Fail closed.

### Model

- `approval_requests` — one row per requested external action: `kind`, `target_type`, `target_id`, `target_version`, `payload_hash`, requested/decided actors, status, expiry, budget ceiling + currency, FX snapshot, `superseded_by`.
- `approval_snapshots` — append-only immutable JSON of exactly what was approved (content body, budget ceiling, model/provider, locale). Approval points to snapshot ID.
- `external_actions` — one row per intended side effect, linked 1:1 to an approval request; status pending/executed/failed/blocked; provider reference and safe error code.
- `external_action_attempts` — immutable attempt log for every provider call.
- `ad_budget_limits` (deferred implementation) — versioned ceiling with `parent_version`, `superseded_at`, spend ledger link.
- `spend_events` (deferred) — recorded spend against a budget version; no negative or implicit increase.

### Rules

1. Publishing and ad activation are two distinct approval kinds; neither can be implied by the other.
2. Every approved ad action stores an exact ceiling: `ceiling_amount` + `ceiling_currency` + USD display amount + `fx_rate_snapshot_id`.
3. Any change to target content or budget increments `target_version` and marks prior approvals `superseded`; superseded approvals cannot execute.
4. Approved snapshots are immutable. Edits create a new version and a new approval request; no in-place mutation of approved data.
5. No automatic budget increases. Increase requires a new approval request with a new ceiling.
6. Execution order is: load approval → verify `approved` + not expired + not superseded + version match → verify snapshot hash → lock budget row → validate `spent + requested <= ceiling` → write `external_actions` → call provider → write attempt log. Any failure stops before provider call.
7. Every external action is auditable via `external_actions`, `external_action_attempts`, and `audit_logs`.

---

## Section 5 — AI provider strategy

- **Provider independence:** `AiGateway` with `TextProvider` and `ImageProvider` protocols; no provider-specific columns in core business tables.
- **Model config:** `ai_provider_configs` + `ai_models` hold capabilities (`text`, `image`), enabled flag, priority/fallback order, unit prices, rate limits, data-residency tag.
- **Usage & cost:** `ai_usage_records` stores tokens/images, unit price snapshot, computed cost, tenant, job, provider, model, request ID; monthly cost caps align with `subscriptions`.
- **Rate limits:** per tenant, per provider, per model counters; DB-backed counters for MVP, provider-side limits mirrored in config.
- **Failure handling:** timeout, bounded retry with jitter, safe error codes, circuit breaker per provider, no raw provider errors to clients.
- **Fallback:** ordered provider list per capability; fallback only to a provider whose residency/cost policy is allowed; every fallback recorded in `ai_usage_records` and audit logs. Single provider may be active initially without lock-in.

---

## Section 6 — Corrected MVP scope

**MUST HAVE:** authentication; organization management; business profile; product catalog; AI Marketing Studio; Arabic marketing copy (`ar`, `ar-DZ`) and French secondary; creative generation; content calendar; approval center; basic landing pages; lead management; AI usage limits; responsive web; DZD + USD display.

**DEFERRED:** Android application; complex CRM; advanced automated campaign optimization; multi-platform advertising automation; advanced analytics; direct social publishing; billing/payment processing. Advertising execution tables are documented but not implemented in MVP.

---

## Section 7 — Updated deliverables

1. This audit report (`11-architecture-audit.md`).
2. Corrected PRD (`01-prd-review.md`).
3. Corrected database design (`03-database-design.md`).
4. Updated ADR log (`10-architecture-decision-log.md`) — ADR-009 superseded, ADR-005 amended, ADR-011..016 added.
5. Updated roadmap (`06-development-roadmap.md`) and backlog (`09-github-backlog.md`).
6. Consistency updates to API, security, testing, and deployment docs.
7. Documentation corrections committed to Arena branch; PR #15 remains draft and unmerged.

## Section 8 — Unresolved risks

| Risk | Severity | Owner action |
|---|---|---|
| Product-owner approval of corrected scope still pending | High | Approve or amend this audit |
| FX rate source/snapshot policy not chosen | Medium | Select provider and rounding rules before implementation |
| Advertising execution deferred but approval schema designed now | Medium | Reconfirm before Phase 3 |
| Darija locale quality and review capacity | Medium | Define human review workflow |
| Postgres queue scaling threshold needs measurement | Medium | Benchmark during Phase 2 |
| Provider data-residency constraints unknown | Medium | Legal/provider review before pilot |
| Image generation cost controls need pricing data | Medium | Populate model price config |
| Branch `main` protection not yet enabled | Medium | Issue #14 before merge |
