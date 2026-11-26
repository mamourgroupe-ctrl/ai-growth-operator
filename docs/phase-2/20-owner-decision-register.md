# Phase 2.6 — Owner Decision Register

**Freeze date:** 2026-11-24 UTC  
**Status:** Decision workshop record. This document does **not** grant owner approval.  
**Branch:** `arena/5dc98770-ai-growth-operator`  
**HEAD at Phase 2.6 start:** `8da2f9aa161070ab2f4af7beca54b9bd41345e23`  
**Companion freeze document:** `19-engineering-design-freeze.md`

## Status vocabulary

| Status | Meaning |
|---|---|
| `OWNER_PROPOSED` | Preliminary owner choice recorded for review; not finally approved and not frozen. |
| `OWNER_APPROVED` | Final owner approval already recorded in Phase 0/1 or by explicit owner decision. |
| `FROZEN` | Technical baseline fixed for implementation planning; does not grant owner approval to a preliminary decision. |
| `DEFERRED` | Explicitly assigned to Phase 3 or later. |
| `BLOCKED` | Cannot be closed without external evidence or final owner confirmation. |

`Owner confirmation` remains pending unless explicitly recorded. A preliminary owner choice is never represented as final approval.

## 1. Register summary

| ID | Decision | Options | Recommended option | Consequence | Status | Owner confirmation |
|---|---|---|---|---|---|---|
| D-01 | Final content approval | Owner-only; editor submission; reviewer findings; viewer read-only | Owner only; editors prepare/submit, Arabic reviewers report, viewers read-only | Determines decide-endpoint role check, UI buttons, audit semantics and negative tests | `OWNER_PROPOSED` | Final confirmation pending |
| D-02 | Landing pages and leads MVP scope | Internal create/edit/preview; public publishing; lead management | Internal create/edit/preview and existing draft/version history only; all leads deferred | Removes Phase 2 public routes, lead tables, lead APIs and lead UI; preserves future Phase 3 design | `OWNER_PROPOSED` | Final confirmation pending |
| D-03 | Currency policy | DZD-only user-facing; DZD+USD display; approved-source conversion | DZD-only user-facing; USD AI cost evidence internally; no conversion or FX source | Blocks foreign-currency display and conversion; advertising FX remains Phase 3 | `OWNER_PROPOSED` | Final confirmation pending |
| D-04 | AI usage quotas | Configurable tenant limits; numeric values after benchmark | Configurable tenant quotas; administrator proposes values, owner approves; no enforcement before approval | Determines reservation/finalization, error codes, admin config, audit and cost reporting | `OWNER_PROPOSED` | Final confirmation pending; numeric values `BLOCKED` |
| D-05 | Pilot sector | Retail, tourism, professional services, manufacturing, restaurants/hospitality, other evidenced sector | Study candidates; no selection; sector-neutral foundations proceed with synthetic fixtures | Affects claim rules, fixtures, recruiting, legal sensitivity and validation evidence | `OWNER_PROPOSED` | Final confirmation pending |
| D-06 | Language policy | Preserve approved MSA/Darija/French/RTL model; reopen | Preserve approved policy; document human-review capability separately | Affects locale enum, RTL QA, reviewer queue, validation and UI labels | `OWNER_APPROVED` | Approved in Phase 0/1; reviewer staffing `BLOCKED` |
| D-07 | AI provider selection | Benchmarked selection; cheapest by list price; provider-neutral fake MVP | Select only after documented benchmark; no winner | Affects adapters, registry, ZDR/retention, cost evidence and enablement flags | `OWNER_PROPOSED` | Final confirmation pending; evidence `BLOCKED` |
| D-08 | Storage provider selection | R2, B2, S3; defer selection | Select after documented security/residency/cost comparison; no winner | Affects bucket policy, backup, egress, residency and contract review | `OWNER_PROPOSED` | Final confirmation pending; evidence `BLOCKED` |
| D-09 | Landing-page version representation | Circular approved-version FK; version-owned approval status; no version table | Version-owned approval status with `landing_page_versions` | Removes circular insert dependency; supports internal draft/version history | `FROZEN` | Engineering baseline |
| D-10 | French UI locale scope | Full UI locale; content style only | Preserve as secondary locale/content style per Phase 0; confirm UI breadth | Affects translation scope, QA, navigation and error messages | `BLOCKED` | Owner input pending |
| D-11 | Viewer lead-PII redaction | Redacted by default; owner-configurable fields; full access | Deferred with lead functionality | No Phase 2 lead data; revisit with Phase 3 leads | `DEFERRED` | Lead functionality deferred |
| D-12 | Arabic review requirement for `fr` | Required; not required by default; owner-enabled flag | Not required by default; owner may enable | Affects review queue, state machine and benchmark scope | `BLOCKED` | Owner input pending |
| D-13 | Generated-image watermark/provenance | Visible watermark; metadata-only provenance; owner decision | Metadata provenance badge now; no external-image policy until approved | Affects image pipeline, UI badges, licensing review | `BLOCKED` | Owner/licensing input pending |
| D-14 | `main` branch protection (#14) | Verified; not verified | Treat as NOT VERIFIED until owner confirms with read access | Production release gate only; does not block local synthetic development | `BLOCKED` | API 403; issue #14 open |
| D-15 | Cross-border transfer/legal position | Counsel review required; assume compliant | Qualified Algerian counsel review; no compliance claim | Blocks real personal/provider data use and public launch, not synthetic local work | `BLOCKED` | Counsel opinion pending |
| D-16 | Non-material edit definition for approval supersession | Configured allowlist; any edit supersedes; owner-defined | Configured allowlist for internal labels only; all body changes supersede | Affects versioning, diff UI, audit and stale-approval risk | `FROZEN` | Engineering baseline |
| D-17 | Notification/SLA for approvals | No notifications in MVP; reminders later | No notification subsystem in Phase 2 MVP | Avoids external side effects and new delivery channel | `DEFERRED` | Outside MVP |
| D-18 | API version-prefix consolidation | Keep root Phase 1 routes; prefix all Phase 2; consolidate later | Keep root legacy routes; new Phase 2 under `/api/v1`; no silent rewrite | Affects clients, docs, OpenAPI tests and backward compatibility | `FROZEN` | Engineering baseline |

---

## 2. D-01 — Content approval authority

**Question.** Who may grant final content approval, and how are validation, linguistic review, human approval and publication eligibility separated?

**Current documented state.** Phase 0/2 docs preserve owner-only final approval. The owner has now supplied a preliminary choice confirming owner-only final authority; editors prepare and submit, Arabic reviewers report findings, and viewers remain read-only. The choice is `OWNER_PROPOSED`, not finally approved.

**Technical consequences.** The decision controls the `decide` endpoint role dependency, UI action visibility, 403 negative tests, audit metadata and any delegation model. Arabic reviewer capability is review evidence only; editor permission is preparation/submission only.

**Options and owner preliminary choice — OWNER_PROPOSED.**

1. **Owner-only final decision — OWNER_PROPOSED.** Editor creates/edits/submits; Arabic reviewer records language findings; viewer reads; owner approves/rejects/requests changes.
2. Editor final approval. Requires an explicit owner change and new negative-test matrix.
3. Delegated approval to another owner only. Requires delegation records and audit.
4. Arabic reviewer approval. Rejected unless owner explicitly changes policy because it conflates linguistic quality with business authorization.

**Dependencies.** D-06 reviewer capability; D-12 French review; `tenant_memberships.is_arabic_reviewer`; audit design; UI approval queue.

**Status:** `OWNER_PROPOSED`. **Owner confirmation:** final confirmation pending. The owner-only baseline is preserved; `block` validation, Arabic linguistic review and human approval remain separate gates.

**Four distinct gates (engineering baseline, not an authority change).**

| Gate | Field / state | Owner of gate | Phase 2 treatment |
|---|---|---|---|
| Content validation | `validation_status`: `pending/blocked/warned/passed` | deterministic validator | `FROZEN` technical control; `block` never overridable |
| Linguistic review | `linguistic_review_status`: `not_required/pending/approved/changes_requested` | Arabic reviewer | `FROZEN` for `ar`/`ar-DZ`; staffing `BLOCKED` externally |
| Human approval | `approval_status`: `pending/approved/rejected/changes_requested/superseded` | owner-only baseline | D-01 `OWNER_PROPOSED`; final confirmation pending |
| Publication eligibility | `publication_eligibility`: `not_eligible/eligible/externally_published_deferred` | owner + policy | No Phase 2 publishing endpoint; internal publish eligibility `DEFERRED` |

**State machine to implement only after final owner confirmation of D-01.**

```text
DRAFT
  -> VALIDATING
  -> VALIDATION_FAILED -> DRAFT
  -> REVIEW_REQUIRED (ar / ar-DZ; or fr if owner enables D-12)
  -> REVIEWED
  -> SUBMITTED
  -> APPROVED | REJECTED | CHANGES_REQUESTED | CANCELLED
APPROVED -> SUPERSEDED (material edit creates a new version)
APPROVED -> SCHEDULED (internal calendar date only, no external effect)
SCHEDULED -> ELIGIBLE (internal draft/version readiness only; publish endpoint DEFERRED)
EXTERNALLY_PUBLISHED -> DEFERRED / Phase 3 integration, not implemented in Phase 2
```

- Phase 2 states: `DRAFT`, `VALIDATING`, `VALIDATION_FAILED`, `REVIEW_REQUIRED`, `REVIEWED`, `SUBMITTED`, `APPROVED`, `REJECTED`, `CHANGES_REQUESTED`, `SUPERSEDED`, `CANCELLED`, internal `SCHEDULED`.
- Deferred/external states: internal publish execution, `PUBLISHED` to social platforms or ad channels, campaign launch, paid-action execution.
- `REJECTED` and `CHANGES_REQUESTED` require a non-empty reason and return to a new draft version.
- `CANCELLED` is allowed before decision; it never mutates historical validation or review evidence.

---

## 3. D-02 — Landing pages and leads

**Question.** What landing/lead functionality is in the Phase 2 MVP?

**Owner preliminary choice (`OWNER_PROPOSED`).** Phase 2 includes internal creation, editing and preview of landing pages, plus drafts and version history where already included in the approved design. It excludes public publishing, external publication, public lead ingestion and lead management functionality.

**Deferred to Phase 3 or later (`DEFERRED`).** The `leads` database table, public lead ingestion endpoint, lead management APIs, lead management UI, public lead submission workflows, internal publish execution endpoints, public URLs, custom domains and external hosting. Historical references remain as historical records; no future Phase 3 architecture is redesigned here.

**Current documented state.** Earlier docs proposed internal-only pages but still carried lead entities, public lead routes and lead-management UI. Those statements are reconciled by this register and `19-engineering-design-freeze.md`.

**Scope comparison.**

| Dimension | Preliminary Phase 2 scope | Deferred / Phase 3 scope |
|---|---|---|
| Page create/edit/version/preview | Yes | N/A |
| Draft and version history | Yes, where already in approved design | N/A |
| Lead capture/lead table/lead APIs/lead UI | No | `DEFERRED` |
| Public URL, hosting, custom domain | No | `DEFERRED` |
| Public lead ingestion | No | `DEFERRED` |
| Internal publish execution endpoint | No | `DEFERRED` until separately approved |
| Tenant resolution | Session-derived only | Future public slug resolver remains a future design, not a Phase 2 route |
| Operational cost | Low; no public hosting | Future review required |
| Security risk | Contained by RLS and role checks | Future security/legal review required |

**Technical consequences.** Phase 2 migrations include only `landing_pages` and `landing_page_versions`. No `leads` table, public route, lead API, lead UI or publish-execution endpoint is implemented. Phase 3 may revisit the deferred design without treating it as approved.

**Dependencies.** Final owner confirmation; D-15 legal review if public pages are later proposed; D-08 storage/residency if external assets are later used. D-11 is `DEFERRED` with lead functionality.

**Status:** `OWNER_PROPOSED`. **Owner confirmation:** final confirmation pending.

---

## 4. D-03 — Currency and financial display

**Question.** How are AI SaaS cost, advertising finance and general business currency display separated?

**Current documented state.** The owner has supplied a preliminary currency rule: DZD only for user-facing amounts; USD only for internal AI provider cost evidence. There is no automatic conversion, no exchange-rate source, no foreign-currency user display and no financial conversion authorization. Advertising FX snapshots remain `DEFERRED` to Phase 3.

**Three distinct concepts.**

1. **AI SaaS consumption and cost accounting.** Internal USD price snapshots and usage records; owner-visible cost reporting; not a customer-facing FX conversion.
2. **Advertising budgets and spending.** Phase 3 only; includes FX snapshots and budget approval; no Phase 2 table or endpoint.
3. **General business currency display.** DZD-only user-facing; no display of original foreign-currency prices in Phase 2.

**Options and owner preliminary choice — OWNER_PROPOSED.**

- **DZD-only user-facing MVP (preliminary owner choice).** Keep provider cost evidence in USD internally; do not display estimated DZD equivalents or original foreign-currency prices.
- DZD + USD display. Not approved; would require a separate owner decision.
- Approved-source conversion. Not authorized in Phase 2; requires source, refresh policy, rounding, timestamp, spread and legal/accounting approval.

**Technical consequences.** No FX provider is invented; AI price snapshots must never be used as FX evidence; validation must not convert currencies; advertising FX tables remain out of Phase 2 migrations.

**Dependencies.** D-04 cost reporting; legal/accounting review; validation price rules; UI display components.

**Status:** `OWNER_PROPOSED`. **Owner confirmation:** final confirmation pending. This decision does not establish an exchange-rate source or authorize financial conversion.

---

## 5. D-04 — AI usage quotas and cost governance

**Question.** What usage model and limits govern AI SaaS consumption in Phase 2?

**Current documented state.** The owner preliminary choice supports configurable per-tenant quota infrastructure. Numeric values are not approved. The system administrator proposes numeric values; the owner reviews and approves them. No numerical quota enforcement is active until those values exist. Sector-neutral quota infrastructure may be designed independently of final numeric limits.

**Technical lifecycle (engineering default).**

1. Validate request schema, locale/style, tenant-owned references and idempotency key.
2. Check tenant quota and rate limits.
3. Reserve estimated usage atomically in `usage_counters` and `ai_usage_records(status='reserved')`.
4. Create idempotent `ai_generation_jobs` row keyed by `(tenant_id, idempotency_key)`.
5. Execute provider request through the gateway with timeout and bounded retry; never retry from `uncertain`.
6. Record actual provider usage and cost from the dated `ai_price_snapshots` row.
7. Finalize the reservation to `finalized`.
8. Release or mark `failed`/`uncertain` on failure; reconcile `uncertain` manually or in Phase 3 tooling.
9. Append audit evidence; never double-charge the same idempotency key.

**Failure handling to freeze.**

| Case | Required behavior |
|---|---|
| Duplicate request | Same idempotency key returns original job/usage record; no second provider call |
| Retry | Bounded, jittered, only before an ambiguous outcome; no blind retry from `uncertain` |
| Timeout | Mark `uncertain`; no silent second charge |
| Provider failure | Finalize usage as `failed`, release reservation where safe |
| Partial result | Store as untrusted draft only if complete enough for validation; otherwise `failed` |
| Missing usage metadata | `uncertain`, estimated reservation retained, manual reconciliation flag |
| Estimate vs actual | Reservation is estimate; actual recorded at finalization |
| Pricing change | New price snapshot required; existing usage keeps its request-time snapshot |
| Auditability | Append-only records with actor, job, provider, model, snapshot, decision and timestamps |

**Enforcement options and trade-offs.**

| Limit type | Benefit | Trade-off |
|---|---|---|
| Request count | Simple, predictable | Does not control expensive prompts/images |
| Input/output tokens | Closest to text cost | Requires provider token parity and cache accounting |
| Image generation count | Simple for images | Editing and high-resolution tiers must be counted separately |
| Image editing count | Separates capabilities | Requires explicit request kind |
| Cost-based | Best economic control | Requires trusted price snapshots and actual usage metadata |

**Preliminary owner choice:** configurable tenant limits across request count, token count, image counts and cost controls. Numeric values and any cost ceiling are `BLOCKED` until administrator proposal, owner approval and benchmark evidence. No numeric value or subscription price is proposed here.

**Dependencies.** System-administrator numeric proposals; owner approval of those values; D-07 benchmark evidence; D-03 currency boundary; D-15 legal gate; admin config surface; worker queue hardening.

**Status:** `OWNER_PROPOSED`. **Owner confirmation:** final confirmation pending; numeric values `BLOCKED`. Advertising budgets must never be mixed into this model.

---

## 6. D-05 — Pilot sector

**Question.** Which sector is the first pilot, and what evidence supports it?

**Current documented state.** No pilot sector has been selected. Existing bakery/salon/café and five-sector frameworks are research hypotheses and candidate sectors only, not owner-approved selections. Sector-neutral foundations may proceed using synthetic fixtures. Sector-specific rules wait for the sector selection decision.

**Transparent scoring model (1–5 each).**

| Criterion | Evidence required |
|---|---|
| Frequency of marketing activity | content-volume diary or owner interview |
| Content production demand | interview + sample request count |
| Social media usage | observable public presence or owner report |
| Arabic and French testing ability | language samples and reviewer availability |
| Ease of recruiting pilot users | named contacts or recruitment channel |
| Willingness to pay | structured card test or pricing interview |
| Workflow complexity | process map; low complexity preferred |
| Regulatory/privacy risk | counsel or documented claim-risk review |

**Candidate handling.** Retail, tourism/travel, restaurants/hospitality, professional services and manufacturing are research candidates. “Other sectors supported by actual evidence” may be added only with evidence. Bakery/patisserie is a hypothesis/research candidate only; it is not a selected or recommended sector.

**Separation of evidence types.**

- Hypothesis: documented assumption, weight and date.
- Market evidence: external observation with source and date.
- Interview evidence: date, participant role, question set, raw notes.
- Pilot validation result: measured task completion/content outcomes.
- Final owner decision: explicit written selection; cannot be inferred from scores.

**Low-cost validation plan.** Owner interviews; willingness-to-pay card test; two-week content-volume diary; synthetic-data generation demo; blind Arabic/Darija scoring. No lead demo in Phase 2; lead functionality is `DEFERRED`.

**Status:** `OWNER_PROPOSED`. **Owner confirmation:** final confirmation pending. Sector-neutral foundations are not blocked; sector-specific rules are `BLOCKED` until selection.

---

## 7. D-06 — Technical and product language policy

**Question.** Should the Phase 2 language model be reopened?

**Current documented state.** Approved Phase 0/1 requirements already specify Modern Standard Arabic (`ar`) default, Algerian Darija (`ar-DZ`) as a distinct option, French (`fr`) secondary, full RTL for Arabic, explicit locale metadata and mixed Arabic/French handling. This is preserved rather than reopened.

**Review surface.**

| Surface | Confirmed requirement |
|---|---|
| Content generation | `ar`, `ar-DZ`, `fr`; Darija not a literal MSA translation |
| UI labels | Arabic-first RTL; French secondary; mixed direction isolated with `dir` |
| Validation | locale/style mismatch block; Darija authenticity hint warn |
| Approval | Arabic review evidence visible to approver for `ar`/`ar-DZ` |
| Landing pages | Conditional on D-02; locale and RTL QA required if approved |
| Notifications | Deferred; no notification subsystem in MVP |
| Error messages | Locale-aware where UI locale exists; no raw provider error leakage |

**Human-review capability.** Arabic reviewer staffing is not assumed. Capability uses the existing `tenant_memberships.is_arabic_reviewer` field from `0001_initial`; reviewer availability is `BLOCKED` externally. Review findings never grant final approval.

**Status:** `OWNER_APPROVED` for the language model. **Owner confirmation:** approved in Phase 0/1 requirements; reviewer staffing `BLOCKED` externally.

---

## 8. Additional decisions discovered during reconciliation

### D-07 — AI provider selection

- **Question:** Which text/image providers are enabled for real use?
- **Owner preliminary choice (`OWNER_PROPOSED`):** No winner is selected. Selection must follow a documented benchmark.
- **Mandatory benchmark criteria:** output quality; Arabic MSA quality; Algerian Darija quality; French quality; cost; latency; reliability; privacy and data retention.
- **Current state:** Official list-price evidence exists; no benchmark run; no selection and no benchmark result is invented.
- **Consequence:** Wrong choice risks unverified language quality, retention violations and unpredictable cost.
- **Options:** benchmarked selection; cheapest list price; provider-neutral fake MVP.
- **Preliminary default:** benchmarked selection plus legal/privacy review; fake adapters until then.
- **Status:** `OWNER_PROPOSED`; evidence `BLOCKED`. **Owner confirmation:** final confirmation pending; no winner recorded.

### D-08 — Storage provider selection

- **Question:** Which S3-compatible storage provider and region are acceptable?
- **Owner preliminary choice (`OWNER_PROPOSED`):** No winner is selected. Selection must follow a documented comparison.
- **Mandatory comparison criteria:** data residency; security; encryption; backup and recovery; data processing agreements; retention; egress costs; total operating cost.
- **Current state:** Corrected cost matrix exists; residency/DPA unresolved; no provider assessment or winner asserted.
- **Consequence:** Blocks production data and public assets until legal/contract evidence exists.
- **Options:** R2, B2, S3, or abstraction-only MVP with synthetic fixtures.
- **Preliminary default:** abstraction-only until the full comparison and legal review are complete.
- **Status:** `OWNER_PROPOSED`; evidence `BLOCKED`. **Owner confirmation:** final confirmation pending; no winner recorded.

### D-09 — Landing-page version representation

- **Question:** How are immutable page versions represented without a circular FK?
- **Current state:** API had a version endpoint while the schema only had `landing_pages.approved_version_id`.
- **Consequence:** Circular insert dependency and ambiguity about approval truth.
- **Options:** circular FK; version-owned approval status; no version table.
- **Recommended:** `landing_page_versions` owns approval status; `landing_pages` keeps only a non-authoritative pointer.
- **Status:** `FROZEN` engineering reconciliation. **Owner confirmation:** not an owner product decision.

### D-10 and D-11 — French UI scope and lead redaction

- **Question:** How broad is French UI support, and what can viewers see in lead lists?
- **Current state:** French is approved as secondary; UI breadth is `BLOCKED` on owner input. All lead functionality, including lead-list redaction, is `DEFERRED`.
- **Baseline:** preserve French as secondary content style/UI where translated. No Phase 2 lead data exists, so D-11 is revisited in Phase 3.
- **Status:** D-10 `BLOCKED`; D-11 `DEFERRED`. **Owner confirmation:** D-10 pending; D-11 not applicable to Phase 2.

### D-12 — Arabic review for French

- **Question:** Does `fr` require human linguistic review?
- **Current state:** `ar`/`ar-DZ` require Arabic review; `fr` does not by default.
- **Recommended:** no French review requirement unless owner enables it.
- **Status:** `BLOCKED`. **Owner confirmation:** pending.

### D-13 — Image provenance

- **Question:** Watermark or metadata-only provenance?
- **Current state:** AI drafts carry a UI provenance badge; external-use policy unresolved.
- **Recommended:** metadata + UI badge now; no external image policy before owner/licensing review.
- **Status:** `BLOCKED`. **Owner confirmation:** pending.

### D-14 and D-15 — Platform and legal gates

- **Question:** Are `main` branch protection and cross-border transfer position verified?
- **Current state:** Branch protection NOT VERIFIED (403); Algerian legal opinion absent.
- **Consequence:** Blocks production release and real-data provider use, not local synthetic development.
- **Status:** `BLOCKED`. **Owner confirmation:** pending.

### D-16 and D-17 — Supersession detail and notifications

- **Question:** What counts as non-material edit, and are approval notifications in MVP?
- **Recommended:** only internal labels are non-material; no notification subsystem in MVP.
- **Status:** D-16 `FROZEN` engineering baseline; D-17 `DEFERRED`. **Owner confirmation:** not required for engineering baseline; notification scope pending if later requested.

### D-18 — API version-prefix consolidation

- **Question:** Should existing root-level Phase 1 routes be moved under `/api/v1`?
- **Current state:** Phase 1 routes are `/auth/...`, `/organizations/...`, `/healthz`, `/readyz`; proposed Phase 2 routes use `/api/v1/...`.
- **Consequence:** Silent rewriting breaks existing clients and tests; coexistence is safe if documented.
- **Options:** keep legacy root routes; prefix new routes only; consolidate with compatibility aliases.
- **Recommended:** keep legacy root routes unchanged, add all Phase 2 routes under `/api/v1`, and require change control for later consolidation.
- **Status:** `FROZEN` engineering baseline. **Owner confirmation:** not an owner product decision.

---

## 9. Final confirmation and evidence before implementation entry

The owner has supplied preliminary choices for D-01, D-02, D-03, D-04, D-05, D-07 and D-08. All are `OWNER_PROPOSED`; none is `OWNER_APPROVED` or `FROZEN`. Do not re-request the preliminary decisions.

1. Final owner confirmation is required for all seven `OWNER_PROPOSED` decisions.
2. D-04 numeric values require system-administrator proposal and owner approval; no numerical enforcement before approval.
3. D-07 requires documented benchmark evidence across quality, MSA, Darija, French, cost, latency, reliability, privacy and retention.
4. D-08 requires documented comparison evidence across residency, security, encryption, backup/recovery, DPA, retention, egress and total cost.
5. D-05 sector-specific rules require a selection decision; sector-neutral foundations are not blocked.
6. D-10, D-12, D-13, D-14 and D-15 remain `BLOCKED` on owner, platform or legal evidence.
7. D-11 is `DEFERRED` with Phase 3 lead functionality.
