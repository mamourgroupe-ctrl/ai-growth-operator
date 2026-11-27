# Phase 1 — Branch protection on `main`

Status: **BLOCKED — requires repository administrator action**. Issue #14 stays OPEN.

Required settings for `main`:

- Required status checks: `lint`, `test`, `security` (exact job names from `.github/workflows/ci.yml`).
- Require branches to be up to date before merging (strict status checks).
- Require a pull request with at least 1 approving review.
- Dismiss stale approvals when new commits are pushed.
- Require all conversations to be resolved before merging.
- Block force pushes and branch deletion.
- Apply the rules to administrators too.
- Do not allow merge until the required checks succeed on the PR head commit.

## Why this is not applied yet

The recorded attempt on 2026-11-24 used:

```text
gh api -X PUT repos/mamourgroupe-ctrl/ai-growth-operator/branches/main/protection
```

It returned `403 Resource not accessible by integration`: the available token lacks repository-administration scope. No further attempt was made during remediation, and no permission boundary was bypassed.

## Exact instructions for the repository owner

### Option A — GitHub UI

1. Open `Settings` → `Branches` → `Branch protection rules` → `Add branch protection rule` (or `Rules` → `New ruleset`).
2. Branch name pattern / target: `main`.
3. Enable `Require a pull request before merging`; set required approvals to `1`.
4. Enable `Dismiss stale pull request approvals when new commits are pushed`.
5. Enable `Require status checks to pass before merging`, then add exactly `lint`, `test`, `security`.
6. Enable `Require branches to be up to date before merging`.
7. Enable `Require conversation resolution before merging`.
8. Enable `Do not allow bypassing the above settings` / `Include administrators`.
9. Disable `Allow force pushes` and `Allow deletions` for `main`.
10. Save the rule, then verify on PR #15 that the three checks are reported as required.

### Option B — GitHub CLI with an administrator token

The owner must run this from an account with `administration:write` on the repository. Replace only the placeholder path values if the repository is renamed; do not paste real credentials into chat or logs.

```bash
gh api -X PUT repos/mamourgroupe-ctrl/ai-growth-operator/branches/main/protection \
  -f required_status_checks[strict]=true \
  -f 'required_status_checks[contexts][]=lint' \
  -f 'required_status_checks[contexts][]=test' \
  -f 'required_status_checks[contexts][]=security' \
  -f 'enforce_admins=true' \
  -f 'required_pull_request_reviews[required_approving_review_count]=1' \
  -f 'required_pull_request_reviews[dismiss_stale_reviews]=true' \
  -f 'restrictions=null' \
  -f 'allow_force_pushes=false' \
  -f 'allow_deletions=false' \
  -f 'required_conversation_resolution=true'
```

Verification the owner should run afterwards:

```bash
gh api repos/mamourgroupe-ctrl/ai-growth-operator/branches/main/protection \
  --jq '{strict: .required_status_checks.strict, checks: .required_status_checks.contexts,
         approvals: .required_pull_request_reviews.required_approving_review_count,
         enforce_admins: .enforce_admins.enabled}'
```

Expected: `strict=true`, `checks=["lint","test","security"]`, `approvals=1`, `enforce_admins=true`.

## Acceptance rule

A documentation file is **not** proof that GitHub settings were applied. Issue #14 may be closed only after the verification command above returns the expected values, or after the owner confirms the same in the GitHub UI. Until then, **do not merge any PR into `main`**, including draft PR #15.
