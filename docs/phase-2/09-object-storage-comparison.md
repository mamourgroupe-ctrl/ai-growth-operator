# Phase 2 — Object Storage Comparison

**Status:** D-08 `OWNER_PROPOSED`; selection blocked on documented comparison; no provider selected.
**Evidence date:** 2026-11-25 from official pricing pages.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | S3-compatible storage abstraction; private-by-default assets; no production credentials in repo. |
| Proposed decisions | Evaluate `Cloudflare R2`, `Backblaze B2`, and `AWS S3 Standard` against the same workload; no provider is selected or designated default. Requirement: S3-compatible API. |
| Open questions | Region/residency, legal/DPA, egress patterns, malware scanning integration, bucket policy, lifecycle, cost at actual volume. |
| External dependencies | Legal review; provider availability from Algeria; owner approval. |
| Risks | Egress surprises; vendor lock-in; unscanned assets; accidental public URLs. |

## 1. Official pricing evidence (USD)

Sources fetched 2026-11-25: [Cloudflare R2](https://developers.cloudflare.com/r2/pricing/), [Backblaze B2](https://www.backblaze.com/cloud-storage/pricing), [AWS S3](https://aws.amazon.com/s3/pricing/).

| Provider & class | Storage | Operations | Retrieval | Egress | Free tier |
|---|---|---|---|---|---|
| `Cloudflare R2` Standard | $0.015/GB-month | Class A $4.50/1M; Class B $0.36/1M | $0 | $0 | 10 GB-month, 1M Class A, 10M Class B / month |
| `Cloudflare R2` Infrequent Access | $0.01/GB-month | Class A $9/1M; Class B $0.90/1M | $0.01/GB | $0 | same free tier |
| `Backblaze B2` | starts $6.95/TB-month (≈$0.0068/GB-month) | Class A/B/C free for pay-as-you-go; Class D $0.004/10k, first 2,500/day free | $0 | up to 3× stored data free, then $0.01/GB | first 10 GB free |
| `AWS S3 Standard` (us-east-1) | $0.023/GB first 50TB; $0.022 next 450TB; $0.021 over 500TB | PUT/COPY/POST/LIST $0.005/1k; GET $0.0004/1k | $0 | separate data transfer charge (not in fetched excerpt) | not stated in fetched excerpt |
| `AWS S3 Standard-IA` | $0.0125/GB | GET $0.001/1k, PUT $0.01/1k | $0.01/GB | separate | not stated |
| `AWS S3 Glacier Instant` | $0.004/GB | see source | $0.03/GB | separate | not stated |
| `AWS S3 Glacier Flexible` | $0.0036/GB | see source | see source | separate | not stated |
| `AWS S3 Deep Archive` | $0.00099/GB | see source | see source | separate | not stated |

B2 states no minimum file size or storage duration. R2 states zero egress fees. S3 prices above are US East (N. Virginia); other regions differ.

## 2. Corrected workload assumptions and cost calculation (illustrative, not measured)

Pricing evidence date: **2026-11-25**; list prices must be re-verified before a decision. The pricing pages use `GB`; this document treats them as provider-billed decimal GB and does **not** silently convert to GiB. If a provider defines billing units as GiB, the calc must be repeated and labeled accordingly. Storage, requests, retrieval, and egress are separate line items.

| Scenario | Volume | Notes |
|---|---|---|
| Pilot | 40 GB stored; 50k GET/month; 10k PUT/month | Assumes 3× free egress is not exceeded where applicable |
| Growth | 500 GB stored; 2M GET/month; 200k PUT/month | Signed reads dominate; egress volume must be measured separately |

### Corrected monthly estimates (storage + requests only; retrieval/egress shown separately)
- **R2 Standard pilot:** billable storage = 40 − 10 free = 30 GB × $0.015 = **$0.45**. 10k Class A PUT within 1M free; 50k Class B GET within 10M free; egress $0. Total **≈$0.45**. The prior “within free tier” claim was wrong because 40 GB exceeds the 10 GB-month storage allowance.
- **B2 pilot:** billable storage = 40 − 10 free = 30 GB. At $6.95 per 1,000 GB ≈ **$0.21** (≈$0.20 if a 1,024 GiB convention is applied). Class A/B/C free for pay-as-you-go; egress unknown. Total **≈$0.21 + applicable egress**.
- **S3 Standard pilot:** 40 × $0.023 = $0.92; PUT 10k × $0.005/1k = $0.05; GET 50k × $0.0004/1k = $0.02. Total **≈$0.99 + egress**.
- **R2 Standard growth:** 500 × $0.015 = $7.50; GET 2M × $0.36/M = $0.72; PUT 0.2M × $4.50/M = $0.90; egress $0. Total **≈$9.12**.
- **B2 growth:** 500 × $6.95/1,000 ≈ **$3.48**; operations free. Egress allowance = 3 × 500 = 1,500 GB. Overage formula: `max(0, actual_egress_GB − 1,500) × $0.01/GB`. The prior “$60 for 1.5 TB egress” was incorrect; 1,500 GB × $0.01 would be $15 and is actually within the free allowance. Total **≈$3.48 + overage**.
- **S3 Standard growth:** 500 × $0.023 = $11.50; PUT 200k × $0.005/1k = $1.00; GET 2M × $0.0004/1k = $0.80. Total **≈$13.30 + egress**.

Retrieval and lifecycle costs are excluded above and must be added if IA/Glacier classes are used. R2 IA has a 30-day minimum and cannot be transitioned back to Standard via lifecycle policy; S3 IA/Glacier have retrieval charges; B2 Class D calls are separately priced.

These are estimates from list prices, not invoices. No provider is selected.

## 3. Reproducible evaluation plan (not yet run)

1. Same 100 synthetic image files (total 200 MB), same access pattern: 1,000 PUT, 10,000 signed GET, 100 DELETE, 1 lifecycle transition to IA where supported.
2. Same SDK abstraction (`ObjectStorage` protocol) and identical tenant key layout.
3. Record: operation success rate, p50/p95 latency, cost from provider calculator/list price, signed URL expiry behavior, region availability, bucket policy behavior, scan integration hooks.
4. No real business data, no production credentials outside secret store.

## 4. Decision criteria (to be applied by owner after evaluation)

| Criterion | Weight (proposed) |
|---|---|
| S3 compatibility / abstraction fit | High |
| Egress cost predictability | High |
| Residency / legal acceptability | High (blocking) |
| Operational simplicity | Medium |
| Malware-scan/queue integration | Medium |
| Cost at pilot size | Medium |
| Ecosystem familiarity | Low |

## 5. Non-price decision dimensions (must be completed before selection)

| Dimension | R2 | B2 | S3 | Status |
|---|---|---|---|---|
| Encryption at rest/in transit | AES-256 at rest, TLS in transit; keys managed by Cloudflare | Official B2 docs cover server-side encryption; key options to be reviewed | SSE-S3 default at rest; SSE-KMS/DSSE-KMS/SSE-C options | Facts from official docs; contract review pending |
| Access control | S3-compatible API, private buckets, signed URLs, Cloudflare IAM | S3-compatible API, application keys/capabilities | IAM, bucket policies, block public access | Architecture requirement below |
| Backup/recovery | Durability/replication documented; lifecycle/versioning behavior to map | Replication, Object Lock, snapshots documented | Versioning, replication, Glacier tiers documented | Runbook pending |
| Regional availability | Automatic/location hints; jurisdictions `eu`, `us`, `fedramp` | Region list exists; not yet incorporated | Choose region; example prices are us-east-1 | Residency unresolved |
| Data residency | No Algeria jurisdiction listed for R2 | Must be confirmed from provider docs/contract | Must be confirmed from provider docs/contract | **External legal dependency** |
| DPA/subprocessors/contract | Not evaluated | Not evaluated | Not evaluated | **External legal dependency** |

No provider is selected on pricing alone. Residency/legal acceptability is a blocking criterion; advertising execution use is Phase 3 and is not part of this comparison.

## 6. Architecture requirements regardless of provider

- Private buckets; signed URLs with 5–15 minute expiry; no public ACL.
- Server-generated keys `tenant/{tenant_id}/{kind}/{uuid}`; no client-supplied key/bucket.
- Objects immutable while referenced; deletion only after DB reference removal and approval/legal check.
- Checksum + MIME/magic-byte validation + scan status gate.
- Abstraction must allow switching without changing tenant APIs; no provider-specific URL in DB rows.
