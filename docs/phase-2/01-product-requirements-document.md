# Phase 2 — Product Requirements Document (engineering preparation)

**Status:** Prepared for owner review. No implementation authorized.  
**Baseline:** Phase 1 conditionally accepted at `aaf37f1`; code baseline `562575a`.  
**Source of truth for approved decisions:** `docs/phase-0/01-prd-review.md`, `docs/phase-0/10-architecture-decision-log.md`, `docs/phase-1/engineering-report.md`, and the owner's Phase 2 planning brief.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Preserve all Phase 0 decisions: modular monolith, multi-tenant SaaS, FastAPI/Next.js/PostgreSQL, RLS+RBAC, Arabic-first/Darija style/French secondary, no direct social publishing or paid execution in MVP. Phase 1 conditionally accepted. Owner-confirmed Phase 2 boundary: content approval only, as recorded in §0 below. |
| `OWNER_PROPOSED` decisions | D-01 owner-only final approval; D-02 internal landing create/edit/preview only with all lead functionality `DEFERRED`; D-03 DZD-only user-facing with USD internal AI cost; D-04 configurable tenant quotas; D-05 study sectors before selection; D-07 benchmark-based AI provider selection; D-08 comparison-based storage selection. See `20-owner-decision-register.md`. |
| `BLOCKED` items | Final owner confirmation for seven `OWNER_PROPOSED` decisions; D-04 numeric values; D-05 sector evidence; D-07 benchmark evidence; D-08 storage comparison/legal evidence. |
| External dependencies | Provider legal/privacy review, ANPDP requirements, provider benchmark results, owner authorization for issue/document corrections. |
| Risks | Scope growth; role ambiguity; unmeasured Darija quality; AI output treated as trusted; unresolved legal transfer gate. |

## 0. Owner-confirmed scope boundary (recorded 2026-11-24 UTC)

**Confirmed:** Phase 2 includes automated preliminary content validation, human content review, content approval permissions, immutable/versioned content approval snapshots, approval history and audit trail, invalidation of previous approval when content changes, content calendar and content management, AI usage quotas and cost tracking for SaaS operation. Landing pages are `OWNER_PROPOSED` for internal create/edit/preview only; lead management is `DEFERRED` to Phase 3 or later.

**Confirmed exclusions:** Phase 2 MUST NOT include advertising budget approvals, advertising expenditure, paid advertising execution, external advertising platform campaign execution, external paid-action authorization, advertising FX snapshots, paid-action outbox and reconciliation, external execution state machines, or automatic campaign launching. These remain Phase 3.

**Preliminary owner choices:** D-01 records owner-only final approval, with editors preparing/submitting, Arabic reviewers reporting findings and viewers read-only. D-02 limits Phase 2 landing pages to internal create/edit/preview and defers all lead functionality and publishing. Both remain `OWNER_PROPOSED`, pending final owner confirmation.

## 1. Product objective

Enable an Algerian small business to describe its identity once, generate Arabic/Darija/French marketing material with AI, validate it automatically and humanly, organize it in an internal calendar, obtain owner approval, and create/edit/preview basic internal landing pages. Public publishing, lead capture, external social publishing and paid ad execution remain outside Phase 2.

## 2. Users and permissions

| Persona | Phase 2 capabilities |
|---|---|
| Owner | Everything an editor can do; final approval/rejection; member management; sees usage/cost. |
| Editor | Create/edit business data, products, brand assets, generate content/images, submit for Arabic review and approval, manage calendar, create/edit/preview landing pages. Lead management is `DEFERRED`. |
| Viewer | Read-only dashboards, catalog, content, calendar and internal landing page previews. Lead lists are `DEFERRED`. |
| Arabic reviewer | Editor with `is_arabic_reviewer=true`; approves MSA/Darija language quality; never grants final approval. |
| System admin (non-tenant) | Provider configs/model registry/pricing; no tenant business data access by default. |

## 3. Scope packages

Scope labels below are planning labels. Confirmed Phase 2/Phase 3 ownership follows §0, not the historical issue titles.

### 2A — Business Foundation
- Business profile: name, description, category, location/wilaya, target audience, objectives, USPs, competitors, preferred tone, contact details.
- Product catalog: products/services, descriptions, features, price + original currency, offers/discounts, availability, categorization, images.
- Brand identity: logos, colors, typography, references, voice, guidelines, asset management (minimal, no full DAM).
- Onboarding: manual wizard **and** conversational assistant. Assistant extracts structured fields, shows a reviewable summary, lists missing/low-confidence fields, and writes only after explicit user confirmation.

### 2B — AI Intelligence
- Provider-independent text/image gateway, model registry, usage/cost tracking, quotas, rate limits, timeouts/retries, policy-gated fallback.
- Marketing strategy outputs: analysis, audience, objectives, positioning, angles, campaign concepts, content strategy.
- Marketing studio: social posts, ad copy, headlines, descriptions, CTAs, promotional messages, weekly ideas in `msa` (`ar`), `darija` (`ar-DZ`), and `fr`.
- Darija is a distinct style, not a translation of MSA.

### 2C — Creative and Governance
- Image generation with optional product references, metadata/history, output validation, brand consistency where technically possible.
- Content calendar: monthly/weekly views of drafts and approved items, internal dates/status only; no publishing.
- Approval center: submit, approve, reject with reason, request changes, versions, approver/timestamp. D-01 `OWNER_PROPOSED` preserves owner-only final approval; editors submit, Arabic reviewers report findings and viewers read. Material edit of approved content invalidates approval and creates a new version. Ad-spend, FX, outbox, external actions, and campaign execution are Phase 3 only.
- Automated validation before review: unsupported claims, price mismatch, missing fields, malformed output, duplicates, unsafe content, detectable brand violations. Never replaces human approval. `block` findings are non-overridable; `warn` findings follow the documented owner override rule.

### 2D — Conversion Foundation (`OWNER_PROPOSED` internal-only boundary)
- Basic landing pages with product presentation, internal preview, responsive layout and SEO metadata.
- Drafts and version history are supported where already included in the approved design.
- No public publishing, external publication, public lead ingestion, lead management, lead table/API/UI, advanced CRM or internal publish-execution endpoint is in Phase 2.
- All lead functionality and publishing execution are `DEFERRED` to Phase 3 or later. This section is a preliminary owner proposal, not final approval.

## 4. Explicit non-goals

Android; direct social publishing; real ad execution/spend; advanced CRM; full billing; automatic budget increases; autonomous approval by AI; production data in lower environments; microservices; client-selectable provider URLs; real FX rate selection or conversion (no Phase 2 FX source).

## 5. Core user flows

1. Owner registers organization (Phase 1) → completes manual or assisted onboarding → reviews and confirms extracted facts → profile becomes source of truth for generation.
2. Editor adds products/brand assets → requests generation with style → job runs through gateway → output stored as untrusted draft → automated validation → Arabic review if `ar`/`ar-DZ` → submit → owner decides.
3. Editor schedules validated content in the internal calendar → approved content may be used in internal landing page copy → editor previews the internal page. No publish or lead-capture step exists in Phase 2.
4. Owner views usage/cost from recorded snapshots.

## 6. Measurable acceptance metrics (proposed, require owner confirmation)

| Metric | Target |
|---|---|
| Time to first Arabic draft | p95 < 60 s |
| Time to first owner-approved item | median < 10 min in pilot |
| Structured output schema validity | ≥ 95% in benchmark |
| Price mismatch in generated copy | 0 in benchmark |
| Darija reviewer score | mean ≥ 4/5 for authenticity and cultural fit |
| Non-AI API latency | p95 < 300 ms |
| Approval bypass attempts | 100% blocked in automated security suite |
| Tenant isolation | 0 cross-tenant rows in RLS/API suite |

All values above are **proposed targets**, not measured results. Measurement method: use the synthetic benchmark harness for schema/price/injection metrics; blind native reviewer scoring for Darija; CI timing for non-AI API latency; RLS/role suites for isolation and bypass. Results must be labelled `target`, `measured`, or `rejected` with run date and evidence path.

## 7. Pilot sector framework

Evaluate each candidate 1–5 on: marketing content demand, product clarity, onboarding ease, pilot availability, repeat use cases, measurable value, regulatory complexity, AI content suitability.

| Candidate sector | Demand | Clarity | Onboarding | Availability | Repeat | Measurement | Regulatory | AI suitability | Trade-off |
|---|---|---|---|---|---|---|---|---|---|
| Bakeries / patisseries | 5 | 5 | 5 | 5 | 5 | 4 | 3 (food/health claims) | 5 | Hypothesis/research candidate only; no owner selection. Would need health-claim controls if later studied. |
| Hair/beauty salons | 4 | 4 | 4 | 4 | 5 | 4 | 3 (service claims) | 4 | Strong repeat content but appointment workflow is out of scope; may create unmet expectations. |
| Local cafés / restaurants | 5 | 4 | 4 | 4 | 5 | 4 | 3 (food/alcohol claims) | 4 | Similar to bakeries but menu volatility and licensing sensitivity are higher. |

**Framework reconciliation:** the earlier three-sector table (bakeries/patisseries, salons, cafés/restaurants) and the Phase 2.5 five-sector framework (retail/commerce, tourism/travel, professional services, manufacturing/production, restaurants/hospitality) are both **assumption-based**. Bakeries/patisseries is a food-retail/hospitality sub-segment, not an approved sector. No market validation evidence exists in the repository and **no pilot sector has been selected**.

Low-cost validation experiments before any owner selection: owner interviews; willingness-to-pay card test; two-week content-volume diary; synthetic-data generation demo; blind Arabic/Darija scoring. Sector-neutral foundations may proceed with synthetic fixtures; sector-specific rules wait for selection.

## 8. Conflicts with existing approved roadmap

1. The Phase 2/Phase 3 boundary is reconciled: #23 Phase 2 content approval core only; ad-spend, FX, external actions, outbox and reconciliation remain Phase 3. #24 landing/lead scope is `OWNER_PROPOSED` internal pages only with leads `DEFERRED`; #25 UI subset is `OWNER_PROPOSED` pending final confirmation.
2. Conversational onboarding and automated validation were new items not in issues #16–#27; proposed backlog IDs are `P2-N1` and `P2-N2`. These IDs were not created as GitHub issues.
3. Image generation remains in “AI-generated content”, but provider, editing capability, licensing, and storage decisions require benchmark and legal/contract evidence.
4. Existing issue titles/labels still say Phase 3 for #23/#24/#25. This is a tracker contradiction to be corrected by the owner, not evidence of a different decision.

## 9. Open questions for owner

- Final confirmation is pending for D-01, D-02, D-03, D-04, D-05, D-07 and D-08; all remain `OWNER_PROPOSED`.
- D-04 numeric quota values require system-administrator proposal and owner approval; no enforcement before approval.
- D-05 sector-specific rules require a selection decision; sector-neutral foundations are not blocked.
- D-03 establishes DZD-only user-facing display and internally recorded USD AI cost; it does not create an FX source or authorize conversion.
- French UI breadth remains `BLOCKED`; GitHub issues were not changed. Do not repeat preliminary decisions already recorded in `20-owner-decision-register.md`.
