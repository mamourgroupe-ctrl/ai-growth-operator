# Phase 2 — Product Requirements Document (engineering preparation)

**Status:** Prepared for owner review. No implementation authorized.  
**Baseline:** Phase 1 conditionally accepted at `aaf37f1`; code baseline `562575a`.  
**Source of truth for approved decisions:** `docs/phase-0/01-prd-review.md`, `docs/phase-0/10-architecture-decision-log.md`, `docs/phase-1/engineering-report.md`, and the owner's Phase 2 planning brief.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Preserve all Phase 0 decisions: modular monolith, multi-tenant SaaS, FastAPI/Next.js/PostgreSQL, RLS+RBAC, Arabic-first/Darija style/French secondary, owner-only final approval, no direct social publishing or ad execution in MVP. Phase 1 conditionally accepted. |
| Proposed decisions | Split delivery into 2A Business Foundation, 2B AI Intelligence, 2C Creative & Governance, 2D Conversion Foundation; add automated validation and conversational onboarding as explicit new work items. |
| Open questions | Pilot sector; AI text/image provider selection; object storage provider; FX source/rounding; exact quotas; whether #23/#24/#25 move from Phase 3 into Phase 2. |
| External dependencies | Provider legal/privacy review, ANPDP requirements, provider benchmark results, owner approval of roadmap re-baseline. |
| Risks | Scope growth; moving approval/landing pages earlier than approved roadmap; Darija quality without measurement; AI output treated as trusted. |

## 1. Product objective

Enable an Algerian small business to describe its identity once, generate Arabic/Darija/French marketing material with AI, validate it automatically and humanly, organize it in an internal calendar, obtain owner approval, and use it on a basic landing page that captures leads. External social publishing and paid ad execution remain outside MVP.

## 2. Users and permissions

| Persona | Phase 2 capabilities |
|---|---|
| Owner | Everything an editor can do; final approval/rejection; member management; sees usage/cost. |
| Editor | Create/edit business data, products, brand assets, generate content/images, submit for Arabic review and approval, manage calendar, create landing pages, view leads. |
| Viewer | Read-only dashboards, catalog, content, calendar, landing pages and lead list (redacted contact fields if owner policy requires). |
| Arabic reviewer | Editor with `is_arabic_reviewer=true`; approves MSA/Darija language quality; never grants final approval. |
| System admin (non-tenant) | Provider configs/model registry/pricing; no tenant business data access by default. |

## 3. Scope packages

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
- Approval center: submit, approve, reject with reason, request changes, versions, approver/timestamp. Owner-only final decision. Material edit of approved content invalidates approval and creates new version.
- Automated validation before review: unsupported claims, price mismatch, missing fields, malformed output, duplicates, unsafe content, detectable brand violations. Never replaces human approval.

### 2D — Conversion Foundation
- Basic landing pages with product presentation, contact form, responsive layout, SEO metadata.
- Leads: contact info, source, landing page, submission time, basic status, tenant isolation. No advanced CRM.

## 4. Explicit non-goals

Android; direct social publishing; real ad execution/spend; advanced CRM; full billing; automatic budget increases; autonomous approval by AI; production data in lower environments; microservices; client-selectable provider URLs; real FX rate selection (remains unresolved).

## 5. Core user flows

1. Owner registers organization (Phase 1) → completes manual or assisted onboarding → reviews and confirms extracted facts → profile becomes source of truth for generation.
2. Editor adds products/brand assets → requests generation with style → job runs through gateway → output stored as untrusted draft → automated validation → Arabic review if `ar`/`ar-DZ` → submit → owner decides.
3. Editor schedules validated content in internal calendar → approved content can be used in landing page copy → owner approves landing page before internal publish → form captures leads.
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

## 7. Pilot sector framework

Evaluate each candidate 1–5 on: marketing content demand, product clarity, onboarding ease, pilot availability, repeat use cases, measurable value, regulatory complexity, AI content suitability.

| Candidate sector | Demand | Clarity | Onboarding | Availability | Repeat | Measurement | Regulatory | AI suitability | Trade-off |
|---|---|---|---|---|---|---|---|---|---|
| Bakeries / patisseries | 5 | 5 | 5 | 5 | 5 | 4 | 3 (food/health claims) | 5 | Recommended: simple catalog, daily promos, visual content; must block unsupported health claims. |
| Hair/beauty salons | 4 | 4 | 4 | 4 | 5 | 4 | 3 (service claims) | 4 | Strong repeat content but appointment workflow is out of scope; may create unmet expectations. |
| Local cafés / restaurants | 5 | 4 | 4 | 4 | 5 | 4 | 3 (food/alcohol claims) | 4 | Similar to bakeries but menu volatility and licensing sensitivity are higher. |

**Proposal:** run first pilot with bakeries/patisseries, subject to owner approval. Do not build sector-specific features until approved.

## 8. Conflicts with existing approved roadmap

1. Existing roadmap places approval center (#23), landing pages/leads (#24), and RTL/UI work (#25) in Phase 3. This brief places approval and conversion foundation in Phase 2. **Resolution required:** owner must approve re-baselining or Phase 2C/2D must be limited to contracts/drafts only.
2. Conversational onboarding and automated content validation are new items not in issues #16–#27. Proposed as new backlog entries, not created in this task.
3. Image generation expands minimal `brand_assets`/`creative_assets` into a real workflow; remains within “AI-generated content” scope but requires storage and validation decisions.

## 9. Open questions for owner

- Approve/reject roadmap re-baseline for #23/#24/#25.
- Approve pilot sector.
- Approve quota numbers and cost caps.
- Confirm whether French is a UI locale in Phase 2 or remains secondary content style only (current ADR says UI `ar` default, `fr` secondary).
- Confirm FX source and rounding before any money display beyond static DZD label.
