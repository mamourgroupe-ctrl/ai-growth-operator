# Phase 2 — Frontend Information Architecture and Screen Specifications

**Status:** Proposed. No screens implemented in this planning task.

## Decision status

| Category | Summary |
|---|---|
| `OWNER_APPROVED` / `FROZEN` baseline | Next.js + TypeScript; Arabic-first RTL default; French as secondary locale; responsive web first; no direct social publishing; owner-only final approval. |
| `OWNER_PROPOSED` decisions | D-01–D-05, D-07, D-08 per `20-owner-decision-register.md`. Workspace navigation, reviewer flag and validation block are `FROZEN` engineering baselines. |
| `BLOCKED` / `DEFERRED` | French UI scope `BLOCKED`; final owner confirmation pending; lead PII redaction and lead UI `DEFERRED`; DZD-only user display. |
| External dependencies | Owner authorization for issue/document amendments; human Arabic reviewer availability; design system constraints. |
| Confirmed boundary | No ad budget, paid execution, FX, external campaign, or launch-control screen is in Phase 2. |
| Risks | Confusing Darija vs MSA; unintended publishing affordance; dense admin screens. |

## 1. IA

The approval center is Phase 2 content approval only. Internal landing create/edit/preview is `OWNER_PROPOSED`; leads, lead PII redaction and publish controls are `DEFERRED` to Phase 3 or later. The locale/RTL/style subset is a planning proposal. DZD-only user display applies; no foreign-currency UI, external publication or advertising execution screen is in Phase 2.

```text
Sign in / tenant selection (Phase 1)
  Dashboard
  Business setup
    Overview
    Manual onboarding wizard
    Conversational onboarding
    Products & offers
    Brand identity & assets
  Marketing
    Strategy
    Content studio
    Image studio
    Content calendar
    Review queue (Arabic reviewer)
    Approval center (owner)
  Growth surface
    Landing pages (internal create/edit/preview only)
  Settings
    Workspace & members
    Usage & cost
    Provider/model catalog (system admin only)
```

No buttons or menu items for external publish, ad launch, budget change, or automatic approval.

## 2. Screen specifications

### 2.1 Dashboard
- Purpose: tenant status, pending approvals, active products, validation failures, generation job health, quota usage.
- Data: counts only; no raw provider errors. Empty CTAs: “Complete business profile”, “Add first product”.

### 2.2 Manual onboarding wizard
- Sections: identity, contact, location, audience, objectives, USPs, competitors, tone/brand voice.
- Each step saves explicitly; validation shows required fields; back navigation preserves unsaved draft locally (no production PII in browser storage beyond session).

### 2.3 Conversational onboarding
- Chat panel with assistant proposals shown as structured cards: `field`, `proposed value`, `source utterance`, `confidence`, `accept/edit/reject`.
- Missing-fields summary. Confirm button writes only accepted cards; no silent fact writes.
- Style switch: MSA/Darija/French is for conversation style, not automatically the stored fact language.

### 2.4 Products and offers
- Table/cards; create/edit; price + currency + optional offer; availability; category; images.
- Inline validation for price mismatch in generated copy via validation panel.

### 2.5 Brand identity and assets
- Logo/colors/typography/tone rules; banned claims/disclaimers.
- Assets show upload status, scan status, usage count; private signed preview only.

### 2.6 Marketing strategy
- Output sections: analysis, audience, positioning, objectives, campaign angles, content plan; “generate draft” and “save as internal note”.
- All AI output clearly badged “AI draft — requires review”.

### 2.7 Content studio
- Type (post/ad/headline/CTA/idea), locale/style selector (`ar` MSA, `ar-DZ` Darija, `fr`), brief, product references.
- Draft editor with version history, validation findings, Arabic review status, submit-for-approval action.
- No social network selector or publish button.

### 2.8 Image studio
- Brief; optional product/brand references; aspect ratio preset; status/progress; preview via signed URL.
- Metadata: provider/model, created at, prompt template version, validation status.

### 2.9 Calendar
- Month/week views; items show title, content type, locale/style, status, internal scheduled date; filters for owner/editor/viewer.
- Drag/drop modifies internal date only; never publishes.

### 2.10 Review and approval center
- Reviewer queue: items requiring Arabic review; MSA/Darija/French tabs; reviewer approves language quality only.
- Owner queue: validation + review evidence, diff of version, approve/reject/request changes; reason required for negative decisions.
- Audit trail visible per request.

### 2.11 Landing pages
- Internal page builder: hero, products and SEO fields; mobile/draft preview; approved version state where already designed.
- No lead form submission, lead table, lead management screen, viewer redaction policy or publish button in Phase 2. All lead functionality and publishing are `DEFERRED` to Phase 3 or later.

### 2.12 Usage
- Owner-only: quota usage, estimated cost from snapshots, model usage breakdown; no provider keys/raw prompts.

## 3. Cross-cutting UI rules

- RTL default for `ar`; independent `dir` attributes for mixed numeric/Latin content; test long Arabic strings and French fallback.
- All destructive actions confirm; all AI-generated text carries provenance badge.
- Accessible forms with labels, error summaries, keyboard navigation; WCAG 2.1 AA target proposed.
- Client never receives public object URLs; signed URLs expire.
- Responsive breakpoints: mobile 360px, tablet 768px, desktop 1280px.

## 4. Explicit UI omissions

No “Publish to Facebook/Instagram/TikTok”, no “Launch campaign”, no “Set budget”, no “Auto-approve”, no Android download, no client-side provider/model dropdown.
