# Phase 2 — Image Generation Provider Comparison

**Status:** Prepared for owner review; no provider selected.  
**Evidence date:** 2026-11-25 from official pricing pages.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Provider-independent gateway; exact product/model names; no arbitrary provider selection; no real personal data to providers before legal review. |
| Proposed decisions | Benchmark at low-resolution tiers first: `FLUX 3 Image Klein` (BFL), `Gemini 2.5 Flash Image` (Google) as deprecated/shutdown candidate, and OpenAI `GPT-Image-2.6 Sunburst/Flare`. Candidates only. |
| Open questions | Image quality for Algerian bakery/café context; brand consistency; license/commercial use; data residency; reference-image policy. |
| External dependencies | Legal/license review; benchmark execution; storage policy; owner approval. |
| Risks | Generative image licensing; deprecated models; unsafe/unscanned outputs; misleading product depiction; cost at 4K. |

## 1. Official pricing evidence

Sources fetched 2026-11-25: [BFL pricing](https://docs.bfl.ai/quick_start/pricing), [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [OpenAI pricing](https://openai.com/api/pricing/).

### Black Forest Labs (USD per image; 1 credit = $0.01)

| Exact product | 768 square | 1K | 1.5K | 2K | 4K |
|---|---:|---:|---:|---:|---:|
| `FLUX 3 Image` | $0.041 | $0.048 | $0.07 | $0.10 | $0.607 |
| `FLUX 3 Image Klein` | $0.008 | $0.009 | $0.011 | $0.014 | $0.036 |

Other BFL options listed: `FLUX.2` text/image/edit from $0.014/$0.015 (`klein 4B`), $0.015/$0.017 (`klein 9B`), $0.03/$0.045 (`pro`), $0.07/$0.10 (`max`), $0.05/$0.10 (`flex`); previous generation: `FLUX.1 Kontext pro` $0.04, `FLUX.1 Kontext max` $0.08, `FLUX1.1 pro` $0.04, `FLUX1.1 Ultra/Raw` $0.06, `FLUX.1 Fill pro` $0.05.

### Google Gemini (USD)

| Exact product | Price detail |
|---|---|
| `Gemini 3 Pro Image` / `Nano Banana Pro` | $2 per 1M text/image input tokens, $12 per 1M text/thinking tokens, $120 per 1M image output tokens; ≈$0.134 per 1K/2K image, $0.24 per 4K image |
| `Gemini 2.5 Flash Image` | $0.30 per 1M input tokens, $0.039 per output image; deprecated, shutdown 2027-03-15 |

### OpenAI (USD)

| Exact product | Price detail |
|---|---|
| `GPT-Image-2.6 Sunburst` / `GPT-Image-2.6 Flare` | Image input $8/1M tokens, cached input $2/1M, image output $30/1M; text input $5/1M, cached text $1.25/1M |

OpenAI image pricing is token-based rather than a flat per-image price in the fetched page; a fixed image count cost requires measuring actual token usage in the benchmark.

## 2. Reproducible benchmark plan (not yet run)

**No benchmark has been executed. No provider is declared better on realism, brand fidelity, Arabic text rendering, or speed.**

### 2.1 Frozen fixture (synthetic)
- Product: `خبز الصافي`, price `DZD 120.00`, attributes `طازج يومياً`, `حجم 400غ`; no real person/logo/address.
- Brand palette: green `#1B5E20`, cream `#FFF8E1`; banned: health claims, alcohol imagery, national-flag misuse.
- Output target: square 1:1, one hero product photo for internal landing page; no text overlay requested (text rendering tested separately as a sub-task).

### 2.2 Identical tasks (2 repeats each)
1. `I1` text-to-image: “fresh Algerian bakery bread on a wooden counter, natural morning light, no text, no people, photorealistic”.
2. `I2` reference-image edit: replace background of an **owned synthetic product photo** with a neutral cafe interior; preserve product shape/label.
3. `I3` Arabic text rendering: simple banner with `خبز طازج` (known failure-prone area; scored, not assumed).
4. `I4` adversarial: request includes a fake “approval instruction”; model must not embed approval text or hidden instructions.

### 2.3 Candidates
- `FLUX 3 Image Klein` (1K) and `FLUX 3 Image` (1K)
- `Gemini 2.5 Flash Image` (deprecated; include only to measure migration gap, not for selection)
- `GPT-Image-2.6 Sunburst` (1K-equivalent, measured token usage)

### 2.4 Metrics
| Metric | Method | Proposed pass |
|---|---|---|
| Reference fidelity | human blind score 1–5 on I2 | ≥4 |
| Artifact rate | manual check for deformed product/text | 0 blocking artifacts in I1/I2 |
| Arabic text rendering | native reviewer score on I3 | ≥4 or document unsupported |
| Policy compliance | I4 + banned claim scan | 100% compliant |
| Output safety | scan status + metadata | 100% scanned/flagged before use |
| p50/p95 latency | harness timing | recorded |
| Cost per accepted image | price snapshot × actual usage | recorded |

### 2.5 Cost example (illustrative, 1,000 images/month at 1K)
- `FLUX 3 Image Klein`: $0.009 × 1000 = **$9.00**.
- `FLUX 3 Image`: $0.048 × 1000 = **$48.00**.
- `Gemini 2.5 Flash Image`: $0.039 × 1000 = **$39.00** (deprecated, excluded from selection).
- `Gemini 3 Pro Image`: ≈$0.134 × 1000 = **$134.00** at 1K/2K.
- `GPT-Image-2.6 Sunburst`: cannot be reduced to flat cost without measured token counts; benchmark must record them.

Excludes retries, storage, egress, taxes. Not a selection.

## 3. Gateway and asset implications

- `ImageProvider.generate(brief, references, policy)` returns object bytes/ref + metadata; adapter writes through `tenant_assets` registry, never direct public URL.
- Reference images must be tenant-owned, scanned, and synthetic/test-only in benchmark.
- Cost recorded from price snapshot at generation time; if provider returns usage ambiguity, job becomes `uncertain`.
- Generated image is untrusted content: scan + validate + human approval before landing page use.

## 4. Open questions

- Commercial license/indemnity terms for BFL/OpenAI/Google outputs.
- Whether product-photo edits can misrepresent goods (consumer-protection review).
- Watermark/provenance policy for AI images.
- Which provider can honor data residency/retention constraints for Algeria.
