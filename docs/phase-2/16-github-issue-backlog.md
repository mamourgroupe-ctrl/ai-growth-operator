# Phase 2 — GitHub Issue Backlog with Dependencies and Acceptance Criteria

**Status:** Proposed. **No GitHub issues were created, edited, closed, or relabeled in this task.**

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Existing issues #8–#32 are preserved; no issue closed without human verification; #14 remains open/NOT VERIFIED. |
| Proposed decisions | Dependency ordering and acceptance criteria below; new issues P2-N1..N4 for gaps. |
| Open questions | Owner approval of re-baseline; quota numbers; provider/storage; FX source. |
| External dependencies | Legal review; benchmark; human reviewers. |
| Risks | Duplicate work if existing issues are edited without review; hidden dependencies between #21 and billing non-goal. |

## 1. Existing Phase 2 issues (dependency order and proposed acceptance criteria)

| Issue | Title | Depends on | Proposed acceptance criteria |
|---|---|---|---|
| #16 | Business profile and brand assets | Phase 1 RBAC/RLS (#3/#5) | Tenant-scoped CRUD; brand asset registry; RLS matrix; synthetic fixtures; no provider call |
| #17 | Product catalog | #16 | Price/currency/offer/availability; soft delete; composite tenant FK; RLS/role tests |
| #20 | Harden Postgres job queue | Phase 1 job table | `SKIP LOCKED`, leases, bounded backoff, dead-letter, idempotency, monitoring; `uncertain` state |
| #9 | Provider-independent AI gateway | #20, benchmark decision | Text/image protocols; fake adapters; config-driven registry; timeout/retry/rate limit; no client provider selection |
| #18 | AI model config, usage, cost tracking | #9 | Dated price snapshots, usage record, owner cost view; no secrets/raw prompt in logs |
| #21 | Usage limits from subscriptions | #18, owner quota decision | Fixed tenant quotas/caps configured by admin; no billing UI; atomic reservation/finalization |
| #22 | Immutable FX snapshots and dual display | #18, FX source decision | Append-only snapshot; source/date/rounding recorded; no live rate call; no display until source approved |
| #8 | Content studio APIs | #16/#17, #9, validation (N2) | Versioned drafts; locale/style enums; validation gate; owner/editor/viewer matrix |
| #27 | Human Arabic quality review | #8, native reviewer allocated | Reviewer flag; `ar`/`ar-DZ` gate; notes/status; cannot approve |
| N2 | Automated content validation | #16/#17, #8 design | Rule catalog from spec; price/injection/asset tests; immutable evidence; no approval authority |
| #19 | Creative assets and content calendar | #9, #17, #8 | Generated image metadata; signed URLs; scan gate; internal calendar only |
| #23 (Phase 3 → proposed move) | Approval center | #8, #27, N2, owner re-baseline | Owner-only decide; snapshot hash; supersession; negative tests; no publishing |
| #24 (Phase 3 → proposed move) | Landing pages and leads | #23 (if moved), owner re-baseline | Internal publish requires approved version; lead PII minimized/redacted; no CRM |
| #25 (Phase 3 → proposed partial move) | Arabic RTL/Darija/dual-currency UI | #8/#24 scope decision | RTL QA; style selectors; dual currency only with FX approval; no publish affordance |

## 2. Proposed new issues (not created)

| ID | Proposed title | Depends on | Acceptance criteria |
|---|---|---|---|
| P2-N1 | Implement manual + conversational onboarding | #16, privacy gate | Structured proposals with confidence/missing fields; no fact write without confirmation; session retention policy |
| P2-N2 | Implement automated content validation | #16/#17, #8 | Rules in `11-automated-content-validation-spec.md`; 100% price/injection/asset-negative tests; evidence immutable |
| P2-N3 | Provider benchmark harness and ADR inputs | #9, legal gate for synthetic use only | Identical fixture/prompts from docs 07/08; recorded cost/latency/quality; no winner claim without run |
| P2-N4 | Asset upload/signed URL and scan integration | #16, storage ADR | Server-generated keys; private bucket; MIME/magic checks; scan status gate; ownership check |

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
                ├─ #22
                └─ P2-N3 ─ (provider ADR) ─ #9 config
* = requires owner re-baseline from Phase 3 to Phase 2
```

## 5. Governance notes

- Do not create issues in this planning task; owner approval comes first.
- Each implementation PR must reference its issue, include tests, and update the Phase 2 status doc.
- No issue may authorize external publishing, paid ads, billing, or AI self-approval.
- Re-baseline of #23/#24/#25 must be recorded in ADR before implementation begins.
