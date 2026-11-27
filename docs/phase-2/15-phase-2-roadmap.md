# Phase 2 — Roadmap (planning proposal)

**Status:** Proposed roadmap with seven `OWNER_PROPOSED` owner choices; final owner confirmation pending. No implementation started.

## Decision status

| Category | Summary |
|---|---|
| `OWNER_APPROVED` baseline | Phase 0/1 foundation completed and conditionally accepted; owner-confirmed Phase 2 includes automated validation, human content review, content approval permissions, immutable approval snapshots, approval history/audit, invalidation on content change, content calendar/management, AI quota/cost tracking. No external publishing/spend; no advertising execution. |
| `OWNER_PROPOSED` decisions | D-01–D-05, D-07, D-08 per `20-owner-decision-register.md`; internal landing create/edit/preview only with all leads `DEFERRED`; DZD-only user display; configurable quotas; sector-neutral work with synthetic fixtures; benchmark/comparison-based selection. Workstreams 2A–2D and documented-only issue proposals remain planning proposals. |
| `BLOCKED` / `DEFERRED` | Final owner confirmation; numeric quota values; pilot-sector evidence; benchmark/storage evidence; legal evidence; French UI scope. Lead functionality and publishing execution `DEFERRED`. |
| External dependencies | Benchmark results (not run), legal opinion, human Arabic reviewer, provider accounts, owner verification of branch protection #14. |
| Risks | Re-baseline conflict; scope creep; provider cost/legal blockage; unresolved pilot sector. |
| Observation date | 2026-11-24: issues #23/#24/#25 still OPEN, `[Phase 3]`-titled, no milestone, label `enhancement`; PR #15 OPEN/DRAFT/unmerged/MERGEABLE at `8da2f9a`. |

## 1. Preconditions (blocking)

| Gate | Owner action / evidence |
|---|---|
| `G0` roadmap | Obtain final owner confirmation of D-01–D-05, D-07, D-08. Issue amendments remain documented only; no issue was edited. |
| `G1` pilot | Study sector candidates; treat retail, tourism, professional services, manufacturing, restaurants/hospitality, bakery and salon/café examples as research hypotheses only. Sector-neutral foundations may proceed with synthetic fixtures. |
| `G2` provider | Run documented benchmarks covering quality, MSA, Darija, French, cost, latency, reliability, privacy and retention; no selection or winner claim in this document. |
| `G3` storage | Document a comparison covering residency, security, encryption, backup/recovery, DPA, retention, egress and total cost; no storage selection. |
| `G4` legal/privacy | Confirm Law 25-11 obligations, DPO/register/log position, cross-border transfer authorization; approve provider data categories. |
| `G5` limits | System administrator proposes numeric AI quotas/cost caps; owner reviews and approves; no numerical enforcement before approval. **Advertising FX remains Phase 3**; D-03 permits no FX source or conversion. |
| `G6` platform | Verify `main` branch protection (#14) before production release; current status NOT VERIFIED (API 403). |

## 2. Workstreams

### 2A — Business foundation (issues #16, #17, new onboarding issue)
1. Business profile + brand assets/guidelines.
2. Product catalog with price/currency/offer/availability.
3. Manual onboarding wizard.
4. Conversational onboarding (proposed new issue; gate on privacy review).
Exit criteria: tenant-scoped CRUD, RLS tests, owner/editor/viewer matrix, synthetic fixtures, no provider calls with real data.

### 2B — AI Intelligence (issues #9, #18, #20, #21, #22)
1. Hardened job queue (#20) — prerequisite for generation.
2. Provider-independent gateway with fake adapters (#9).
3. Model registry, usage/cost snapshots, quotas (#18/#21).
4. Configurable quota infrastructure and AI price snapshots for SaaS operating cost (#18/#21); no numerical quota enforcement before owner approval. **No advertising FX snapshot or paid execution table in Phase 2**; D-03 sets DZD-only user display with internally recorded USD AI cost.
Exit criteria: benchmark executed with corrected, valid fixtures; provider decision recorded in ADR; USD AI price snapshot accuracy test; no client provider selection; numeric limits approved by owner before enforcement.

### 2C — Content, validation and governance (issues #8, #27, #19, new validation issue, possible #23)
1. Content studio APIs and versioning (#8).
2. Automated validation (proposed new issue).
3. Human Arabic review (#27).
4. Image studio + internal content calendar (#19).
5. Content approval center: automated validation, submission, Arabic review, immutable snapshots and approval history are owner-confirmed Phase 2. #23 is proposed to be split: content approval in Phase 2, ad-spend/FX/external action/outbox in Phase 3. D-01 `OWNER_PROPOSED` preserves owner-only final approval; final confirmation pending.
Exit criteria: no submit with `block` findings; no `ar-DZ` without human review; owner-only-decision negative tests; snapshots immutable; no publish endpoint in Phase 2.

### 2D — Conversion foundation (possible #24/#25, gated)
1. Internal landing create/edit/preview with drafts and version history where already designed.
2. Lead capture, lead table, public lead ingestion, lead APIs/UI, redaction and publishing execution are `DEFERRED` to Phase 3 or later.
3. Required Arabic RTL/Darija UI subset (#25 partial) only if re-baselined; DZD-only user display.
Exit criteria: no lead table/route/UI, no publish-execution endpoint, no external side effect, responsive RTL QA. D-02 remains `OWNER_PROPOSED`.

## 3. Delivery sequence (proposed)

```text
G0-G5 decisions
  -> 2A business foundation
  -> #20 queue hardening
  -> #9/#18/#21 gateway + usage (fake providers first)
  -> benchmark + provider/storage ADRs
  -> 2B content studio + validation + Arabic review
  -> 2C images/calendar
  -> content approval core (Phase 2; #23 content slice only)
  -> internal landing preview/draft scope only (leads/publish `DEFERRED`)
  -> QA/human review -> G6 production readiness
  -> Phase 3 only: #23 ad-spend/external execution, #22 advertising FX, #26 outbox/reconciliation
```

## 4. Estimate ranges (rough, not commitments)

| Workstream | Rough engineering range |
|---|---|
| 2A | 3–5 developer-days |
| 2B | 5–8 developer-days + benchmark/review time |
| 2C | 5–8 developer-days (+3–5 if #23 included) |
| 2D | 4–7 developer-days (+UI subset if #25 included) |
| Legal/provider/security review | parallel, owner-driven; not estimated |

## 5. What is explicitly deferred

Phase 3 or later: #26 outbox/reconciliation and external execution state machines; #22 advertising FX snapshots; #23 ad-spend approval/external paid-action authorization/campaign launching; full responsive UI #12 unless partially re-baselined; staging/production deployment #13; advanced CRM; billing; Android; paid ads; social publishing.

Under D-02, the following are also `DEFERRED` to Phase 3 or later:

- `leads` database table.
- Public lead ingestion.
- Lead management APIs and UI.
- Lead lifecycle and retention implementation.
- Internal publishing execution.
- Public publishing and public URLs.
- Publication event execution.
- External hosting and custom-domain support.

No external side effect, Leads data lifecycle or publishing execution is authorized in Phase 2.

## 6. Roadmap conflicts to resolve before implementation

1. Owner-confirmed Phase 2 includes content approval, validation, review and AI quota/cost tracking; current issues #23/#24/#25 remain `[Phase 3]` (observed 2026-11-24). A split of #23 and partial re-baseline of #24/#25 are **proposals documented in `16-github-issue-backlog.md` only**; no issue was edited. D-02 preliminarily limits landing scope and defers leads.
2. “Automation” additions (onboarding assistant, automated validation) have no GitHub issues. Proposed issues are documented in `16-github-issue-backlog.md`; no issue was created.
3. Subscription-based usage limits (#21) require a plan/billing decision, but billing is a non-goal. D-04 `OWNER_PROPOSED`: fixed per-tenant configurable quotas; system administrator proposes numbers and owner approves; no enforcement before approval.
4. Sector examples in `01-product-requirements-document.md` and prior lists are research hypotheses/candidates only. No pilot sector is selected; sector-neutral work may proceed with synthetic fixtures.
5. D-03 `OWNER_PROPOSED`: DZD-only user-facing, USD AI cost evidence internally; no conversion, FX source or foreign-currency user display. Advertising FX is Phase 3.
