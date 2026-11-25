# Phase 2 — Roadmap (planning proposal)

**Status:** Proposed, subject to owner approval. No implementation started.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Phase 0/1 foundation completed and conditionally accepted; no external publishing/spend; owner-only approval; modular monolith. |
| Proposed decisions | Four workstreams 2A–2D with gates; #23/#24/#25 re-baseline requested; new issues proposed for onboarding assistant/content validation. |
| Open questions | Owner approval; pilot sector; provider/storage; legal gate; quotas; FX source. |
| External dependencies | Benchmark results, legal opinion, human Arabic reviewer, provider accounts, branch protection #14. |
| Risks | Re-baseline conflict; scope creep; provider cost/legal blockage. |

## 1. Preconditions (blocking)

| Gate | Owner action / evidence |
|---|---|
| `G0` roadmap | Approve Phase 2 roadmap and decide whether #23/#24/#25 move from Phase 3 into Phase 2C/2D |
| `G1` pilot | Approve pilot sector from three-candidate framework in `01-product-requirements-document.md` |
| `G2` provider | Review benchmark and approve text/image providers; no selection in this document |
| `G3` storage | Review object-storage evaluation and approve provider/residency |
| `G4` legal/privacy | Confirm Law 25-11 obligations, DPO/register/log position, cross-border transfer authorization; approve provider data categories |
| `G5` limits | Approve quotas, cost caps, FX source/rounding |
| `G6` platform | Verify `main` branch protection (#14) before production release |

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
4. FX snapshot table and dual display only after source approved (#22).
Exit criteria: benchmark executed with identical prompts/data; provider decision recorded in ADR; cost snapshot accuracy test; no client provider selection.

### 2C — Content, validation and governance (issues #8, #27, #19, new validation issue, possible #23)
1. Content studio APIs and versioning (#8).
2. Automated validation (proposed new issue).
3. Human Arabic review (#27).
4. Image studio + internal calendar (#19).
5. Approval center (#23) **only if owner approves re-baseline**; otherwise contracts only.
Exit criteria: no submit with blocking validation; no `ar-DZ` without human review; owner-only decision with negative tests; no publish action.

### 2D — Conversion foundation (possible #24/#25, gated)
1. Landing page basic builder with internal publish.
2. Lead capture and owner/editor view with redaction.
3. Required Arabic RTL/Darija UI subset (#25 partial) only if #24/#25 re-baselined.
Exit criteria: approved version required; no external side effect; lead PII protected; responsive RTL QA.

## 3. Delivery sequence (proposed)

```text
G0-G5 decisions
  -> 2A business foundation
  -> #20 queue hardening
  -> #9/#18/#21 gateway + usage (fake providers first)
  -> benchmark + provider/storage ADRs
  -> 2B content studio + validation + Arabic review
  -> 2C images/calendar
  -> [if approved] #23 approval center
  -> [if approved] #24/#25 landing/leads/UI subset
  -> QA/human review -> G6 production readiness
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

Phase 3 #26 outbox/reconciliation (no external side effects in Phase 2); full responsive UI #12 unless partially re-baselined; staging/production deployment #13; advanced CRM; billing; Android; paid ads; social publishing.

## 6. Roadmap conflicts to resolve before implementation

1. PRD brief requires approval center and landing pages in Phase 2; current issues place #23/#24/#25 in Phase 3. Do not silently move them.
2. “Automation” additions (assistant, validation) have no existing issues; create backlog items after owner approval, not in this task.
3. Subscription-based usage limits (#21) require plan/billing decision, but billing is a non-goal. Proposed interpretation: fixed per-tenant quotas configured by system admin, no billing UI.
