# Phase 1 — Branch protection on `main`

Status: **BLOCKED** — not yet applied.

Required settings for `main`:

- Required checks: `lint`, `test`, `security`.
- Strict status checks (branch must be up to date before merge).
- Require a pull request with at least 1 approving review.
- Dismiss stale reviews.
- Require conversation resolution.
- Block force pushes and branch deletion.
- Enforce for administrators.

Attempt recorded on 2026-11-24: `gh api -X PUT repos/mamourgroupe-ctrl/ai-growth-operator/branches/main/protection` returned `403 Resource not accessible by integration` despite repository admin permission. The available GitHub token scope does not include branch-protection administration.

Resolution required: a product owner/repository admin with the `administration:write` scope must apply these settings, then close issue #14. Until then, **do not merge any PR into `main`**.
