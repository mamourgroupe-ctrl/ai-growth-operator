# Phase 2 — Approval Workflow Specification

**Status:** Proposed. No implementation authorized.

## Decision status

| Category | Summary |
|---|---|
| Approved decisions | Mandatory human approval; owner-only final decision; AI never approves; no direct publishing; immutable audit evidence. |
| Proposed decisions | Two-stage pipeline (Arabic review → owner decision), version-based approval invalidation, explicit request states. |
| Open questions | Whether Arabic review is required for `fr`; delegation when no owner exists; retention; approval SLA. |
| External dependencies | Owner roadmap decision on #23; human reviewer availability. |
| Risks | Unintended auto-approval via edits; editor escalating role; stale approval reused. |

## 1. Roles and authority

| Action | owner | editor | Arabic reviewer | viewer |
|---|---|---|---|---|
| Create/edit draft | yes | yes | yes (if editor) | no |
| Complete Arabic review | no* | yes if flagged | yes | no |
| Submit for approval | yes | yes | yes if editor | no |
| Approve / reject / request changes | **yes** | no | no | no |
| Override validation block | yes (documented) | no | no | no |

\*Owner may also be flagged as reviewer but cannot use review status as final approval.

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

### Landing page
`draft → approved_version → internally_published`

- Internal publish does not create external side effects. Changing approved blocks creates a new version and requires new approval.

## 3. API and data invariants

1. `POST /approval/requests/{id}/decide` checks `tenant_membership.role == 'owner'` inside tenant context; editors/viewers receive 403.
2. No service, job, gateway, or migration path can set `approval_requests.status='approved'` except the owner decision service.
3. Submitting requires: no `block` findings; Arabic review for `ar`/`ar-DZ`; asset ownership/scans validated; stable payload hash.
4. Idempotency key on decide endpoint prevents double decision; repeated request returns original decision.
5. Rejection/change request must include non-empty reason; reason stored in audit.
6. Approval snapshot append-only; UPDATE/DELETE rejected by DB constraint/trigger + repository design.
7. If owner membership removed after approval, approved content remains valid but internal publish of new versions is blocked until an owner exists.

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
| `landing.internally_published` | page id, approved version, actor |

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

- Should `fr` require French-language review in pilot?
- Can an owner delegate approval to another owner only, or to a trusted editor? Current decision: owner only.
- What SLA triggers reminder notifications? Notifications not in Phase 2 scope unless separately approved.
