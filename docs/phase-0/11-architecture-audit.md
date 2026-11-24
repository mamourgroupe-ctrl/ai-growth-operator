# Phase 0 — Independent Architecture Audit

**Role:** Independent Principal Software Architect / CTO review.
**Date:** 2026-11-24
**Scope:** Documentation consistency audit and final acceptance corrections. No code, no Phase 1, no merge of PR #15.
**Verdict:** Corrections applied; awaiting final product-owner approval.

## ملخص تنفيذي

تم تدقيق الوثائق مقابل القرارات المعتمدة، وتصحيح أولوية اللغة إلى العربية والدارجة، وإضافة عرض العملتين، وبناء نموذج موافقة مالي صارم. في الجولة النهائية أُضيفت حماية التنفيذ الخارجي عبر outbox ومفاتيح idempotency وحالة `uncertain` وعملية تسوية، وتم تثبيت صلاحية الموافقة النهائية للمالك فقط، وتوثيق مصدر الصرف كقرار لم يُحسم بعد، وتحديد مراجعة بشرية للجودة العربية. لا توجد موافقة نهائية بعد.

---

## Section 1 — Product requirements verification

| Approved decision | Previous state | Finding | Correction |
|---|---|---|---|
| Algeria, small businesses, multi-tenant SaaS | Implied / present | Pass | Explicit |
| Human approval before external publish/ad spend | Draft-only, no model | Fail | Approval center + owner-only decision + fail-closed gate |
| DZD + USD | DZD only | Fail | Dual display, immutable FX snapshots |
| Responsive web primary | Deferred | Fail | MVP |
| Arabic first incl. Darija, then French | French-first ADR-009 | Fail | ADR-011 + ADR-019; `ar` default, `ar-DZ` style, `fr` secondary |
| Android future | Unstated | Gap | Deferred |
| Direct social publishing / paid ad execution | Ambiguous | Gap | Explicitly outside MVP; extension points preserved |

## Section 2 — PostgreSQL jobs vs Redis/Celery

Accepted with mandatory hardening: `FOR UPDATE SKIP LOCKED`, leases/heartbeat, `run_at`, `max_attempts`, exponential backoff with full jitter, idempotency, dead-letter, monitoring, worker concurrency 2, known DB-load limits. Migration to Celery+Redis via stable `JobDispatcher`, outbox, and shadow run. Redis not introduced for complexity. Trade-off documented in ADR-012.

## Section 3 — Database completeness

MVP: business_profiles, products, brand_assets (minimal), landing_pages, leads, ai_provider_configs, ai_usage_records, subscriptions (lite), audit_logs. Final additions: arabic_reviews, outbox_events, fx_rate_snapshots, creative_assets. Unified `approval_requests` covers content_approvals and all external-action targets. Deferred extensions: social_connections, ad_accounts, ad_campaigns, ad_budget_limits, spend_events. Every tenant-owned table has RLS; system tables admin-only.

## Section 4 — Approval, financial safety, and external execution

### Model
- `approval_requests` + immutable `approval_snapshots`; edits supersede prior versions.
- **Owner-only decision** (ADR-018); editors prepare/submit; viewers read-only; Arabic reviewer is an editor capability, not approval authority.
- Ad-kind approvals require exact ceiling, currency, USD display, and immutable FX snapshot.
- `external_actions` state machine, `external_action_attempts`, `outbox_events`, audit log.

### Transactional outbox
Authorization decision and outbox event insert happen in **one DB transaction**. Dispatcher publishes due events; no provider call before commit. Replay with same aggregate/idempotency key is a no-op.

### Idempotency
Client key on creation; deterministic `provider_idempotency_key` per external action, reused across retries. Duplicate replay never creates a second publish or spend.

### State machine
`created → authorized → queued → dispatching → executed`; branches to `uncertain`, `failed`, `dead_letter`, `blocked`, `cancelled`. `uncertain` forbids automatic retry.

### Reconciliation
Scheduled job queries provider by idempotency key/reference, resolves `uncertain` to reconciled states, compares action ledger with provider records and budget counters, raises incidents on duplicates/unexplained effects, and freezes tenant execution until resolved. All results appended to audit log.

### Fail-closed rule
Missing approval, non-owner decision, stale version/hash, missing FX snapshot, failed Arabic review, or budget validation failure stops before outbox/provider. No automatic budget increases.

## Section 5 — AI provider strategy

Gateway with text/image protocols, config-driven models/prices/priority/residency, usage and cost records, rate limits, circuit breaker, policy-gated fallback. One provider initially, no lock-in.

## Section 6 — Corrected MVP scope

**MUST HAVE:** auth, organization, business profile, product catalog, AI Studio, Arabic MSA + Darija style + French secondary, human Arabic review, creatives, calendar, approval center (owner decides), basic landing pages, leads, usage limits, responsive web, DZD+USD display.

**DEFERRED:** Android, complex CRM, advanced optimization, multi-platform ads, paid ad execution, direct social publishing, advanced analytics, billing. Extension points preserved.

## Section 7 — Documentation quality review

Checked all Phase 0 docs for stale French-first text, contradictory ADRs, outdated backlog items, and corrupted text. Findings corrected: ADR-009 explicitly superseded; ADR-005 amended; ADR-007 superseded; FX source marked unresolved; approver role unified to owner-only; deferred routes documented as `501`; backlog #1–#25 reconciled and #26/#27 added; Arabic summary repaired.

## Section 8 — Remaining risks

| Risk | Severity | Owner action |
|---|---|---|
| Final product-owner approval pending | High | Approve or amend |
| FX source + rounding unresolved | Medium | Select before financial execution |
| Provider residency constraints unknown | Medium | Legal/provider review |
| Plan quotas / USD precision unset | Low | Business confirmation |
| Postgres queue threshold unmeasured | Medium | Benchmark Phase 2 |
| Provider reconciliation API capability unverified | Medium | Confirm chosen provider supports idempotency lookup |
| Branch protection not enabled | Medium | Issue #14 before merge |

## Section 9 — Final corrections trace

ADR-017 (outbox/state machine/reconciliation), ADR-018 (owner-only approval), ADR-019 (Arabic quality), ADR-015 amended (FX unresolved + immutable snapshots), ADR-016 clarified (publishing/ads outside MVP). Final report: `12-final-acceptance-report.md`.
