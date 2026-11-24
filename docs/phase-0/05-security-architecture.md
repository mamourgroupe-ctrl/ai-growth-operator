# Phase 0 — Security Architecture (post-audit)

**Status:** Corrected for approval. No controls implemented in Phase 0.

## 1. Trust boundaries

1. Browser ↔ API (public network; Arabic-first responsive client).
2. API ↔ PostgreSQL (tenant context set per transaction; RLS enforced).
3. AI Gateway ↔ text/image providers (external processing of prompts and brand context).
4. Execution gate ↔ publishing/ad platforms (external side effects; deferred for ads).
5. CI/CD ↔ GitHub Secrets.

## 2. Authentication and sessions

- Argon2id password hashing; opaque session token stored as SHA-256 hash only.
- Cookies: HttpOnly, Secure, SameSite=Lax; 14-day idle, 30-day absolute expiry; rotation on login.
- CSRF token required on every mutation; login rate-limited per IP/email; no account enumeration.
- MFA/SSO deferred; revisit if PRD requires.

## 3. Authorization matrix

| Action | Owner | Editor | Viewer |
|---|---|---|---|
| View organization content, calendar, leads | yes | yes | yes |
| Edit profile, products, content, creatives, landing pages | yes | yes | no |
| Approve content/landing publish | yes | yes | no |
| Approve ad activation or budget change | yes | no | no |
| Manage members/settings | yes | no | no |
| Change AI provider config | system admin only | no | no |

Every handler resolves `{org_id}` from the path, verifies membership and role, then applies RLS via `SET LOCAL app.current_tenant_id`.

## 4. Approval and financial safety (fail-closed)

1. Two distinct approval kinds: publishing and advertising/budget. One never implies the other.
2. Approval snapshots are append-only and hashed; approved data cannot be mutated in place. Edits bump `target_version`, supersede old approvals, and require new approval.
3. Ad approvals require exact `ceiling_amount`, `ceiling_currency`, USD display amount, and FX snapshot. Missing any field → no approval created.
4. Execution gate order: load approval → check status/expiry/superseded/version/hash → lock budget row → validate `spent + requested <= ceiling` → insert `external_actions` → provider call → append attempt log.
5. No automatic budget increases. Increase requires a new approval with a new ceiling.
6. Any validation failure stops before the external call: no publish, no spend.
7. Audit trail: `approval_requests`, `approval_snapshots`, `external_actions`, `external_action_attempts`, `audit_logs`.

## 5. AI gateway security

- Provider allowlist in `ai_provider_configs`; no arbitrary provider URLs from tenant input.
- Residency tags gate fallback: never fall back to a provider that violates policy.
- Prompt injection: tenant briefs and brand text are untrusted, delimited, and cannot set system instructions; no tool execution.
- Output validation for text and image metadata; safe error codes only; raw provider errors never returned.
- Cost caps per model/tenant; usage and cost recorded in `ai_usage_records`.
- Rate limits per tenant/provider/model; circuit breaker per provider.

## 6. Data protection and isolation

- Tenant-owned tables RLS-protected (see `03-database-design.md` §6). System tables admin-only.
- TLS/HSTS; security headers (`CSP`, `nosniff`, `Referrer-Policy: no-referrer`).
- Secrets only in GitHub Environments/host secret manager; no secrets in repo; rotate on exposure.
- Logs redacted: no passwords, cookies, tokens, full prompts, or provider keys.
- No production data in lower environments; encrypted backups with PITR and restore drill.
- Data export/deletion workflows deferred with legal review.

## 7. Supply chain and change control

- Pydantic validation, parameterized SQL, dependency scanning, SAST, required review.
- Branch protection on `main`; required checks; no auto-merge.
- PR #15 remains draft and unmerged until product-owner approval.

## 8. Compliance note

No compliance claim. Algerian data-protection rules and provider residency obligations require review before pilot data. FX display policy (source, rounding) also requires business confirmation.
