# Phase 2 — GitHub Issue Backlog with Dependencies and Acceptance Criteria

**Status:** Proposed. **No GitHub issues were created, edited, closed, or relabeled in this task.**

## Decision status

| Category | Summary |
|---|---|
| `OWNER_APPROVED` baseline | Existing issues #8–#32 are preserved; no issue closed without human verification; #14 remains open/NOT VERIFIED. Owner-confirmed Phase 2 content governance is recorded in `01-product-requirements-document.md`. |
| `OWNER_PROPOSED` decisions | D-01–D-05, D-07, D-08 per `20-owner-decision-register.md`. Preliminary choices do not authorize issue edits, implementation or final scope. Dependency ordering, #23 split and #24/#25 re-baseline remain documented-only proposals. **No GitHub issue was created, edited, relabeled, closed, or re-milestoned.** |
| `BLOCKED` / `DEFERRED` | Final owner confirmation; quota numbers; benchmark/storage/legal evidence; pilot-sector selection. Lead functionality and publishing execution `DEFERRED`. |
| External dependencies | Legal review; benchmark (not run); human reviewers; owner verification of branch protection. |
| Risks | Duplicate work if existing issues are edited without review; hidden dependencies between #21 and billing non-goal. |
| Observation date | 2026-11-24/25: #23, #24, #25 are OPEN with label `enhancement`, no milestone; their titles still say `[Phase 3]`. Proposed wording changes are recorded below only. |

## 1. Existing Phase 2 issues (dependency order and proposed acceptance criteria)

| Issue | Title | Depends on | Proposed acceptance criteria |
|---|---|---|---|
| #16 | Business profile and brand assets | Phase 1 RBAC/RLS (#3/#5) | Tenant-scoped CRUD; brand asset registry; RLS matrix; synthetic fixtures; no provider call |
| #17 | Product catalog | #16 | Price/currency/offer/availability; soft delete; composite tenant FK; RLS/role tests |
| #20 | Harden Postgres job queue | Phase 1 job table | `SKIP LOCKED`, leases, bounded backoff, dead-letter, idempotency, monitoring; `uncertain` state |
| #9 | Provider-independent AI gateway | #20, benchmark decision | Text/image protocols; fake adapters; config-driven registry; timeout/retry/rate limit; no client provider selection |
| #18 | AI model config, usage, cost tracking | #9 | Dated price snapshots, usage record, owner cost view; no secrets/raw prompt in logs |
| #21 | Usage limits from subscriptions | #18, owner quota decision | Fixed tenant quotas/caps configured by admin; no billing UI; atomic reservation/finalization |
| #22 | Immutable **advertising** FX snapshots | Phase 3 only | Advertising FX snapshots, ad-spend ceilings and reconciliation remain Phase 3; no FX source/rate invented; D-03 sets DZD-only user display with USD internal cost evidence |
| #8 | Content studio APIs | #16/#17, #9, validation (N2) | Versioned drafts; canonical body in `content_versions`; locale/style enums; validation gate; owner/editor/viewer matrix |
| #27 | Human Arabic quality review | #8, native reviewer allocated | `tenant_memberships.is_arabic_reviewer`; `ar`/`ar-DZ` gate; notes/status; cannot approve |
| N2 | Automated content validation | #16/#17, #8 design | Rule catalog from `11-automated-content-validation-spec.md`; price/injection/asset tests; immutable evidence; no approval authority |
| #19 | Creative assets and content calendar | #9, #17, #8 | Generated image metadata; signed URLs; scan gate; internal content calendar only |
| #23 (Phase 3 → **proposed split only**) | Content approval center | #8, #27, N2 | Phase 2 content slice: owner-only-decision baseline, snapshots, history, invalidation, negative tests, no publishing. Phase 3 slice: ad-spend approval, FX ceiling, external actions, outbox/reconciliation, campaign launch |
| #24 (Phase 3 → **proposed partial move; D-02 `OWNER_PROPOSED`**) | Internal landing pages only | Content approval core | Internal create/edit/preview and draft/version history; lead table, lead ingestion, lead APIs/UI and publish execution `DEFERRED` to Phase 3 or later |
| #25 (Phase 3 → **proposed partial move**) | Arabic RTL/Darija UI | #8/#24 scope decision | RTL QA; Darija style selectors; visible Arabic review evidence; DZD-only user display; no publish affordance |

## 2. Proposed new issues (not created)

| ID | Proposed title | Depends on | Acceptance criteria |
|---|---|---|---|
| P2-N1 | Implement manual + conversational onboarding | #16, privacy gate | Structured proposals with confidence/missing fields; no fact write without confirmation; session retention policy |
| P2-N2 | Implement automated content validation | #16/#17, #8 | Rules in `11-automated-content-validation-spec.md`; 100% price/injection/asset-negative tests; evidence immutable |
| P2-N3 | Provider benchmark harness and ADR inputs | #9, legal gate for synthetic use only | Identical fixture/prompts from docs 07/08; recorded cost/latency/quality; no winner claim without run |
| P2-N4 | Asset upload/signed URL and scan integration | #16, storage ADR | Server-generated keys; private bucket; MIME/magic checks; scan status gate; ownership check |

### 2.1 Proposed wording changes for existing issues (documentation record only)

The following are **proposals for owner consideration**, not edits made to GitHub:

- **#23** — proposed retitle: `[Phase 2] Implement content approval center and fail-closed content gate`; proposed body: content versions, automated validation, Arabic review, immutable approval snapshots, approval history, invalidation on change, D-01 `OWNER_PROPOSED` owner-only final approval; no ad-spend, FX, external action, outbox/reconciliation, publishing or campaign launch. A separate Phase 3 issue should retain those advertising items.
- **#24** — proposed retitle: `[Phase 2] Implement internal landing page create/edit/preview`; proposed body: internal draft/version preview only; no lead table, lead route, lead UI, role-based lead redaction, publish endpoint, external publication or CRM. All lead functionality and publishing are `DEFERRED` to Phase 3 or later.
- **#25** — proposed retitle: `[Phase 2] Implement Arabic RTL and Darija styling for internal content`; proposed body: `ar` RTL, `fr` secondary where approved, Darija style, visible Arabic review; **DZD-only user-facing display**, with USD AI cost evidence internal only.

## 3. Phase 1 remediation issues (do not close by assumption)

| Issue | State note |
|---|---|
| #28, #29, #30, #31, #32 | Implementation/remediation work was recorded in Phase 1 commits, but issues remain OPEN; owner/human must verify and close after acceptance. This Phase 2 task does not change them. |
| #14 | `main` branch protection NOT VERIFIED due 403; remains OPEN. Do not close until read access confirms required checks. |

## 4. Dependency graph (simplified)

```text
#16 ─┬─ #17 ─┬─ N4 ─ #19
    │       └─ N2 ─ #8 ─ #27 ─ #23* ─ #24* ─ #25*
    └─ P2-N1
#20 ─ #9 ─ #18 ─┬─ #21
                └─ P2-N3 ─ (provider ADR) ─ #9 config

Phase 3 only: #22 advertising FX, #23 advertising slices, #26 outbox/reconciliation
* = proposed documentation-only re-baseline/split; no GitHub issue state was changed
```

## 5. Governance notes

- Do not create issues in this planning task; owner approval comes first.
- Each future implementation PR must reference its issue, include tests, and update the Phase 2 status doc.
- No issue may authorize external publishing, paid ads, billing, FX execution, or AI self-approval.
- Re-baseline of #23/#24/#25 must be recorded in an ADR before implementation begins; ADR-020 in `17-architecture-decision-record.md` currently records the conflict, not an approval.
- Final owner confirmation is pending for seven `OWNER_PROPOSED` decisions; preliminary choices must not be treated as approvals. D-04 numeric values, D-05 sector selection, D-07 benchmark evidence and D-08 storage comparison remain `BLOCKED`.

## 6. Phase 2.5 remediation register (F-01–F-28, historical)

The statuses below preserve the earlier Phase 2.5 record. D-01–D-05, D-07 and D-08 now have preliminary owner choices in `20-owner-decision-register.md`; those choices reconcile the earlier “pending” findings but are not final approvals. Lead/publishing items previously described as proposed are `DEFERRED` to Phase 3 or later.

**Scope:** documentation-only remediation executed on branch `arena/5dc98770-ai-growth-operator`; initial HEAD `8da2f9aa161070ab2f4af7beca54b9bd41345e23`; observation date 2026-11-24/25. No code, migration, test, CI, GitHub issue, PR, label, milestone, branch, or provider API was changed.

**Status vocabulary**

- `RESOLVED_IN_DOCS` — concrete inconsistency corrected in documentation.
- `DOCUMENTED_OWNER_DECISION_PENDING` — conflict/boundary recorded; no decision silently made.
- `DOCUMENTED_EXTERNAL_DEPENDENCY` — legal/benchmark/provider evidence is outstanding; no factual claim promoted.
- `DOCUMENTED_BACKLOG_ONLY` — proposed issue/roadmap change recorded in docs; GitHub untouched.

| ID | Root cause | Action taken | Document / section | Priority | Acceptance criterion | Evidence | Status |
|---|---|---|---|---|---|---|---|
| F-01 | Owner-confirmed Phase 2 approval/validation scope contradicted `[Phase 3]` issues #23/#24/#25 and stale roadmap text | State confirmed boundary; record split/re-baseline as proposals only | `01 §1`, `02 §1/§7`, `15 §1/§6`, `16 §1/§2.1` | P0 | Phase 2 content governance present; advertising execution absent; no issue edited | Preflight `gh issue view 23/24/25`; doc diff | `DOCUMENTED_BACKLOG_ONLY` |
| F-02 | “Owner/editor authorization” conflicted with owner-only final approval | Preserve owner-only final decision; propose four-role matrix; mark unresolved | `01 §6`, `02 §1`, `05 §2`, `12 §1/§7` | P0 | No authority silently changed; editor submission distinguished from final approval | `12-approval-workflow-spec.md §1` | `DOCUMENTED_OWNER_DECISION_PENDING` |
| F-03 | Landing/leads Phase 2 boundary unspecified | Internal-only proposal; trusted resolver; no external side effect; owner decision retained | `01 §3`, `02 §7`, `05 §2`, `06 §1`, `14 §4`, `15 §2D` | P0 | No external publish/CRM/paid path; scope still marked unresolved | `05-api-contracts.md §2` | `DOCUMENTED_OWNER_DECISION_PENDING` |
| F-04 | Pilot sector examples (bakery/salon/café) did not match prior candidate frameworks | Treat all sector lists as hypotheses/research candidates; no sector selected | `01 §6`, `15 §1/§6` | P1 | All candidates recorded; no recommendation asserted | `01-product-requirements-document.md §6` | `DOCUMENTED_OWNER_DECISION_PENDING` |
| F-05 | Non-advertising dual-currency display treated as approved while advertising FX was Phase 3 | Separate SaaS cost evidence from advertising FX; leave display unresolved | `01 §6`, `03 §3`, `04 §3`, `10 §1`, `15 §1/§6` | P0 | No rate/source/rounding invented; advertising FX Phase 3 | `03-database-design.md §3` | `DOCUMENTED_OWNER_DECISION_PENDING` |
| F-06 | Numeric AI quota/cost limits absent | Treat as owner decision; require numeric caps before enforcement | `01 §6`, `05 §1`, `07 §5`, `15 §1/§2B`, `16 §6` | P1 | No invented quota; quota gate documented | `15-phase-2-roadmap.md §1` | `DOCUMENTED_OWNER_DECISION_PENDING` |
| F-07 | `content_items.body` duplicated canonical body in versions | Make `content_versions.body` canonical; `content_items` metadata/pointer only | `03 §1`, `04 §4`, `11 §1`, `16 §1` | P0 | Single canonical body; no dual-copy writes | `03-database-design.md §1` | `RESOLVED_IN_DOCS` |
| F-08 | Approval snapshot FK direction suggested circular insert dependency | Snapshot FK points to request; unique `(tenant_id, approval_request_id, version)` | `03 §3`, `04 §2`, `12 §4` | P0 | No circular FK; append-only history | `03-database-design.md §3` | `RESOLVED_IN_DOCS` |
| F-09 | Arabic reviewer flag not consistently located | Document existing `tenant_memberships.is_arabic_reviewer` from `0001_initial` as canonical field | `03 §1`, `05 §2`, `12 §1`, `16 §1` | P1 | Review capability distinct from final approval; no new column migration | `apps/api/migrations/versions/0001_initial.py`; `03-database-design.md §1` | `RESOLVED_IN_DOCS` |
| F-10 | Idempotency uniqueness not specified consistently for AI usage/jobs | Preserve existing job `uq_jobs_tenant_idempotency` and extend one-row-per-key rule to `ai_usage_records` | `03 §2`, `04 §4`, `05 §2` | P0 | Duplicate usage prevented; retry safe; no duplicate constraint recreated | `apps/api/migrations/versions/0001_initial.py`; `04-alembic-migration-plan.md §4` | `RESOLVED_IN_DOCS` |
| F-11 | AI price snapshots and advertising FX snapshots conflated | Separate USD AI operating-cost snapshots from Phase 3 advertising FX | `03 §3`, `04 §3`, `05 §2`, `15 §2B` | P0 | AI cost evidence never used as FX/ad budget | `03-database-design.md §3` | `RESOLVED_IN_DOCS` |
| F-12 | `FORCE ROW LEVEL SECURITY` semantics overstated | State that it applies policies to owner but grants no privileges | `03 §4`, `04 §3`, `10 §3.2` | P0 | `ago_app` non-superuser/NOBYPASSRLS and explicitly granted | `10-data-privacy-security-review.md §3.2` | `RESOLVED_IN_DOCS` |
| F-13 | RLS policy combination semantics missing | Document PERMISSIVE default/OR and RESTRICTIVE/AND | `03 §4`, `04 §3`, `10 §3.2` | P0 | Tenant isolation cannot be weakened by an additive policy | `10-data-privacy-security-review.md §3.2` | `RESOLVED_IN_DOCS` |
| F-14 | Tenant context treated as a general session variable | Specify server-derived transaction-local `set_config(..., true)` | `03 §4`, `04 §3`, `10 §3.2` | P0 | No client-supplied tenant context; no parameter-bound `SET` | `03-database-design.md §4` | `RESOLVED_IN_DOCS` |
| F-15 | Public lead insert lacked explicit tenant resolver | Require trusted slug→tenant resolver before insert | `03 §4`, `04 §3`, `05 §2` | P0 | Public route cannot select tenant from client | `03-database-design.md §4` | `RESOLVED_IN_DOCS` |
| F-16 | Approval API paths inconsistent (`/approval/...` vs `/api/v1/approval/...`) | Establish `/api/v1/approval/...` as canonical | `05 §2`, `11 §1`, `12 §4` | P1 | All specs reference one path set | `05-api-contracts.md §2` | `RESOLVED_IN_DOCS` |
| F-17 | Landing page version endpoint missing from API contract | Add proposed `POST /api/v1/landing/pages/{id}/versions` | `05 §2`, `16 §1` | P1 | Immutable page version supports approval | `05-api-contracts.md §2` | `RESOLVED_IN_DOCS` |
| F-18 | Validation override rules contradicted `block` immutability | Separate non-overridable `block` codes from owner-recorded `warn` overrides | `05 §3`, `11 §1/§5`, `12 §4` | P0 | No `block` override path; every override audited | `11-automated-content-validation-spec.md §1` | `RESOLVED_IN_DOCS` |
| F-19 | Embedded benchmark fixture was invalid JSON | Replace with syntactically valid versioned fixture | `07 §2.1`, `13 §3` | P1 | `json.loads` passes on documented fixture | Corrected JSON block in `07 §2.1` | `RESOLVED_IN_DOCS` |
| F-20 | `T5` referenced five products while fixture had two | Expand fixture to three products and align `T1`/`T3`/`T5` | `07 §2.1/§2.2`, `13 §3` | P1 | Product count consistent across fixture/tasks | `07-ai-gateway-text-provider-comparison.md §2` | `RESOLVED_IN_DOCS` |
| F-21 | Benchmark lacked model/revision pinning, cache accounting and error accounting | Add exact IDs, dated revisions, actual tokens/cache state, 429/5xx/retry metrics | `07 §2.0/§2.4/§2.5` | P1 | Reproducible harness spec; no winner claim | `07-ai-gateway-text-provider-comparison.md §2` | `DOCUMENTED_EXTERNAL_DEPENDENCY` |
| F-22 | Image generation and editing were scored as one capability | Split `G` generation and `E` editing task families and metrics | `08 §2`, `13 §3` | P1 | Separate evidence per capability; no cross-claim | `08-image-generation-provider-comparison.md §2` | `RESOLVED_IN_DOCS` |
| F-23 | ZDR/retention claim implied for `GPT-Image-2.6` | Record that official ZDR-compatible image list does not name 2.6; legal/contract gate | `08 §2.3/§4` | P0 | No verified-ZDR claim; provider not selected | `08-image-generation-provider-comparison.md §4` | `DOCUMENTED_EXTERNAL_DEPENDENCY` |
| F-24 | R2 free tier misapplied to 40 GB pilot | Correct billable storage to 30 GB and remove “free” claim | `09 §2` | P1 | 40 − 10 = 30 GB-month shown | `09-object-storage-comparison.md §2` | `RESOLVED_IN_DOCS` |
| F-25 | B2 egress arithmetic wrong (`$60` for 1.5 TB) | Correct allowance and formula; 1,500 GB is within 3× free allowance | `09 §2` | P1 | Formula `max(0, egress − 1,500) × $0.01` documented | `09-object-storage-comparison.md §2` | `RESOLVED_IN_DOCS` |
| F-26 | Storage decision ignored residency, encryption, backup and contract dimensions | Add non-price matrix; no default provider selected | `09 §5`, `15 §1` | P0 | Residency/legal blocking criterion explicit | `09-object-storage-comparison.md §5` | `DOCUMENTED_EXTERNAL_DEPENDENCY` |
| F-27 | Historical report mixed current-state claims with stale PR/commit/CI statements | Mark historical observations by date; distinguish CI from local tests; keep branch protection NOT VERIFIED | `18 §1/§4/§7`, `10 §3.1`, `13 §1.1` | P0 | No false local-test claim; CI run identified; PR #15 state dated | `18-final-engineering-report.md` | `RESOLVED_IN_DOCS` |
| F-28 | Issue proposals and verification limits lacked traceability | Record #23/#24/#25 proposals in backlog docs only; document 403 branch-protection limit and no benchmark/no local pytest | `16 §1/§2.1/§6`, `18 §7` | P1 | No GitHub issue/PR/label/milestone modified; limits explicit | `git status --short`; `gh issue view`/`gh pr view` read-only calls | `DOCUMENTED_BACKLOG_ONLY` |

### 6.1 Register summary

- `RESOLVED_IN_DOCS`: F-07, F-08, F-09, F-10, F-11, F-12, F-13, F-14, F-15, F-16, F-17, F-18, F-19, F-20, F-22, F-24, F-25, F-27 — 18 findings.
- `DOCUMENTED_OWNER_DECISION_PENDING`: F-02, F-03, F-04, F-05, F-06 — 5 findings.
- `DOCUMENTED_EXTERNAL_DEPENDENCY`: F-21, F-23, F-26 — 3 findings.
- `DOCUMENTED_BACKLOG_ONLY`: F-01, F-28 — 2 findings.
- No finding is marked “implemented”; documentation remediation only.
