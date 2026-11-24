# Corrected PRD — Phase 0 (post-audit)

**Status:** Corrected against product-owner decisions supplied in the architecture-audit request. Awaiting final product-owner approval.
**Source of truth:** Approved decisions listed in the audit request; `README.md`; verified repository state.
**Note:** No standalone PRD file exists in the repository. This document is the canonical Phase 0 PRD until a separate PRD is supplied.

## 1. Verified product decisions

| Decision | Status | Implementation implication |
|---|---|---|
| Market: Algeria | Confirmed | Default timezone `Africa/Algiers`, base currency DZD, Arabic-first UX |
| Customer segment: small businesses | Confirmed | One lean workspace per business, low operational overhead |
| Product: multi-tenant SaaS | Confirmed | Organization (tenant) as isolation boundary; shared schema + RLS |
| Autonomy: human approval required before external publishing or advertising expenditure | Confirmed | Approval center; fail-closed execution gate; versioned immutable approvals |
| Currency display: DZD and USD | Confirmed | Dual display everywhere money appears; FX snapshot on approvals |
| Primary interface: responsive web application | Confirmed | Web is MVP, not a later phase |
| Language priority: Arabic first including Algerian Darija, then French | Confirmed | UI default `ar`; copy locales `ar`, `ar-DZ`, `fr` |
| Android: future phase | Confirmed | No Android work in MVP or Phase 1 |

## 2. Product definition

AI Growth Operator is a multi-tenant SaaS for Algerian small businesses that helps a small team produce Arabic-first marketing copy and creative assets, organize them in a content calendar, obtain explicit human approval, and publish only through a controlled action path. Basic landing pages and lead capture are included. Advertising activation is designed for safety but platform automation is deferred.

**Technical vocabulary:** "Organization" is the product-facing name; `tenant` is the technical identifier.

## 3. Language and locale policy

- UI locale priority: `ar` (Arabic, default) → `fr` (French, secondary). Darija UI copy may be added later without schema change.
- AI copy locales: `ar` (Modern Standard Arabic), `ar-DZ` (Algerian Darija, first-class), `fr`.
- All generated content stores its locale; review workflow shows locale explicitly.
- Prompt templates are locale-aware and versioned in the AI gateway; no French-only assumptions remain.

## 4. Currency policy

- Base currency: `DZD`. Display currencies: `DZD` and `USD` simultaneously where monetary values are shown.
- `fx_rates` stores dated rate snapshots with source; displayed USD values use a snapshot, not a live undetermined rate.
- Approvals store an exact ceiling in its native currency plus USD display amount and `fx_rate_snapshot_id`.
- No spending decision is ever based on an unsnapshotted conversion.

## 5. MVP scope — MUST HAVE

1. Authentication (email/password, sessions, CSRF).
2. Organization management (create, members, roles).
3. Business profile (name, sector, contact, address, brand voice).
4. Product catalog (products/services used in copy generation).
5. AI Marketing Studio (text + creative generation, job status, usage limits).
6. Arabic marketing copy (`ar`, `ar-DZ`) with French secondary.
7. Creative generation via provider-independent gateway.
8. Content calendar (scheduled content items).
9. Approval center (publish and ad-spend approvals, versioned snapshots).
10. Basic landing pages with publish approval.
11. Lead management (leads from landing pages).
12. AI usage limits per plan.

## 6. Explicitly deferred

- Android application.
- Complex CRM.
- Advanced automated campaign optimization.
- Multi-platform advertising automation and direct social publishing.
- Advanced analytics.
- Billing/payment processing (plan quotas only).
- Full digital-asset management and brand-asset versioning.
- Multi-provider user-facing selector (gateway supports future providers internally).

Advertising tables (`ad_accounts`, `ad_campaigns`, `ad_budget_limits`, `spend_events`) are documented for safety but not implemented in MVP.

## 7. Success metrics (proposed, confirm at approval)

| Metric | Proposed target |
|---|---|
| Time to first Arabic draft | < 60 seconds p95 |
| Time to first approved publish-ready item | < 10 minutes after signup |
| Approval rejection rate | Track only |
| Weekly active organizations | Track from pilot |
| API p95 latency (non-AI) | < 300 ms |

## 8. Human approval model

Publishing and advertising activation always require explicit approval. Every approved advertising action carries an exact budget ceiling; budget changes supersede prior approvals; approved snapshots are immutable; no automatic budget increases; every external action is recorded. Full design in `11-architecture-audit.md` Section 4 and `03-database-design.md`.

## 9. Remaining open questions

1. Final product-owner approval of this corrected PRD.
2. FX rate source and rounding rules.
3. Provider data-residency constraints and approved provider list.
4. Darija content review ownership and quality bar.
5. Exact plan quotas and USD display precision.
6. Whether editor or owner may approve (current proposal: owner + editor for content; owner only for ad spend).

## 10. Review verdict

Ready for product-owner approval. Phase 1 remains blocked until approval is explicit.
