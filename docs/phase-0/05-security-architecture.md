# Phase 0 — Security Architecture (final acceptance draft)

**Status:** Corrected for final approval. No controls implemented in Phase 0.

## 1. Trust boundaries

Browser ↔ API; API ↔ PostgreSQL (RLS + tenant context); AI Gateway ↔ providers; execution dispatcher ↔ external platforms (deferred for social/ads); CI/CD ↔ GitHub Secrets.

## 2. Authentication

Argon2id passwords; opaque session token stored only as SHA-256 hash; HttpOnly/Secure/SameSite=Lax cookies; idle 14d / absolute 30d; rotation on login; CSRF token on every mutation; login rate limit; no account enumeration. MFA/SSO deferred.

## 3. RBAC and approval bypass prevention

| Action | Owner | Editor (incl. Arabic reviewer) | Viewer |
|---|---|---|---|
| Read organization data | yes | yes | yes |
| Prepare content/products/landing pages | yes | yes | no |
| Submit for Arabic review / submit for approval | yes | yes | no |
| Decide Arabic quality review | yes | yes if `is_arabic_reviewer` | no |
| **Final approval of any request** | **yes (only)** | **no** | no |
| Trigger publish/execute after approval | yes | yes | no |
| Manage members/settings | yes | no | no |
| Configure AI providers / FX snapshots | system admin | no | no |

Enforcement:
- Central authorization dependency on every route; role is read from DB membership in the same tenant context, never from client payload/token claim.
- `/approvals/{id}/decide` hard-checks `role='owner'`. Forged `approval_id`, UI-hidden buttons, or direct API calls cannot grant approval authority.
- Publish/execute handlers independently re-validate approval status, owner decision, version, hash, expiry, Arabic review, and tenant match before writing an outbox row.
- RLS is a second boundary; viewer cross-tenant or cross-role attempts return `403`/`404`.

## 4. Approval and financial safety

- Distinct approval kinds; budget changes/content edits supersede prior approvals; snapshots immutable and hashed.
- Exact ceiling + immutable FX snapshot required for any ad-kind approval (deferred execution, contract fixed).
- Transactional outbox ensures the action intent and approval authorization commit together; no external call before commit.
- Deterministic provider idempotency key stored per `external_actions` row and reused across retries; replay is a no-op.
- State machine includes `uncertain`: on ambiguous provider result, automatic retry is forbidden; reconciliation resolves using provider idempotency key/reference.
- No automatic budget increases; `spent + requested <= ceiling` checked under row lock before dispatch.
- Every attempt, decision, outbox publish, and reconciliation result is appended to immutable logs.

## 5. Arabic quality control

`ar`/`ar-DZ` content cannot enter approval until an `arabic_reviews` row is `approved` by a flagged editor reviewer. Review covers MSA grammar, Darija authenticity, brand voice, cultural fit, and factual claims. Reviewer identity and notes are audited. Viewer can never review.

## 6. AI gateway security

Provider allowlist; residency-gated fallback; prompts/brands treated as untrusted; no tool execution; output validation; safe error codes; cost caps and rate limits; usage/cost recorded. No client-chosen provider URLs.

## 7. Data protection and operations

TLS/HSTS; CSP/no-sniff/referrer headers; redacted logs (no secrets, tokens, full prompts); secrets only in GitHub Environments; encrypted backups with PITR and restore drill; no production data in lower environments. FX source remains an unresolved configuration decision and must be selected before financial approvals are activated.

## 8. Supply chain

Pydantic validation, parameterized SQL, dependency scanning, SAST, required review, branch protection on `main`, no auto-merge. PR #15 remains draft and unmerged.

## 9. Compliance

No compliance claim. Algerian data-protection and provider residency review required before pilot.
