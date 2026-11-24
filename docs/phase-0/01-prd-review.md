# Corrected PRD — Phase 0 (final acceptance draft)

**Status:** Corrected against product-owner decisions; awaiting final explicit approval.
**Source of truth:** Approved decisions in the two audit/acceptance messages; `README.md`; verified repository state. No standalone PRD file exists in the repository.

## 1. Verified product decisions

| Decision | Status | Implementation implication |
|---|---|---|
| Market: Algeria | Confirmed | `Africa/Algiers`, DZD base, Arabic-first UX |
| Customer: small businesses | Confirmed | One lean workspace per business |
| Multi-tenant SaaS | Confirmed | Organization (tenant) boundary; shared schema + RLS |
| Human approval before external publishing/ad spend | Confirmed | Owner-only final approval; fail-closed gate; outbox + reconciliation |
| Currency display: DZD and USD | Confirmed | Dual display; immutable FX snapshots; **FX source is an unresolved configuration decision** |
| Primary interface: responsive web | Confirmed | MVP, Arabic/RTL-ready |
| Language priority: Arabic first incl. Algerian Darija, then French | Confirmed | `ar` default (MSA), `ar-DZ` Darija style, `fr` secondary |
| Android: future phase | Confirmed | No Android work in MVP |
| Direct social publishing and paid ad execution | Confirmed deferred | Extension points and approval safety preserved; no implementation in MVP |

## 2. Product definition

AI Growth Operator is a multi-tenant SaaS for Algerian small businesses that produces Arabic-first marketing copy and creative assets, organizes them in a content calendar, routes them through Arabic-quality review and an owner approval center, and supports basic landing pages and lead capture. External social publishing and paid advertising execution are out of MVP scope but their approval/safety contracts are already designed.

**Vocabulary:** "Organization" is the product term; `tenant` is the technical identifier.

## 3. Language and Arabic quality policy

- UI default locale: `ar` (Modern Standard Arabic), RTL-ready. `fr` is secondary. Darija UI copy may be added later without schema change.
- Content generation styles/locales:
  - `ar` — Modern Standard Arabic (MSA).
  - `ar-DZ` — Algerian Darija, a **distinct content-generation style** of Arabic, not a separate UI locale.
  - `fr` — French, secondary.
- Prompt templates are locale/style-aware and versioned in the AI gateway.
- **Human Arabic review process (MVP):**
  1. Generated `ar` or `ar-DZ` content enters `arabic_reviews` as `pending` before it can be submitted for approval.
  2. A designated Arabic reviewer (an editor flagged `is_arabic_reviewer`) checks MSA grammar/spelling, Darija authenticity and regional appropriateness, brand voice, cultural fit, and factual claims (prices/offers).
  3. Reviewer records `approved` or `changes_requested` with notes; `changes_requested` returns the item to draft.
  4. Only reviewed Arabic content can be submitted by an editor to the owner approval center.
  5. French content follows the same approval gate without the Arabic review step.

## 4. Currency policy

- Base currency: `DZD`. Both DZD and USD are displayed wherever money appears.
- **FX rate source is unresolved** — a configuration decision requiring product-owner selection before implementation (candidate: central bank / licensed provider / manual admin rate). Rounding and effective-date policy are also open.
- Authoritative `fx_rate_snapshots` rows are immutable once written; each carries rate, source, observed/captured time, and hash.
- Displayed USD uses a server-selected snapshot; clients cannot submit rates.
- Financial approvals store native ceiling, USD display amount, and `fx_rate_snapshot_id`. No spend decision uses an unsnapshotted rate.

## 5. MVP scope — MUST HAVE

1. Authentication (email/password, sessions, CSRF).
2. Organization management (create, members, roles).
3. Business profile (name, sector, contact, wilaya, brand voice).
4. Product catalog.
5. AI Marketing Studio (text + creative generation, job status, usage limits).
6. Arabic marketing copy (`ar` MSA, `ar-DZ` Darija style) and French secondary.
7. Human Arabic quality review.
8. Creative generation via provider-independent gateway.
9. Content calendar.
10. Approval center — **owner is the only final approver**; editors prepare and submit; viewers read only.
11. Basic landing pages (internal publish, approval-gated).
12. Lead management.
13. AI usage limits.
14. Responsive Arabic-first web.
15. DZD + USD display from immutable FX snapshots.

## 6. Explicitly deferred

- Android application.
- Complex CRM.
- Advanced automated campaign optimization.
- Multi-platform advertising automation and paid ad execution.
- Direct social-network publishing.
- Advanced analytics.
- Billing/payment processing (plan quotas only).
- Full DAM/versioning; multi-provider user-facing selector.

Architectural extension points (`approval_requests`, `external_actions`, transactional outbox, reconciliation, ad/social tables) are documented now but not activated.

## 7. Roles

| Role | Capability |
|---|---|
| Owner | Final approval authority for all approvals, including ad-spend when enabled; member/settings management |
| Editor | Content preparation, submission for review/approval, creative generation, product/landing page editing |
| Viewer | Read-only access |

## 8. Financial execution safety

Transactional outbox, deterministic idempotency keys, an explicit external-execution state machine (including `uncertain`), and a reconciliation process are required so an ambiguous provider result never causes duplicate publishing or duplicate spending. See `11-architecture-audit.md` §4 and `10-architecture-decision-log.md` ADR-017.

## 9. Success metrics (proposed)

Time to first Arabic draft <60s p95; time to first owner-approved item <10 min; approval rejection rate tracked; weekly active organizations tracked; non-AI API p95 <300ms.

## 10. Remaining open questions

1. Final product-owner approval of this corrected PRD.
2. FX rate source, rounding, and effective-date policy.
3. Provider data-residency constraints and approved provider list.
4. Exact plan quotas and USD display precision.

Approver roles and Arabic review process are now resolved and no longer open.

## 11. Verdict

Ready for final approval. Phase 1 remains blocked until explicit approval.
