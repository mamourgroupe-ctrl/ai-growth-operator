# Phase 2 — Object Storage Comparison

**Status:** Prepared for owner review; no provider selected.  
**Evidence date:** 2026-11-25 from official pricing pages.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | S3-compatible storage abstraction; private-by-default assets; no production credentials in repo. |
| Proposed decisions | Benchmark/backtest `Cloudflare R2` as default candidate; `Backblaze B2` and `AWS S3 Standard` as alternatives. Requirement: S3-compatible API. |
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

## 2. Workload assumptions for comparison (illustrative, not measured)

| Scenario | Volume | Notes |
|---|---|---|
| Pilot | 20 tenants × 2 GB = 40 GB; 50k GET/month; 10k PUT/month | 1K product images + logos + generated images |
| Growth | 500 GB; 2M GET/month; 200k PUT/month | signed reads dominate |

### Illustrative monthly costs (storage + requests only; egress estimate where given)
- Pilot, R2 Standard: 40 GB × $0.015 = $0.60 + GET 0.05M×$0.36/M=$0.018 + PUT 0.01M×$4.50/M=$0.045 → **≈$0.66** (within free tier in practice).
- Pilot, B2: 40 GB ≈$0.27 + Class A/B free → **≈$0.27** (within 10 GB free tier for part of volume).
- Pilot, S3 Standard: 40 GB × $0.023 = $0.92 + PUT 10k×$0.005/1k=$0.05 + GET 50k×$0.0004/1k=$0.02 → **≈$0.99 + egress**.
- Growth, R2: 500 GB × $0.015=$7.50 + 2M×$0.36/M=$0.72 + 0.2M×$4.50/M=$0.90 → **≈$9.12 + $0 egress**.
- Growth, B2: 500 GB ≈$3.48 + free ops + possible egress if >3× stored (6M×$0.01/M=$60 if full 1.5TB egress) → **≈$3.48–$63.48**.
- Growth, S3: 500 GB × $0.023=$11.50 + PUT $1.00 + GET $0.80 = **≈$13.30 + egress**.

These are estimates from fetched list prices, not invoices. Actual signed-URL access patterns and region selection may change the result.

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

## 5. Architecture requirements regardless of provider

- Private buckets; signed URLs with 5–15 minute expiry; no public ACL.
- Server-generated keys `tenant/{tenant_id}/{kind}/{uuid}`; no client-supplied key/bucket.
- Objects immutable while referenced; deletion only after DB reference removal and approval/legal check.
- Checksum + MIME/magic-byte validation + scan status gate.
- Abstraction must allow switching without changing tenant APIs; no provider-specific URL in DB rows.
