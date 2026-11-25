# Phase 2 — Automated Content Validation Specification

**Status:** Proposed. No implementation authorized.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | AI output untrusted; human approval mandatory; no external publishing; no AI authorization of decisions. |
| Proposed decisions | Deterministic-first validation pipeline with optional model-assisted checks; severity model (`block`/`warn`/`info`); validation evidence stored per version. |
| Open questions | Banned claim taxonomy per sector; tolerance for near-duplicate text; model-assisted validator provider; reviewer sign-off criteria. |
| External dependencies | Pilot sector approval; legal review of claim rules; Darija reviewer. |
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

- `overall=blocked` → cannot submit for Arabic review/approval; editor must edit or request policy override (override cannot clear price/banned/asset/instruction blocks).
- `overall=warned` → can submit with visible warning; owner decides.
- Every re-validation creates a new `content_validations` row; no mutation of prior evidence.

## 6. Price extraction rules (deterministic)

- Parse Arabic-Indic and Western digits; normalize `د.ج`, `DZD`, `DA` to `DZD` only if configured.
- If a price token is found without a recognized currency and product context is ambiguous → `currency_missing` block.
- If generated text mentions multiple products, match by exact product name snippet first; otherwise block on ambiguity.
- Do not convert currency. FX source unresolved; any conversion must come from approved snapshot.

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
