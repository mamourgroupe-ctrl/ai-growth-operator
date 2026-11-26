# Phase 2 — Approval Workflow Specification

**Status:** Proposed. No implementation authorized.

## Decision status

| Category | Summary |
|---|---|
| `OWNER_APPROVED` decisions | Mandatory human approval; owner-only final decision; AI never approves; no direct publishing; immutable audit evidence. |
| `OWNER_PROPOSED` decisions | D-01 owner-only final approval; D-02 internal landing pages only; D-03 DZD-only display; D-04 configurable quotas; D-05 study sectors; D-07 benchmark provider choice; D-08 comparison storage choice. Two-stage pipeline and version invalidation are `FROZEN`. |
| `BLOCKED` / `DEFERRED` | Final owner confirmation; `fr` review and SLA `BLOCKED`; lead functionality and publishing execution `DEFERRED`. |
| External dependencies | Owner authorization for issue/document amendments; human reviewer availability. |
| Confirmed boundary | Phase 2 approval is content-only. Ad-spend approval, FX snapshots, external paid-action authorization, outbox/reconciliation, external state machines and campaign launching are Phase 3 only. |
| Risks | Unintended auto-approval via edits; editor escalating role; stale approval reused. |

## 1. Roles and authority (D-01 `OWNER_PROPOSED`)

**Owner preliminary choice:** final approval is owner-only. Editors prepare and submit content; Arabic reviewers report linguistic findings; viewers are read-only. Validation (`block`/`warn`), Arabic review and human approval are separate gates. D-01 is `OWNER_PROPOSED` pending final confirmation; this preserves the existing owner-only baseline.

| Action | Owner | Editor | Arabic reviewer | Viewer |
|---|---|---|---|---|
| Create/edit draft | yes | yes | yes (if also editor) | no |
| Complete Arabic review | no* | yes if flagged | yes | no |
| Submit for approval | yes | yes | yes (if editor) | no |
| Final approve / reject / request changes | **yes** | no | no | no |
| Record `warn` override reason | yes | no | no | no |
| Clear `block` finding | no | no | no | no |

\*An owner may also be flagged as reviewer, but review status is not final approval. Arabic reviewer capability uses the existing `tenant_memberships.is_arabic_reviewer` field from `0001_initial` (`03-database-design.md §1`). No role may approve advertising spend or external actions in Phase 2.

## 2. State model

### Content version
`draft → validating → review_required (ar/ar-DZ) → reviewed → submitted → approved | rejected | changes_requested`

- `fr` content: `draft → validating → submitted → approved|...` unless owner enables `fr` review.
- Any material edit of an approved content item creates `version+1`; approval state of old version becomes `superseded`.
- Non-material metadata edit (e.g. internal label) does not invalidate approval; definition recorded in config.

### Approval request
`pending → approved | rejected | changes_requested`

- Request stores immutable `approval_snapshots` with version payload hash.
- Decision stores actor, timestamp, reason, request id, validation findings, Arabic review reference.

### Landing page (conditional scope)
`draft → approved_version` (internal preview/draft history only)

- Approval status lives on `landing_page_versions`; `landing_pages` holds only a non-authoritative pointer. No circular approved-version FK exists.
- Internal publish execution is `DEFERRED` to Phase 3 or later; no Phase 2 publishing endpoint. Changing approved blocks creates a new version and requires new approval.

## 3. API and data invariants

1. `POST /api/v1/approval/requests/{id}/decide` checks `tenant_membership.role == 'owner'` inside tenant context; editors/viewers receive 403. This path matches `05-api-contracts.md §2`.
2. No service, job, gateway, or migration path can set `approval_requests.status='approved'` except the owner decision service; this preserves the owner-only baseline under D-01 `OWNER_PROPOSED`.
3. Submitting requires: no `block` findings; Arabic review for `ar`/`ar-DZ`; asset ownership/scans validated; stable payload hash. `warn` overrides are owner-recorded and auditable; `block` findings cannot be cleared.
4. Idempotency key on the decide endpoint prevents double decision; repeated request returns original decision.
5. Rejection/change request must include non-empty reason; reason stored in audit.
6. `approval_requests` has no `snapshot_id` FK. `approval_snapshots.approval_request_id` points to the request; snapshots are append-only with unique `(tenant_id, approval_request_id, version)`.
7. `kind='content'` only in Phase 2. No ad-spend kind, FX ceiling, external action, outbox, reconciliation, publishing execution or lead state exists here.
8. If owner membership is removed after approval, approved content remains valid; no Phase 2 publish endpoint exists.

## 4. UI evidence shown to owner

- Full text/image preview with diff vs previous version.
- Validation findings with severity and evidence.
- Arabic review status/notes.
- Product/price snapshot used.
- Request id, submitter, submitted time.
- Decision buttons; reason field for reject/changes.

## 5. Audit events

| Event | Metadata |
|---|---|
| `content.version_created` | content id, version, hash, actor |
| `content.validation_completed` | version, overall, rule codes |
| `content.arabic_reviewed` | version, reviewer, status |
| `approval.requested` | request id, snapshot hash |
| `approval.decided` | decision, reason, actor, request id |
| `approval.superseded` | old version, new version |
| `landing.internally_published` | Phase 3+ `DEFERRED`; historical event only |

Audit rows are tenant-scoped except system events; no raw secrets or provider keys.

## 6. Negative tests required

- Editor/viewer/reviewer calling decide → 403.
- AI job or gateway calling decide service → denied by architecture boundary.
- Submit with blocking validation → 409.
- Submit `ar-DZ` without Arabic review → 409.
- Modify approved draft → new version + old approval superseded.
- Replay same idempotency key → same decision, no second audit row.
- Direct DB UPDATE of snapshot → rejected.

## 7. Open questions

- Final confirmation is pending for D-01; the preliminary choice preserves owner-only final approval, editor submission, reviewer findings and viewer read-only access. Do not treat a preliminary choice as final approval.
- Should `fr` require French-language review in pilot?
- Can an owner delegate final approval to another owner only, or to a trusted editor? Current documented decision: owner only, unchanged.
- What SLA triggers reminder notifications? Notifications are not in Phase 2 scope unless separately approved.
- Landing page approval is `OWNER_PROPOSED` for internal draft/version state only; publish execution is `DEFERRED`.
