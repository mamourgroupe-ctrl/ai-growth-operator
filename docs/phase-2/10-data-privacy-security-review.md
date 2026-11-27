# Phase 2 — Data Privacy and Security Review

**Status:** Prepared for owner/legal review. Planning only; not a legal compliance certification.

## Decision status

| Category | Summary |
|---|---|
| `OWNER_APPROVED` baseline | RLS + app RBAC; tenant isolation on all tenant-owned records; no production data in dev/test; no real personal data to external providers before privacy/legal review; AI output untrusted; owner-only approval; no direct publishing/spend. |
| `OWNER_PROPOSED` decisions | D-01–D-05, D-07, D-08 per `20-owner-decision-register.md`. Data classification and transfer gates are `FROZEN` engineering baselines. |
| `BLOCKED` / `DEFERRED` | DPO, ANPDP, transfer authorization, retention, subprocessors and final owner confirmation `BLOCKED`; lead PII redaction `DEFERRED`. |
| External dependencies | Algerian legal counsel/owner determination; provider DPAs; malware scanner; production secret management; owner verification of `main` branch protection. |
| Confirmed boundary | No advertising FX, ad budgets, paid execution, outbox/reconciliation, or external execution in Phase 2. AI cost snapshots are SaaS cost evidence only. |
| Risks | Unauthorized transfers; PII in prompts/logs; legal non-compliance; unscanned assets; prompt injection; approval bypass. |

## 1. Data classification

| Class | Examples | Allowed handling |
|---|---|---|
| Tenant business facts | business profile, products, brand rules | tenant-only DB, optional provider transfer only after legal gate; synthetic in tests |
| Personal data (tenant users) | names/emails/phones of staff/owners | auth DB, RLS; never sent to AI providers |
| Personal data (leads) | Phase 3+ `DEFERRED` | No Phase 2 lead table, route or UI; revisit in Phase 3 |
| Untrusted AI output | generated text/images | treated as data, never instruction or authorization |
| Secrets | provider keys, storage credentials | secret manager/GitHub Environments only; no logs/repo |
| Audit/usage | actor/action/cost metadata | append-only; redact prompts/PII |

**Staging and test data policy (corrected):** local, CI, and staging use **synthetic fixtures only**; no production or production-derived data is copied into them. Any future use of de-identified production-derived data requires a separate owner decision plus legal review and a documented anonymization standard; it is not authorized by this document.

**Currency boundary (D-03 `OWNER_PROPOSED`):** DZD only for user-facing amounts; USD AI provider cost evidence internally. No automatic conversion, no FX source, no original foreign-currency user display and no financial conversion authorization in Phase 2. Advertising FX remains `DEFERRED` to Phase 3.

## 2. Algerian privacy context (official source reviewed)

Official source: [JORADP Law 25-11 PDF](https://www.joradp.dz/FTP/JO-FRANCAIS/2025/F2025048.pdf), Official Gazette No. 48 (2025-07-24), pp. 14–18; [NATLEX metadata](https://natlex.ilo.org/dyn/natlex2/r/natlex/fe/details?p3_isn=118858). Accessed 2026-11-25.

Verified text changes:
- DPO requirement added (art. 41 bis).
- Processing registers added (art. 41 bis 2).
- Automated processing operation logs added (art. 41 bis 3).
- Regional control poles (art. 27 bis) and Title V bis for law-enforcement processing.
- Former arts. 10 and 11 repealed; art. 6 exception narrowed to personal/domestic processing and national defence/security matters.

Context from secondary summaries (not authoritative quotes): prior declaration regime under former arts. 12–21 remains relevant; cross-border transfer authorization under art. 44 (Law 18-07 as amended) remains relevant; penalties for illicit transfers were reported. **These points require confirmation by qualified Algerian counsel before reliance.**

Design implications: plan for DPO contact/role, register of processing activities, automated operation logging, and a transfer-control gate. Do not claim compliance from architecture alone.

## 3. Security controls mapped to Phase 2

| Control | Implementation requirement | Verification |
|---|---|---|
| Tenant isolation | RLS FORCE on every tenant table; composite tenant FKs; app role `ago_app` NOBYPASSRLS | Automated catalog check + cross-tenant API/RLS tests |
| Authorization | Server-resolved membership/role; owner-only approval; reviewer flag separate | Role matrix tests |
| Input validation | Pydantic schemas; allowlists for locale/style/kind; price numeric | Contract tests |
| Prompt injection | Delimit untrusted business data; versioned templates; no tools; local JSON schema validation | T4/T4-image adversarial benchmark |
| Output safety | Untrusted draft; sanitize before render; no raw HTML; scan assets | Unit + integration tests |
| AI authorization boundary | Gateway cannot publish, spend, approve, change budgets | Static review + negative tests |
| Secrets | No keys in code; masked logs; rotated keys | Secret scanner in CI |
| Audit | Owner decisions, generation jobs, asset upload/use, provider config changes append-only | Integrity tests |
| Transport/storage | HTTPS; private buckets; short-lived signed URLs | Config review |
| PII minimization | No lead data in prompts; no user PII in AI requests; redact logs | Log inspection tests |
| Backup/restore | Tenant-scoped restore test | Operational runbook (future) |

### 3.1 Verified current controls vs proposed controls

**Verified current (observed 2026-11-24/25):** CI workflow has `lint`, `test`, and `security` jobs; latest run `45565465339` on `8da2f9a` reported all three successful. The security job runs bandit and the repository secret scanner. Local test execution was not possible in the audit sandbox (`pytest` unavailable); CI success is not local test evidence. `main` branch protection is **NOT VERIFIED**; the GitHub API returned `403 Resource not accessible by integration`.

**Proposed future gates (not implemented here):** RLS catalog verification for every tenant table; OpenAPI contract/role-matrix tests; Alembic upgrade/downgrade cycle; fake-provider integration; approval-negative and prompt-injection suites. These must not be described as existing CI gates.

### 3.2 PostgreSQL RLS semantics

- A policy is `PERMISSIVE` by default; permissive policies combine with OR. Add a `RESTRICTIVE` policy only when an AND condition is intended.
- `FORCE ROW LEVEL SECURITY` makes RLS apply to the table owner; it does not grant privileges.
- Runtime role `ago_app` must be non-superuser, `NOBYPASSRLS`, and explicitly granted table privileges. Grants and policies are separate controls.
- Tenant context is transaction-local: `set_config('app.current_tenant_id', <uuid>, true)`. It is set server-side from membership/session, never from client input.
- Public lead submission is `DEFERRED` to Phase 3 or later; no Phase 2 route. Any future public resolver must be trusted and use RLS context; no privileged bypass.

## 4. Provider transfer gate (blocking)

Before any real tenant personal data is sent to an external AI provider:
1. Legal review of Law 25-11 as amended and cross-border transfer authorization requirements.
2. Provider DPA/subprocessor list, retention, training-on-data policy, residency options.
3. Documented data categories allowed to leave tenant DB (prefer business facts only, never lead PII or user credentials).
4. Owner written approval recorded in ADR.
5. Production key/secret stored in secret manager; no real data in CI/dev.

Until all are complete: benchmark and development use **synthetic fixture only**. If gate fails, gateway remains disabled for real tenants.

## 5. Threat model highlights

| Threat | Attack | Mitigation |
|---|---|---|
| Cross-tenant data read | craft tenant id / change context | RLS + server-derived tenant + tests |
| Approval bypass | editor calls decide endpoint | owner-only dependency + negative test |
| AI instruction injection | malicious product text instructs output | no tools, bounded schema, validation, human review |
| Cost abuse | loop generation calls | configurable tenant quotas; administrator proposes numeric values, owner approves; no numerical enforcement before approval; rate limit and idempotency |
| Asset exposure | guess storage URL | private bucket, short signed URL, ownership check |
| Malicious upload | SVG/HTML/script disguised image | MIME+magic check, scan status, safe rendering |
| Lead PII leak (**DEFERRED — Phase 3 or later**) | Future Lead contact data if introduced after Phase 2; no Phase 2 Leads data is collected or processed | Future requirement: redaction policy, role check and audit must be designed and approved before Leads are introduced. No Phase 2 implementation is implied. |
| Secret leak | provider error logged | sanitize exceptions, scanner |

## 6. Privacy by design for onboarding assistant

- Assistant session stores only inferred proposals; facts written after explicit confirmation.
- Confidence/missing fields shown to user; rejected values remain in session only.
- Max session retention proposed 30 days, then purge. No PII used for prompt improvement without separate approval.

## 7. Open compliance artifacts to prepare (not created here)

- DPO designation/contact evidence (if required).
- Register of processing activities template.
- Automated processing log specification aligned with art. 41 bis 3.
- Transfer impact assessment / authorization position for each provider.
- Subprocessor inventory and retention table.
- Breach response runbook.

### 7.1 Questions for qualified Algerian counsel (external dependency)

1. Does Law 18-07 art. 44 authorization apply to each proposed AI/storage provider, and what evidence is required?
2. What DPO, processing-register, and automated-operation-log obligations arise under Law 25-11?
3. Is ANPDP declaration or authorization required before pilot processing?
4. What retention/deletion rules apply to audit logs and AI usage records? Lead retention is `DEFERRED` with Phase 3 lead functionality.
5. Are DPAs/subprocessor lists sufficient for business facts only, or is a broader transfer arrangement needed?
6. What commercial-use and consumer-protection constraints apply to generated images/text?

These are questions, not legal conclusions. No compliance claim is made.

## 8. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Unauthorized international transfer | Blocking | Provider transfer gate; synthetic-only until cleared |
| Missing DPO/register/log evidence | High | Legal review; create artifacts before pilot |
| PII in model prompts | High | Data minimization + redaction tests |
| Prompt injection into approval | High | No tools + owner-only decision + negative tests |
| Unscanned asset use | Medium-high | scan_status gate; private storage |
| Over-collection of leads | Medium | no Phase 2 lead collection; minimal fields and retention policy in Phase 3 |
