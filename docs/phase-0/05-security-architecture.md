# Phase 0 — Security Architecture

**Status:** Proposed for approval. No security controls are implemented in Phase 0.
**Threat model:** lightweight STRIDE review tailored to a multi-tenant SaaS with AI-generated text.

## 1. Trust boundaries

1. Browser ↔ API (public network).
2. API ↔ PostgreSQL (internal, but still guarded by RLS).
3. Worker ↔ LLM provider (external processor of prompt text).
4. CI/CD ↔ GitHub Secrets (deployment boundary).

## 2. Threat model summary

| Threat | Example | Primary control |
|---|---|---|
| Spoofing | Stolen session cookie, credential stuffing | HttpOnly/SameSite cookies, login rate limit, session rotation |
| Tampering | CSRF on content approval | CSRF token on all mutations, strict content-type checks |
| Repudiation | Unknown actor changed a campaign | Append-only audit log |
| Information disclosure | Tenant A reads tenant B data | RLS + application membership checks + redacted logs |
| Denial of service | Generation spam / huge prompts | Quotas, prompt size limits, provider timeout, bounded retries |
| Elevation of privilege | Viewer edits content | RBAC enforcement at API layer, tests per role |

## 3. Authentication and sessions

- Email + password with Argon2id hashing (encoded parameters, no plaintext or reversible storage).
- Opaque random session token stored as SHA-256 hash in `sessions`; raw token only in the cookie.
- Cookie attributes: `HttpOnly`, `Secure`, `SameSite=Lax`, path `/`, 14-day idle expiry, 30-day absolute expiry.
- Rotate session id on login; revoke on logout and password change.
- Login endpoint rate-limited per IP and per email; no account enumeration in responses.
- MFA and managed IdP are explicitly deferred; revisit if PRD requires SSO or stricter assurance.

## 4. Authorization

| Action | Owner | Editor | Viewer |
|---|---|---|---|
| View workspace/campaigns/content | yes | yes | yes |
| Create/edit campaigns and content | yes | yes | no |
| Approve content | yes | yes* | no |
| Manage members/roles | yes | no | no |
| Change tenant settings | yes | no | no |

\* Pending PRD confirmation; if approval must be owner-only, change the API check and tests before Phase 2.

Every handler resolves the tenant from the URL, verifies membership, then checks role. RLS is applied via `SET LOCAL app.current_tenant_id`.

## 5. Data protection

- TLS everywhere; HSTS at the edge.
- Managed Postgres with encryption at rest; daily backups + PITR.
- No secrets or provider keys in the repository; GitHub Environments hold deploy secrets.
- Logs are structured JSON with redaction: no passwords, tokens, cookie values, or full prompts.
- Prompt text is stored only in `ai_generation_jobs` and cleaned on a schedule.
- No production data in lower environments.
- Data export and deletion workflows are Phase 3 candidates pending legal review.

## 6. AI-specific controls

- Treat campaign names and briefs as untrusted input; delimit them in prompts and never grant tool access.
- Validate model output against expected shape and length before persistence.
- Strip obvious prompt-injection instructions from user-provided briefs where feasible; never let brief text define system instructions.
- Single provider adapter with timeout, max tokens, and cost cap per request.
- Provider receives only minimum necessary text; no tenant secrets or credentials.
- Store provider/model name for traceability; never store provider API keys in DB.

## 7. Application and supply-chain hygiene

- Pydantic validation on all request bodies; reject unknown fields by default.
- Parameterized SQL only via SQLAlchemy; no string-built queries.
- Security headers: CSP (deny inline by default), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`.
- `pip-audit`/Dependabot and SAST in CI; high-severity findings block merge.
- Branch protection on `main`: required PR, required checks, no direct push, no auto-merge.
- Production deploys require an environment approval; never merge without review.

## 8. Incident response outline

1. Detect via health checks/logs/error reports.
2. Contain by revoking sessions/tokens or disabling a provider key.
3. Assess using audit logs and request IDs.
4. Eradicate via patch + deploy; restore from backup only if data integrity is affected.
5. Notify affected tenants according to legal requirements (obligations to be confirmed).
6. Record a post-incident action item in the backlog.

## 9. Compliance note

No claim of compliance is made in Phase 0. Algerian data-protection, sector rules, and AI-provider data-residency obligations must be reviewed before pilot data is stored.
