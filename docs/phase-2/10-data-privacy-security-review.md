# Phase 2 — Data Privacy and Security Review

**Status:** Prepared for owner/legal review. Planning only; not a legal compliance certification.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | RLS + app RBAC; tenant isolation on all tenant-owned records; no production data in dev/test; no real personal data to external providers before privacy/legal review; AI output untrusted; owner-only approval; no direct publishing/spend. |
| Proposed decisions | Data classification, blocking gates for provider transfer, DPO/register/log requirements mapped to design, DPIA trigger, lead PII minimization. |
| Open questions | DPO appointment, ANPDP declaration/authorization status, cross-border transfer authorization, retention schedule, lead PII redaction for viewer, subprocessors list. |
| External dependencies | Algerian legal counsel/owner determination; provider DPAs; malware scanner; production secret management. |
| Risks | Unauthorized transfers; PII in prompts/logs; legal non-compliance; unscanned assets; prompt injection; approval bypass. |

## 1. Data classification

| Class | Examples | Allowed handling |
|---|---|---|
| Tenant business facts | business profile, products, brand rules | tenant-only DB, optional provider transfer only after legal gate; synthetic in tests |
| Personal data (tenant users) | names/emails/phones of staff/owners | auth DB, RLS; never sent to AI providers |
| Personal data (leads) | lead name/email/phone/message | tenant-only DB; minimized; no provider use; access-controlled |
| Untrusted AI output | generated text/images | treated as data, never instruction or authorization |
| Secrets | provider keys, storage credentials | secret manager/GitHub Environments only; no logs/repo |
| Audit/usage | actor/action/cost metadata | append-only; redact prompts/PII |

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
| Cost abuse | loop generation calls | quota reservation, rate limit, idempotency, owner cost caps |
| Asset exposure | guess storage URL | private bucket, short signed URL, ownership check |
| Malicious upload | SVG/HTML/script disguised image | MIME+magic check, scan status, safe rendering |
| Lead PII leak | viewer reads contacts | redaction policy + role check + audit |
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

## 8. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Unauthorized international transfer | Blocking | Provider transfer gate; synthetic-only until cleared |
| Missing DPO/register/log evidence | High | Legal review; create artifacts before pilot |
| PII in model prompts | High | Data minimization + redaction tests |
| Prompt injection into approval | High | No tools + owner-only decision + negative tests |
| Unscanned asset use | Medium-high | scan_status gate; private storage |
| Over-collection of leads | Medium | minimal lead fields; retention policy pending |
