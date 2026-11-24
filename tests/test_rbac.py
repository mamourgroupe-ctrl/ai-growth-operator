import uuid

from app.main import app
from fastapi.testclient import TestClient

PASSWORD = "CorrectHorseBatteryStaple42!"  # secret-scan-exempt: dummy test credential


def _register(prefix: str) -> tuple[TestClient, dict]:
    client = TestClient(app)
    response = client.post(
        "/auth/register",
        json={
            "email": f"{prefix}-{uuid.uuid4().hex[:10]}@example.com",
            "password": PASSWORD,
            "full_name": f"{prefix} owner",
            "organization_name": f"{prefix} org",
            "organization_slug": f"{prefix}-{uuid.uuid4().hex[:8]}",
        },
    )
    assert response.status_code == 201, response.text
    return client, response.json()


def _add_member(owner: TestClient, csrf: str, org_id: str, email: str, role: str, reviewer: bool = False):
    return owner.post(
        f"/organizations/{org_id}/members",
        headers={"X-CSRF-Token": csrf},
        json={"email": email, "role": role, "is_arabic_reviewer": reviewer},
    )


def test_owner_can_manage_members_and_create_organization() -> None:
    owner, body = _register("owner")
    csrf = body["csrf_token"]
    org_id = body["organization"]["id"]

    created = owner.post(
        "/organizations",
        headers={"X-CSRF-Token": csrf},
        json={"name": "Second org", "slug": f"second-{uuid.uuid4().hex[:8]}"},
    )
    assert created.status_code == 201, created.text
    assert created.json()["default_ui_locale"] == "ar"

    _, member_body = _register("member")
    member_email = member_body["user"]["email"]
    added = _add_member(owner, csrf, org_id, member_email, "editor", reviewer=True)
    assert added.status_code == 201, added.text
    assert added.json()["role"] == "editor"
    assert added.json()["is_arabic_reviewer"] is True

    members = owner.get(f"/organizations/{org_id}/members")
    assert members.status_code == 200
    assert any(row["role"] == "editor" for row in members.json())


def test_editor_and_viewer_cannot_approve_or_manage() -> None:
    owner, owner_body = _register("root")
    _, editor_body = _register("editor")
    _, viewer_body = _register("viewer")
    org_id = owner_body["organization"]["id"]
    csrf = owner_body["csrf_token"]

    assert _add_member(owner, csrf, org_id, editor_body["user"]["email"], "editor").status_code == 201
    assert _add_member(owner, csrf, org_id, viewer_body["user"]["email"], "viewer", True).status_code == 201

    editor = TestClient(app)
    assert editor.post(
        "/auth/login",
        json={"email": editor_body["user"]["email"], "password": PASSWORD},
    ).status_code == 200
    editor_csrf = editor.get("/auth/me").status_code  # sanity: authenticated

    assert editor.get(f"/organizations/{org_id}").status_code == 200
    blocked_add = _add_member(editor, "forged", org_id, viewer_body["user"]["email"], "owner")
    assert blocked_add.status_code == 403
    blocked_patch = editor.patch(
        f"/organizations/{org_id}",
        headers={"X-CSRF-Token": "forged"},
        json={"name": "Hacked"},
    )
    assert blocked_patch.status_code == 403
    assert editor_csrf == 200

    viewer = TestClient(app)
    viewer.post(
        "/auth/login",
        json={"email": viewer_body["user"]["email"], "password": PASSWORD},
    )
    assert viewer.get(f"/organizations/{org_id}").status_code == 200
    assert viewer.post(
        f"/organizations/{org_id}/members",
        json={"email": viewer_body["user"]["email"], "role": "owner"},
    ).status_code == 403

    members = owner.get(f"/organizations/{org_id}/members").json()
    viewer_row = next(row for row in members if row["role"] == "viewer")
    assert viewer_row["is_arabic_reviewer"] is False


def test_cross_tenant_access_is_rejected() -> None:
    _, org_a = _register("tenanta")
    client_b, org_b = _register("tenantb")

    assert client_b.get(f"/organizations/{org_a['organization']['id']}").status_code == 404
    assert client_b.get(f"/organizations/{org_b['organization']['id']}").status_code == 200
