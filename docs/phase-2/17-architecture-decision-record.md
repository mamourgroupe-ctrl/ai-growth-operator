# Phase 2 — Architecture Decision Records (proposed)

**Status:** All Phase 2 ADRs below are **PROPOSED/OPEN** unless marked as preserving a previously approved decision. None may be treated as approved until the owner records acceptance.

Phase 0 ADR-001..ADR-019 remain in `docs/phase-0/10-architecture-decision-log.md` and are preserved. Numbering starts at ADR-020 to avoid collisions.

## Decision status (all ADRs in this file)

| Category | Summary |
|---|---|
| `OWNER_APPROVED` baseline | Only references to Phase 0/1 ADRs plus the owner-confirmed Phase 2.5 boundary: automated content validation, human content review, content approval permissions, immutable approval snapshots/history, invalidation on change, content calendar/management, AI quota/cost tracking. |
| `OWNER_PROPOSED` decisions | D-01–D-05, D-07, D-08 are preliminary owner choices; ADR-020..ADR-026 remain proposed. No ADR approves a final provider, storage vendor, pilot sector, numeric quota or FX source. |
| `BLOCKED` / `DEFERRED` | Final owner confirmation; sector/provider/storage evidence; numeric quotas; legal review. Lead functionality and publishing are `DEFERRED`. |
| External dependencies | Owner decisions, corrected benchmark results (not run), legal counsel, provider terms, human Arabic reviewer. |
| Risks | Recorded per ADR. |
| Observation date | 2026-11-24/25: issues #23/#24/#25 remain OPEN/`[Phase 3]`; PR #15 remains OPEN/DRAFT/MERGEABLE at `8da2f9a`. |

---

## ADR-020 — Phase 2 scope packages and re-baseline of #23/#24/#25

- Status: **OPEN — requires owner decision on wording/boundary; confirmed content scope is not open**.
- Context: owner confirmation includes Phase 2 automated validation, human review, content approval, immutable snapshots/history and invalidation, content calendar and AI quota/cost tracking. Existing issues #23/#24/#25 still say `[Phase 3]` (observed 2026-11-24).
- Confirmed boundary: no ad budget approval, ad expenditure, paid ad execution, external ad-platform campaign execution, paid-action authorization, advertising FX snapshots, outbox/reconciliation, external execution state machine, or automatic campaign launching in Phase 2.
- Decision proposed: split #23 into Phase 2 content approval and Phase 3 advertising/external execution; propose internal-only #24/#25 subset pending exact scope decision; record proposed issue wording in `16-github-issue-backlog.md §2.1` only.
- Alternatives: keep strict Phase 3 boundary (contradicts owner-confirmed content scope); move everything (scope creep and Phase 3 violation).
- Consequences: roadmap/gates must be updated before implementation; no silent change to issue phases; no GitHub issue was edited by this task.
- External dependencies: owner decision on approval authority wording and landing/lead boundary.
- Risks: mismatch between product expectations and delivered scope; UI work underestimated.

## ADR-021 — Pilot sector selection framework

- Status: **PROPOSED — owner approval pending**.
- Context: prior frameworks list retail, tourism, professional services, manufacturing and restaurants/hospitality; earlier docs also used bakery/salon/café examples. All are research candidates/hypotheses; no final pilot sector is selected.
- Decision proposed: evaluate candidate sectors on transparent criteria (content cadence, owner availability, legal claim sensitivity, Arabic/Darija need, asset readiness, data consent, operational complexity, feedback quality). Sector-neutral foundations may proceed with synthetic fixtures.
- Alternatives: select a sector now (rejected: no owner decision/evaluation evidence); keep legacy bakery example (rejected: conflicts with owner-confirmed list).
- Consequences: no sector-specific features or claim rules until approval; validation rules remain generic; pilot metrics are targets, not measured results.
- External dependencies: pilot partner availability; legal review of food/health claims.
- Risks: mislabeling “best”/“healthy”; pilot partner churn.

## ADR-022 — Provider selection is deferred until reproducible benchmark

- Status: **PROPOSED policy — no provider selected**.
- Context: official price pages were collected 2026-11-25; **no reproducible benchmark has been run**. Earlier fixture JSON was invalid and the product count conflicted with `T5`; both are corrected in doc 07.
- Decision proposed: run the corrected text fixture and separated image generation/editing tasks with pinned model identifiers/revisions, identical wrapper/prompt/schema/fixture, recorded token/cache/error/latency data, and dated price snapshots. Owner selects after evidence review. Price alone never decides.
- Alternatives: select cheapest now (rejected: unsupported quality/legal assumptions); assume equal tokenization across providers (rejected).
- Consequences: gateway must support multiple adapters behind one interface; model registry config-driven; fake adapters in CI. No selection is recorded here.
- External dependencies: benchmark execution; legal/provider terms; human Arabic reviewer; structured-output support verification.
- Risks: deprecations (`Gemini 2.5 Flash`, `Gemini 2.5 Flash Image`); price changes; Darija quality unproven; unsupported retention claim for `GPT-Image-2.6`.

## ADR-023 — S3-compatible object abstraction, provider deferred

- Status: **PROPOSED policy — no storage provider selected**.
- Context: R2, B2, S3 official pricing fetched 2026-11-25; residency/legal unknown.
- Decision proposed: keep `ObjectStorage` protocol with private buckets, short signed URLs, server-generated keys, scan status gate; owner chooses provider after workload/residency review.
- Alternatives: direct vendor SDK in tenant services (rejected: lock-in); public asset URLs (rejected: privacy).
- Consequences: metadata stores provider-neutral `storage_ref`; migration between providers is config/ops work.
- External dependencies: provider DPA/residency; malware scanner choice.
- Risks: egress cost; accidental public objects; unscanned assets.

## ADR-024 — AI output is untrusted and cannot authorize any action

- Status: **PROPOSED confirmation of existing non-negotiable**.
- Context: generated text/images may contain instructions or unsafe claims.
- Decision proposed: no tools, no publish/spend/approve capabilities in gateway; deterministic validation before review; owner-only final decision baseline unchanged; AI output stored as draft with provenance. `warn` overrides are owner-recorded; `block` codes are non-overridable.
- Alternatives: allow AI or editors to grant final approval on validation success (rejected: violates existing policy and unresolved authority must not be silently changed).
- Consequences: adversarial tests mandatory; validation cannot clear blocks; no advertising action capability.
- External dependencies: human reviewers; validation rule owner; final owner confirmation of D-01.
- Risks: prompt injection; over-trust in automation.

## ADR-025 — Conversational onboarding writes only confirmed facts

- Status: **PROPOSED**.
- Context: assistant can infer structured fields but may hallucinate.
- Decision proposed: show proposed fields with confidence/source; user accepts/edits/rejects; only confirmed fields persisted; session proposals expire (proposed 30 days).
- Alternatives: auto-write inferred facts (rejected); no assistant (rejected by Phase 2 brief).
- Consequences: new `onboarding_sessions` table; audit confirmation events; no PII in prompts before legal gate.
- External dependencies: privacy review; prompt template approval.
- Risks: false confidence; stale session data; PII leakage.

## ADR-026 — Versioned approvals and supersession

- Status: **PROPOSED extension of ADR-014/018**.
- Context: material edits after approval can make approval stale.
- Decision proposed: immutable `content_versions.body` and approval snapshots with FK to `approval_requests`; new version supersedes prior approval; owner-only-decision baseline; idempotent `/api/v1/approval/requests/{id}/decide`; approval history/audit retained.
- Alternatives: mutate approved draft and keep approval (rejected: no evidence integrity); duplicate body in `content_items` (rejected).
- Consequences: UI diff; append-only DB constraints; audit event `approval.superseded`; no Phase 2 ad-spend/execution state.
- External dependencies: final owner confirmation and issue split if #23 is re-baselined.
- Risks: UX confusion; non-material edit definition disputes.

## ADR-027 — DZD-only user display; advertising FX remains Phase 3 (`OWNER_PROPOSED`)

- Status: **OWNER_PROPOSED**; final confirmation pending.
- Context: D-03 preliminarily requires DZD-only user-facing amounts and internally recorded USD AI provider cost evidence. Advertising FX snapshots and financial authorization remain Phase 3. No source, timestamp, rounding, spread or rate exists for user display.
- Decision: no Phase 2 conversion display or FX source; no original foreign-currency user display. AI operating-cost snapshots are USD pricing evidence only and must never be used as FX or ad-budget evidence. Advertising FX snapshots and reconciliation are `DEFERRED` to Phase 3.
- Alternatives: arbitrary FX API (rejected); AI price snapshots as FX (rejected); USD user display (rejected pending separate owner decision).
- Consequences: no Phase 2 `fx_rate_snapshots` seed or live call; no invented rate; no claim that a preliminary choice is final approval.
- External dependencies: final owner confirmation; for Phase 3, financial/FX source review.
- Risks: misleading prices; stale rates; conflation of SaaS cost with ad spend.
