# Phase 2 — Automated Content Validation Specification

**Status:** Proposed. No implementation authorized.

## Decision status

| Category | Summary |
|---|---|
| `OWNER_APPROVED` / `FROZEN` baseline | AI output untrusted; human approval mandatory; no external publishing; no AI authorization of decisions. |
| `OWNER_PROPOSED` / `FROZEN` | Owner choices D-01–D-05, D-07, D-08 are preliminary. Deterministic-first validation, severity model and evidence storage are `FROZEN` engineering baselines. |
| Open questions | Banned claim taxonomy per sector; tolerance for near-duplicate text; model-assisted validator provider; reviewer sign-off criteria. |
| `BLOCKED` / `DEFERRED` | Sector-specific rules `BLOCKED` pending selection; legal claim review and Darija reviewer availability `BLOCKED`; lead functionality `DEFERRED`. |
| Risks | False positives blocking content; false negatives passing claims; over-reliance on automated checks. |

## 1. Principles

1. Validation is advisory/enforcing **before** review, never a substitute for human approval.
2. Deterministic checks run first and fail closed on uncertain data.
3. Every finding stores rule code, severity, evidence, and validator version.
4. Validation inputs are tenant-owned content + immutable facts snapshot; no live uncontrolled DB reads mid-validation.
5. Model-assisted checks, if used, run through the same gateway and cannot alter content or approval state.

## 2. Validation stages

| Stage | Trigger | Blocking? |
|---|---|---|
| `structural` | immediately after generation or manual save | yes on malformed schema |
| `factual` | before submit-for-approval | yes on price/currency mismatch |
| `policy` | before submit | yes on banned claims/unsafe content |
| `brand` | before submit | warn unless guideline marked mandatory |
| `linguistic` | before Arabic review | warn; reviewer decides |
| `duplicate` | before submit | warn; owner may override |
| `human_arabic_review` | for `ar`/`ar-DZ` | required before submit |
| `owner_approval` | final | always required |

## 3. Rule catalogue (initial)

| Code | Severity | Check | Evidence |
|---|---|---|---|
| `schema_invalid` | block | JSON required fields/types/locales/styles | missing field path |
| `empty_output` | block | non-empty text within limits | length |
| `locale_mismatch` | block | declared locale/style matches expected script/style markers | detected script |
| `price_mismatch` | block | every mentioned price/currency matches product snapshot | expected/found values |
| `currency_missing` | block if price mentioned | currency present | snippet |
| `banned_claim` | block | exact/near phrase from brand/legal banned list | matched phrase + rule source |
| `unsupported_claim` | warn/block per guideline | superlative/health/cure claims | snippet |
| `tool_instruction_leak` | block | output contains instruction-like approval/publish commands | snippet |
| `duplicate_content` | warn | similarity threshold (proposed 0.9) to prior tenant versions | matched version id |
| `brand_tone` | warn | tone vocabulary outside brand rules | matched tokens |
| `darija_authenticity_hint` | warn | heuristic MSA-only markers in `ar-DZ` | markers |
| `asset_unscanned` | block | referenced asset scan status not clean | asset id/status |
| `asset_cross_tenant` | block | asset tenant mismatch | asset id |
| `seasonality_stale` | warn | references date/holiday not in window | detected phrase |

## 4. Data snapshot

Validation receives a frozen snapshot:
```jsonc
{
  "tenant_id": "uuid",
  "products": [{"id":"uuid","name":"...","price_amount":"120.00","currency":"DZD"}],
  "brand_rules": {"banned_claims": ["شفاء", "أفضل في الجزائر"], "required_disclaimers": []},
  "content": {"locale":"ar-DZ","style":"darija","text":"..."},
  "assets": [{"id":"uuid","scan_status":"clean","tenant_id":"uuid"}],
  "validator_version": "2026-11-25.1"
}
```

## 5. Output contract

```jsonc
{
  "overall": "blocked|warned|passed",
  "findings": [
    {"rule_code":"price_mismatch","severity":"block","passed":false,
     "evidence":{"product_id":"uuid","expected":"DZD 120.00","found":"DZD 100.00"},
     "validator_version":"2026-11-25.1"}
  ],
  "checked_at":"2026-11-25T00:00:00Z"
}
```

- `overall=blocked` → cannot submit for Arabic review/approval. There is **no override path** for `block` findings. Must-correct rule codes: `schema_invalid`, `empty_output`, `locale_mismatch`, `price_mismatch`, `currency_missing`, `banned_claim`, `tool_instruction_leak`, `asset_unscanned`, `asset_cross_tenant`.
- `overall=warned` → can submit with visible warning. Owner may record an override reason for `warn` findings only (`unsupported_claim` when configured warn, `duplicate_content`, `brand_tone`, `darija_authenticity_hint`, `seasonality_stale`); the reason is appended to audit evidence.
- `overall=passed` → may proceed to Arabic review where required, then approval.
- Every re-validation creates a new `content_validations` row; no mutation of prior evidence. Canonical body is `content_versions.body` per `03-database-design.md §1`.
- Validation endpoints use `/api/v1/content/versions/{id}/validate`; approval endpoints use `/api/v1/approval/...` per `05-api-contracts.md §2`. No advertising validation/approval kind exists in Phase 2.

## 6. Price extraction rules (deterministic)

- Parse Arabic-Indic and Western digits; normalize `د.ج`, `DZD`, `DA` to `DZD` only if configured.
- If a price token is found without a recognized currency and product context is ambiguous → `currency_missing` block.
- If generated text mentions multiple products, match by exact product name snippet first; otherwise block on ambiguity.
- Do not convert currency (D-03 `OWNER_PROPOSED`). No Phase 2 FX source or conversion rule; user-facing amounts are DZD-only and USD AI cost evidence is internal only.

## 7. Banned claims and legal sensitivity

- Seed banned list from brand guidelines + pilot-sector legal list pending review.
- Bakeries/patisseries candidate: health/cure claims, “best in Algeria” superlatives, inaccurate ingredients.
- Do not assert a phrase is illegal without legal evidence; rule code records `rule_source`.

## 8. Model-assisted validation (optional, future)

- Same gateway, deterministic prompt, JSON schema, low temperature.
- May propose findings but cannot clear a deterministic block or change approval state.
- Must be benchmarked with synthetic data; no tenant PII transfer before privacy gate.

## 9. Acceptance criteria (future implementation)

- 100% price-mismatch detection on synthetic fixture set including Arabic-Indic digits.
- 100% block of injected approval/publish instructions.
- 100% block of cross-tenant/unscanned asset references.
- ≤5% false-positive rate on 50 human-labelled pilot sentences (target; measure, don't claim).
- Validation evidence immutable and visible in approval UI.
