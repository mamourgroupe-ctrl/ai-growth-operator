# Phase 2 — Final Engineering Planning Report

**Outcome:** Phase 2 documentation prepared. **Phase 2 implementation has NOT started.**  
**Status:** Ready for owner review; no provider/storage/sector selection made; no code, migration, endpoint, issue, deployment, or spend action performed.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Preserved Phase 0/1 decisions only: modular monolith, multi-tenant SaaS, Next.js+TypeScript, FastAPI, PostgreSQL, SQLAlchemy+Alembic, RLS+RBAC, provider-independent gateway, S3-compatible abstraction, owner-only approval, no direct publishing/spend, no production data in lower environments. |
| Proposed decisions | All Phase 2 architecture, schema, API, QA, deployment, roadmap, backlog and ADR-020..027 items in `docs/phase-2/` — subject to owner approval. |
| Open questions | Pilot sector; roadmap re-baseline of #23/#24/#25; text/image provider; storage provider; legal/privacy/ANPDP position; quotas; FX source; French UI scope. |
| External dependencies | Official benchmark execution, Algerian legal review, provider terms/DPAs, human Arabic/Darija reviewers, owner sign-off, #14 verification. |
| Risks | Scope conflict; unproven Darija quality; provider cost/deprecation; unauthorized data transfer; approval bypass; branch protection unverified. |

## 1. Branch and repository state (reviewed)

- Branch: `arena/5dc98770-ai-growth-operator` (current branch; based on `main` commit `7820f29893815562613dd9c72ea4b0e51b956df3`).
- HEAD before documentation: `aaf37f1f0304f0a47c11c2566f6204dc594a96c9`.
- `main` / `origin/main`: `7820f29893815562613dd9c72ea4b0e51b956df3` — unchanged.
- Draft PR #15: OPEN, DRAFT, unmerged, `headRefOid=aaf37f1...` — not merged.
- Issue #14: OPEN; `main` branch protection **NOT VERIFIED** (prior 403 on read attempt).
- Working tree before this task: clean.

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

**Modified files:** none. Prior Phase 0/Phase 1 reports were preserved unchanged. **Deleted files:** none.

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

- Reproducible benchmark **plans** with frozen synthetic fixtures, exact prompts/tasks, repetition counts, metrics and pass criteria are documented in docs 07 and 08.
- **No benchmark has been executed** (no sandbox calls, no spend, no API keys). No provider has been declared faster, cheaper in practice, more Arabic-capable, or higher quality from an unrun test.
- Cost tables are illustrative calculations from list prices only; they are not invoices or performance evidence.

## 5. Recommended architecture (proposed, not approved)

- Single FastAPI modular monolith + separate worker process sharing package and PostgreSQL; Next.js responsive Arabic-first UI.
- Tenant-owned tables use shared schema with FORCE RLS, `USING`/`WITH CHECK`, composite tenant FKs, and `ago_app` non-superuser runtime role.
- AI gateway with `TextProvider`/`ImageProvider` protocols, config-driven model registry with dated price snapshots, policy engine, fake adapters in CI, quotas and idempotent usage records; client cannot select provider/model.
- Untrusted generated output → deterministic validation → Arabic human review for `ar`/`ar-DZ` → owner-only approval with immutable version snapshots. No tools, publishing, spend, or self-approval.
- Private S3-compatible asset storage with server-generated keys, short signed URLs, MIME/checksum/scan gates; provider deferred.
- Approval center and landing/leads are **gated** on owner re-baseline of #23/#24/#25; otherwise contracts/drafts only.
- Deployment: local/CI/staging/production with synthetic data below production, feature flags default-off, secrets in environment stores, migration as controlled step.

## 6. Unresolved decisions requiring owner input

1. Approve/reject Phase 2 package split and re-baseline of #23/#24/#25.
2. Approve pilot sector (recommendation: bakeries/patisseries; alternatives documented).
3. Approve text/image provider after benchmark; acknowledge deprecations.
4. Approve object storage provider/residency.
5. Legal/privacy: DPO, processing register, automated logs, cross-border transfer authorization, allowed data categories, retention.
6. Quotas/cost caps; fixed per-tenant interpretation of #21 (billing remains non-goal).
7. FX source, timestamp, rounding for #22.
8. French UI locale scope; viewer lead-PII redaction policy.
9. Verify `main` branch protection (#14) before production release.

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

Existing Phase 2 issues #8–#11, #16–#22, #27 are retained with proposed dependency order: foundation (#16/#17) → queue (#20) → gateway/usage (#9/#18/#21) → content/validation (#8 + proposed N2) → Arabic review (#27) → creative/calendar (#19) → gated #23 → gated #24/#25. Proposed new issues: P2-N1 onboarding assistant, P2-N2 validation, P2-N3 benchmark harness, P2-N4 asset upload/scan. No issues were created or edited. Full criteria in `16-github-issue-backlog.md`.

## 9. Testing and acceptance strategy

CI lint/test/security gate preserved; unit, API/contract, DB/RLS catalog, migration cycle, fake-provider integration, worker/queue, adversarial validation, approval-negative and optional E2E/a11y suites proposed. Human gates: Arabic reviewer for `ar`/`ar-DZ`; owner review of benchmark/provider/storage/pilot; legal gate before real data. No benchmark result or test is claimed to have been run in this planning task. Detailed criteria in `13-testing-qa-strategy.md`.

## 10. Internal architecture review (performed before this report)

- Verified all 18 deliverables exist and each required decision-status section is present.
- Verified no provider/storage/sector is selected; no benchmark is claimed as executed.
- Verified non-negotiables preserved: RLS+RBAC, owner-only approval, no direct publishing/spend, S3 abstraction, no production data in lower environments.
- Verified roadmap conflict #23/#24/#25 is explicitly gated rather than silently moved.
- Verified no prior Phase 0/1 report was modified.
- Verified repository state: only untracked `docs/phase-2/`; no code/migration/API/infra changes.

## 11. Commit and confirmations

- Commit SHA for Phase 2 planning deliverables 01–17: `b51eee6ce964491340c3c5082b097dd62a0ff556` (documentation-only; created after the internal check). This final report is added in a separate documentation-only commit because a file cannot contain its own commit SHA; see `git log -1 --format=%H` after that commit for its SHA.
- Confirmations:
  - No application code, migrations, endpoints, frontend screens, provider integrations, dependency changes or infrastructure changed.
  - No production credentials used; no external provider calls or benchmark spending performed.
  - No deployment, no publishing, no ad/spend action.
  - No GitHub issue created/edited/closed; PR #15 not merged; `main` not modified.
  - Issue #14 remains open; branch protection NOT VERIFIED.
  - Prior Phase 0/Phase 1 audit and remediation reports preserved.
  - **Phase 2 implementation has NOT started.** Work stops here pending explicit human approval of the open decisions.
