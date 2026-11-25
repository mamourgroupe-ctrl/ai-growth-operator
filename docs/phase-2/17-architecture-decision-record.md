# Phase 2 — Architecture Decision Records (proposed)

**Status:** All Phase 2 ADRs below are **PROPOSED/OPEN** unless marked as preserving a previously approved decision. None may be treated as approved until the owner records acceptance.

Phase 0 ADR-001..ADR-019 remain in `docs/phase-0/10-architecture-decision-log.md` and are preserved. Numbering starts at ADR-020 to avoid collisions.

## Decision status (all ADRs in this file)

| Category | Summary |
|---|---|
| Approved decisions | Only references to Phase 0/1 ADRs listed above. |
| Proposed decisions | ADR-020 through ADR-027 as described below. |
| Open questions | Provider, storage, pilot, roadmap re-baseline, quotas, FX, legal. |
| External dependencies | Owner approval, benchmark results, legal counsel, provider terms. |
| Risks | Recorded per ADR. |

---

## ADR-020 — Phase 2 scope packages and re-baseline of #23/#24/#25

- Status: **OPEN — requires owner decision**.
- Context: Phase 2 brief includes approval center and conversion foundation; existing repo roadmap places #23, #24, #25 in Phase 3.
- Decision proposed: split Phase 2 into 2A/2B/2C/2D; pull #23 and minimal #24/#25 into Phase 2 **only with explicit owner approval**; otherwise leave as API contracts/drafts.
- Alternatives: keep strict Phase 3 boundary (no usable approval/landing surface in Phase 2); move everything (scope creep risk).
- Consequences: roadmap/gates must be updated before implementation; no silent change to issue phases.
- External dependencies: owner decision.
- Risks: mismatch between product expectations and delivered scope; UI work underestimated.

## ADR-021 — Pilot sector selection framework

- Status: **PROPOSED — owner approval pending**.
- Context: pilot sector must be chosen by transparent framework, not arbitrary.
- Decision proposed: evaluate bakeries/patisseries, hair/beauty salons, local cafés/restaurants on 8 weighted criteria; recommend bakeries/patisseries first pending owner approval.
- Alternatives: salon pilot (repeat content but appointment expectations); café/restaurant pilot (menu/licensing volatility).
- Consequences: no sector-specific features or claim rules until approval; validation rules remain generic.
- External dependencies: pilot partner availability; legal review of food/health claims.
- Risks: mislabeling “best”/“healthy”; pilot partner churn.

## ADR-022 — Provider selection is deferred until reproducible benchmark

- Status: **PROPOSED policy — no provider selected**.
- Context: official price pages collected 2026-11-25; no performance/quality benchmark run.
- Decision proposed: benchmark frozen synthetic fixture across Gemini/OpenAI/Anthropic text and BFL/Gemini/OpenAI image candidates with identical prompts; record cost/latency/quality; owner selects after review. Price alone never decides.
- Alternatives: select cheapest now (rejected: unsupported quality/legal assumptions).
- Consequences: gateway must support multiple adapters behind one interface; model registry config-driven; fake adapters in CI.
- External dependencies: benchmark execution; legal/provider terms; human Arabic reviewer.
- Risks: deprecations (`Gemini 2.5 Flash`, `Gemini 2.5 Flash Image`); price changes; Darija quality unproven.

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
- Decision proposed: no tools, no publish/spend/approve capabilities in gateway; deterministic validation before review; owner-only final decision; AI output stored as draft with provenance.
- Alternatives: allow AI to approve/publish on validation success (rejected: violates approved policy).
- Consequences: adversarial tests mandatory; validation cannot clear blocks.
- External dependencies: human reviewers; validation rule owner.
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
- Decision proposed: immutable content versions and approval snapshots; new version supersedes prior approval; owner-only decision; idempotent decide endpoint.
- Alternatives: mutate approved draft and keep approval (rejected: no evidence integrity).
- Consequences: UI diff; append-only DB constraints; audit event `approval.superseded`.
- External dependencies: owner re-baseline if #23 pulled forward.
- Risks: UX confusion; non-material edit definition disputes.

## ADR-027 — FX source remains unresolved

- Status: **OPEN — carried from Phase 0 ADR-015**.
- Context: dual display requires trusted rate; no approved source/rounding exists.
- Decision proposed: implement only immutable snapshot table/contract; do not display converted amounts until owner selects source, timestamp, rounding, and spread policy.
- Alternatives: use an arbitrary free API now (rejected); display USD without conversion (out of MVP scope).
- Consequences: `fx_rate_snapshots` schema can be prepared; no live provider call.
- External dependencies: owner/FX source decision; financial review.
- Risks: misleading prices; stale rates.
