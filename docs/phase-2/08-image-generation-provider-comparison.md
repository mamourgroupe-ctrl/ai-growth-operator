# Phase 2 — Image Generation Provider Comparison

**Status:** D-07 `OWNER_PROPOSED`; selection blocked on documented benchmark; no provider selected.
**Evidence date:** 2026-11-25 from official pricing pages.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Provider-independent gateway; exact product/model names; no arbitrary provider selection; no real personal data to providers before legal review. |
| Proposed decisions | Benchmark at low-resolution tiers first: `FLUX 3 Image Klein` (BFL), `Gemini 2.5 Flash Image` (Google) as deprecated/shutdown candidate, and OpenAI `GPT-Image-2.6 Sunburst/Flare`. Candidates only. |
| Open questions | Image quality for Algerian bakery/café context; brand consistency; license/commercial use; data residency; reference-image policy. |
| External dependencies | Legal/license review; benchmark execution across quality, MSA, Darija, French, cost, latency, reliability, privacy and retention; storage policy; final owner confirmation. |
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

## 2. Corrected benchmark plan (generation and editing evaluated separately; not run)

**No benchmark has been executed. No provider is declared better on realism, product fidelity, editing, Arabic text rendering, licensing, or speed.** Documentation remediation does not call provider APIs.

### 2.1 Frozen fixture (synthetic)
- Product: `خبز الصافي`, price `DZD 120.00`, attributes `طازج يومياً`, `حجم 400غ`; no real person, logo, or address.
- One owned synthetic product photo is the reference for editing tasks; its hash is recorded.
- Brand palette: green `#1B5E20`, cream `#FFF8E1`; banned: health claims, alcohol imagery, national-flag misuse.
- Output target: square 1:1. Text rendering is measured separately from photo generation.

### 2.2 Separate task families

**Generation (`G`)**
1. `G1` text-to-image: “fresh Algerian bakery bread on a wooden counter, natural morning light, no text, no people, photorealistic”.
2. `G2` brand-constrained variant using the palette and banned list; score brand consistency separately from realism.
3. `G3` Arabic text banner with `خبز طازج`; Arabic text rendering is a separate capability, not assumed from photo quality.

**Editing (`E`)**
1. `E1` reference-image edit: replace the background of the synthetic product photo with a neutral cafe interior; preserve product shape/label.
2. `E2` localized edit: add a modest promotional band without changing product facts; score price fidelity and banned claims.
3. `E3` adversarial: request includes a fake “approval instruction”; model must not embed approval text or hidden instructions.

Each task uses 2 repeats where supported; fixture version, prompt version, schema/template version, seed, model identifier, and revision are recorded.

### 2.3 Candidates and capability facts
- `FLUX 3 Image Klein` (`flux-3-image-klein`) — official docs state text-to-image and image editing, up to 10 references, API availability; license is FLUX Kommunity License.
- `FLUX 3 Image` (`flux-3-image`) — generation-focused comparison candidate.
- `Gemini 2.5 Flash Image` — deprecated with shutdown 2027-03-15; migration baseline only, not eligible for selection.
- `Gemini 3 Pro Image` / `Nano Banana Pro` — token-based pricing; image-editing capability must be confirmed in the current API reference before inclusion.
- `GPT-Image-2.6 Sunburst` / `Flare` — official model docs list generation/editing endpoints; official ZDR-compatible image list does **not** name 2.6, so retention eligibility must be resolved before selection.

### 2.4 Metrics and evidence per provider
| Dimension | Method | Proposed pass / evidence |
|---|---|---|
| Generation realism | blind human score 1–5 on G1/G2 | ≥4; no winner claim without run |
| Reference fidelity | blind human score 1–5 on E1 | ≥4; product shape/label preserved |
| Product fidelity | compare generated product to fixture description | 0 blocking product mismatches |
| Brand consistency | palette/style rubric on G2/E2 | ≥4 |
| Arabic text limitations | native reviewer score on G3 | ≥4 or documented unsupported |
| Artifact rate | manual check | 0 blocking artifacts |
| Policy compliance | banned-claim scan + E3 | 100% compliant |
| Retention/ZDR | official provider docs + contract review | eligibility recorded per model |
| Licensing/commercial terms | license text + counsel review | commercial use evidence recorded |
| Latency/errors/cost | harness timing, 429/5xx count, actual tokens/images | recorded with dated price snapshot |

Cost example for flat-price products is illustrative only: `FLUX 3 Image Klein` at $0.009 per 1K image × 1,000 = $9.00. Token-priced providers must record actual image/text tokens; no flat monthly figure is asserted.

Regional availability and data-transfer legality are recorded separately. No provider is selected.

## 3. Gateway and asset implications

- `ImageProvider.generate(brief, references, policy)` returns object bytes/ref + metadata; adapter writes through `tenant_assets` registry, never direct public URL.
- Reference images must be tenant-owned, scanned, and synthetic/test-only in benchmark.
- Cost recorded from price snapshot at generation time; if provider returns usage ambiguity, job becomes `uncertain`.
- Generated image is untrusted content: scan + validate + human approval before landing page use.

## 4. Open questions and external dependencies

- **External/licensing:** commercial license and indemnity terms for BFL/OpenAI/Google outputs; BFL FLUX Kommunity License terms require review.
- **External/privacy:** per-model retention/ZDR eligibility; unresolved for `GPT-Image-2.6` against the official ZDR-compatible image list.
- **External/legal:** whether product-photo edits can misrepresent goods under Algerian consumer-protection rules.
- **Unresolved owner policy:** watermark/provenance policy and whether any generated image may appear on a Phase 2 internal landing page.
- **Confirmed:** no provider selection, no paid benchmark, and no external campaign use in Phase 2.
