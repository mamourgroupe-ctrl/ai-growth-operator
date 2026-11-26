# Phase 2 — Final Engineering Planning Report

**Outcome:** Phase 2 documentation prepared, then Phase 2.5 documentation remediation applied. **Phase 2 implementation has NOT started.**
**Status:** Phase 2.6 owner-decision documentation reconciliation applied in the workspace; final owner confirmation remains pending. No provider/storage/sector selection made; no code, migration, endpoint, issue, deployment, or spend action performed.

> **Historical-state notice:** This report was originally written as the Phase 2 planning final report at commit `8da2f9aa161070ab2f4af7beca54b9bd41345e23`. Statements below about “this task” refer to that original planning task unless explicitly labeled **Phase 2.5 remediation** (observation dates 2026-11-24/25). The remediation was performed on the same Arena branch without commit or push; the current working tree therefore differs from the historical commit. Historical facts are retained with their original context rather than silently rewritten.

## Decision status

| Category | Summary |
|---|---|
| `OWNER_APPROVED` baseline | Preserved Phase 0/1 decisions plus owner-confirmed Phase 2 scope: automated content validation, human content review, content approval permissions, immutable/versioned approval snapshots, approval history/audit, invalidation on content change, content calendar/management, AI usage quota/cost tracking. Existing owner-only final approval remains unchanged. |
| `OWNER_PROPOSED` decisions | D-01, D-02, D-03, D-04, D-05, D-07 and D-08 are preliminary owner choices recorded in `20-owner-decision-register.md`; none is finally approved. Phase 2 architecture/schema/API/QA/deployment/roadmap/backlog/ADR items remain proposals or `FROZEN` technical baselines. |
| `BLOCKED` / `DEFERRED` | Final confirmation; D-04 numeric values; D-05 sector selection; D-07 benchmark evidence; D-08 storage/legal evidence; D-10/French UI scope. Lead functionality and publishing are `DEFERRED`. |
| External dependencies | Corrected benchmark execution (not run), Algerian legal review, provider terms/DPAs, human Arabic/Darija reviewers, owner sign-off, #14 verification. |
| Risks | Scope conflict; unproven Darija quality; provider cost/deprecation; unauthorized data transfer; approval bypass; branch protection unverified. |
| Confirmed Phase 3 boundary | Ad budget approval, ad expenditure, paid ad execution, external ad-platform campaign execution, paid-action authorization, advertising FX snapshots, paid outbox/reconciliation, external execution state machines, and automatic campaign launching. |

## 1. Branch and repository state (reviewed)

- Branch: `arena/5dc98770-ai-growth-operator` (current branch; based on `main` commit `7820f29893815562613dd9c72ea4b0e51b956df3`).
- HEAD before the original Phase 2 planning work: `aaf37f1f0304f0a47c11c2566f6204dc594a96c9` (historical fact).
- HEAD after Phase 2 planning commits and before Phase 2.5 remediation: `8da2f9aa161070ab2f4af7beca54b9bd41345e23` (verified 2026-11-24/25).
- `main` / `origin/main`: `7820f29893815562613dd9c72ea4b0e51b956df3` — unchanged.
- Draft PR #15 (observed 2026-11-24/25): OPEN, DRAFT, unmerged, head `8da2f9a...`, base `main`, `MERGEABLE` — not modified.
- Issue #14: OPEN; `main` branch protection **NOT VERIFIED** (GitHub API returned 403 on read attempt).
- Working tree before Phase 2.5 remediation: clean.
- Working tree during/after Phase 2.5 remediation: modified documentation under `docs/phase-2/` only; no commit or push.

## 2. Files reviewed (read-only)

- Phase 0 baseline: `docs/phase-0/01-prd-review.md`, `02-technical-architecture.md`, `03-database-design.md`, `04-api-specification.md`, `05-security-architecture.md`, `06-development-roadmap.md`, `07-testing-strategy.md`, `08-deployment-strategy.md`, `10-architecture-decision-log.md`, `11-architecture-audit.md`, `12-final-acceptance-report.md`.
- Phase 1 evidence: `docs/phase-1/engineering-report.md`, `independent-acceptance-audit.md`, `remediation-report.md`, `branch-protection.md`, `secret-scanner.md`.
- Implementation baseline: `README.md`, `apps/api/app/*`, `apps/api/migrations/*`, `apps/web/*`, `tests/*`, `.github/workflows/ci.yml`.
- GitHub backlog/PR: issues #1–#32 and PR #15 metadata (via `gh`), no changes made.

## 3. Files created in this task

All new files are documentation under `docs/phase-2/`:

| # | File | Deliverable |
|---|---|---|
| 1 | `01-product-requirements-document.md` | Phase 2 PRD + pilot sector framework |
| 2 | `02-detailed-technical-architecture.md` | Detailed architecture |
| 3 | `03-database-design.md` | Updated DB design / ERD |
| 4 | `04-alembic-migration-plan.md` | Proposed Alembic migration plan |
| 5 | `05-api-contracts.md` | API contracts / OpenAPI changes |
| 6 | `06-frontend-information-architecture.md` | Frontend IA / screen specs |
| 7 | `07-ai-gateway-text-provider-comparison.md` | AI gateway + text provider comparison |
| 8 | `08-image-generation-provider-comparison.md` | Image generation provider comparison |
| 9 | `09-object-storage-comparison.md` | Object storage comparison |
| 10 | `10-data-privacy-security-review.md` | Privacy/security review |
| 11 | `11-automated-content-validation-spec.md` | Automated content validation spec |
| 12 | `12-approval-workflow-spec.md` | Approval workflow spec |
| 13 | `13-testing-qa-strategy.md` | Testing/QA strategy |
| 14 | `14-deployment-environment-strategy.md` | Deployment/environment strategy |
| 15 | `15-phase-2-roadmap.md` | Phase 2 roadmap |
| 16 | `16-github-issue-backlog.md` | Issue backlog with dependencies/acceptance |
| 17 | `17-architecture-decision-record.md` | Proposed ADR-020..027 |
| 18 | `18-final-engineering-report.md` | This report |

**Original planning task:** modified files were none; prior Phase 0/Phase 1 reports were preserved unchanged; deleted files none.

**Phase 2.5 remediation:** all 18 files under `docs/phase-2/` were reviewed and the files with verified inconsistencies were edited in place. The complete itemized list, per-file summary, and F-01–F-28 register are in the final in-chat remediation report and in `16-github-issue-backlog.md §6`. No file outside `docs/phase-2/` was changed.

## 4. Comparison sources (official, dated 2026-11-25)

| Source | Used for |
|---|---|
| [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) | Text model names/prices; Gemini 3 Pro Image and Gemini 2.5 Flash Image prices; deprecations |
| [OpenAI API pricing](https://openai.com/api/pricing/) | GPT-6.x text and GPT-Image-2.6 prices; tool/batch/residency notes |
| [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) | Claude Fable/Opus/Sonnet/Haiku prices and cache rates |
| [BFL pricing](https://docs.bfl.ai/quick_start/pricing) | FLUX 3, FLUX.2, FLUX.1 product prices |
| [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing/) | R2 Standard/IA storage, operations, egress, free tier |
| [Backblaze B2 pricing](https://www.backblaze.com/cloud-storage/pricing) | B2 storage, free egress allowance, API call pricing |
| [AWS S3 pricing](https://aws.amazon.com/s3/pricing/) | S3 Standard/IA/Glacier storage and request prices (us-east-1) |
| [Algeria Law 25-11 (JORADP)](https://www.joradp.dz/FTP/JO-FRANCAIS/2025/F2025048.pdf) + [NATLEX](https://natlex.ilo.org/dyn/natlex2/r/natlex/fe/details?p3_isn=118858) | DPO, processing registers, automated logs, scope amendments; secondary summaries used only as context |

Exact prices and model names are in docs 07–09. Third-party search snippets were discarded where official pages were available.

### Benchmark status

- Corrected reproducible benchmark **plans** are documented in docs 07 and 08: valid versioned fixture, consistent product count, pinned model identifiers/revisions, separated image generation/editing tasks, and recorded token/cache/error/latency accounting.
- **No benchmark has been executed** (no sandbox calls, no spend, no API keys). No provider has been declared faster, cheaper in practice, more Arabic-capable, or higher quality from an unrun test.
- Cost tables are corrected illustrative calculations from list prices only; they are not invoices or performance evidence. The R2 40 GB pilot is not wholly within the 10 GB-month free tier, and 1,500 GB B2 egress is within the 3× free allowance; no `$60` figure is asserted.
- Regional availability includes Algeria in official provider lists, but transfer legality is a separate unresolved legal gate.

## 5. Recommended architecture (proposed, not approved)

- Single FastAPI modular monolith + separate worker process sharing package and PostgreSQL; Next.js responsive Arabic-first UI.
- Tenant-owned tables use shared schema with FORCE RLS, `USING`/`WITH CHECK`, composite tenant FKs, and `ago_app` non-superuser runtime role.
- AI gateway with `TextProvider`/`ImageProvider` protocols, config-driven model registry with dated price snapshots, policy engine, fake adapters in CI, quotas and idempotent usage records; client cannot select provider/model.
- Untrusted generated output → deterministic validation (non-overridable `block` findings; owner-recorded `warn` overrides) → Arabic human review for `ar`/`ar-DZ` → owner-only-decision baseline with immutable `content_versions.body` snapshots and approval history. No tools, publishing, spend, or self-approval.
- Canonical AI idempotency is `(tenant_id, idempotency_key)`; AI price snapshots are USD operating-cost evidence, never advertising FX or ad budgets.
- Private S3-compatible asset storage with server-generated keys, short signed URLs, MIME/checksum/scan gates; provider deferred pending non-price residency/legal review.
- Content approval core is owner-confirmed Phase 2. #23 is proposed to split, with ad-spend/FX/external execution remaining Phase 3. D-02 preliminarily limits landing pages to internal create/edit/preview and defers all lead functionality and publishing to Phase 3 or later; #25 UI subset remains a proposal.
- Deployment: local/CI/staging/production with synthetic data below production, feature flags default-off, secrets in environment stores, migration as controlled step.

## 6. Unresolved decisions requiring owner input

1. Obtain final owner confirmation for D-01, D-02, D-03, D-04, D-05, D-07 and D-08. Preliminary choices are not approvals.
2. D-02 issue amendments remain documented only; no GitHub issue was edited; see `16-github-issue-backlog.md §2.1`.
3. D-05: no pilot sector is selected; sector examples are hypotheses/candidates; sector-neutral work may use synthetic fixtures.
4. D-07: select text/image providers only after a documented benchmark covering quality, MSA, Darija, French, cost, latency, reliability, privacy and retention.
5. D-08: select storage only after a documented comparison covering residency, security, encryption, backup/recovery, DPAs, retention, egress and total cost.
6. Legal/privacy: DPO, processing register, automated logs, cross-border transfer authorization, allowed data categories and retention remain `BLOCKED`.
7. D-04: system administrator proposes numeric quota/cost values and owner approves; no numerical enforcement before approval.
8. D-03: DZD-only user-facing, USD AI cost internally; no conversion or FX source. Advertising FX source/rounding for #22 remains Phase 3.
9. French UI scope remains `BLOCKED`; viewer lead-PII redaction is `DEFERRED` with Phase 3 leads.
10. Verify `main` branch protection (#14) before production release; current status NOT VERIFIED.

## 7. Risks and mitigations (summary)

| Risk | Mitigation |
|---|---|
| Scope conflict with Phase 3 issues | Explicit gate G0; no silent re-baseline |
| Provider cost/deprecation | Price snapshots, quotas, benchmark before selection, avoid deprecated models |
| Unauthorized personal-data transfer | Blocking legal gate; synthetic-only until cleared |
| Prompt injection / untrusted AI output | No tools, schema validation, adversarial tests, human approval |
| Approval bypass / stale approval | Owner-only endpoint, version supersession, negative tests |
| Cross-tenant leakage | FORCE RLS + composite FKs + catalog/API tests with `ago_app` |
| Unscanned/exposed assets | Private buckets, signed URLs, scan gate, ownership check |
| Darija quality unproven | Blind native reviewer in benchmark; no locale enablement before pass |
| Branch protection unverified | #14 remains open; production release gated on owner verification |

## 8. Backlog and dependencies

Retained issues in proposed dependency order: foundation (#16/#17) → queue (#20) → gateway/usage (#9/#18/#21; numeric limits pending) → content/validation (#8 + proposed N2) → Arabic review (#27) → creative/calendar (#19) → Phase 2 content approval slice of #23 → proposed internal-only #24/#25 subset. Issue #22 advertising FX is Phase 3; #23 advertising/external execution and #26 outbox/reconciliation are Phase 3. Proposed new issues: P2-N1 onboarding assistant, P2-N2 validation, P2-N3 benchmark harness, P2-N4 asset upload/scan. No issues were created or edited. Full criteria in `16-github-issue-backlog.md`.

## 9. Testing and acceptance strategy

CI lint/test/security gate preserved; unit, API/contract, DB/RLS catalog, migration cycle, fake-provider integration, worker/queue, adversarial validation, approval-negative and optional E2E/a11y suites proposed. Human gates: Arabic reviewer for `ar`/`ar-DZ`; owner review of benchmark/provider/storage/pilot; legal gate before real data. No benchmark result or test is claimed to have been run in this planning task. Detailed criteria in `13-testing-qa-strategy.md`.

## 10. Internal architecture review

**Historical review performed before the original report (at `aaf37f1`):**

- Verified all 18 deliverables existed and each required decision-status section was present.
- Verified no provider/storage/sector was selected; no benchmark was claimed as executed.
- Verified non-negotiables were preserved: RLS+RBAC, owner-only approval, no direct publishing/spend, S3 abstraction, no production data in lower environments.
- Verified roadmap conflict #23/#24/#25 was explicitly gated rather than silently moved.
- Verified no prior Phase 0/1 report was modified.
- Verified repository state at that time: only untracked `docs/phase-2/`; no code/migration/API/infra changes.

**Phase 2.5 remediation review (2026-11-24/25):**

- Verified preflight identity, exact branch, clean tree, base/head SHAs, current issue states and PR #15 state before editing.
- Verified and corrected concrete inconsistencies in scope, DB/API, security wording, benchmark fixtures, image evaluation split, storage arithmetic/matrix, historical reporting and issue traceability.
- Verified no provider/storage/sector selection was introduced and no benchmark was run.
- Verified unresolved owner decisions remain unresolved and are explicitly labeled.
- Verified no code, migration, test, CI, GitHub issue, PR, label, milestone, branch, or deployment changes were made.
- Performed read-only validation only; no local pytest run and no implementation-readiness claim.

## 11. Commit and confirmations

- Historical commit SHA for Phase 2 planning deliverables 01–17: `b51eee6ce964491340c3c5082b097dd62a0ff556` (documentation-only).
- Historical final planning commit: `8da2f9aa161070ab2f4af7beca54b9bd41345e23`.
- **Phase 2.5 remediation is intentionally not committed:** HEAD remains `8da2f9aa161070ab2f4af7beca54b9bd41345e23`; changes are uncommitted in the working tree for owner review.
- Confirmations:
  - No application code, migrations, endpoints, frontend screens, provider integrations, dependency changes or infrastructure changed.
  - No production credentials used; no external provider calls or benchmark spending performed.
  - No deployment, no publishing, no ad/spend action.
  - No GitHub issue created/edited/closed; PR #15 not merged; `main` not modified.
  - Issue #14 remains open; branch protection NOT VERIFIED.
  - Prior Phase 0/Phase 1 audit and remediation reports preserved.
  - **Phase 2 implementation has NOT started.** Work stops here pending explicit human approval of the open decisions.
