import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import current_user, require_csrf, require_owner, tenant_membership
from ..db import get_db, set_tenant_context
from ..errors import Problem
from ..models import Tenant, TenantMembership, User
from ..schemas import (
    MemberCreate,
    MembershipOut,
    MemberUpdate,
    OrganizationCreate,
    OrganizationOut,
    OrganizationUpdate,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _slug(raw: str | None) -> str:
    if not raw:
        return f"org-{uuid.uuid4().hex[:12]}"
    candidate = "-".join(raw.strip().lower().replace("_", "-").split())
    return candidate or f"org-{uuid.uuid4().hex[:12]}"


@router.get("")
def list_organizations(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(
        select(Tenant).join(TenantMembership).where(
            TenantMembership.user_id == user.id,
            TenantMembership.status == "active",
            Tenant.deleted_at.is_(None),
        )
    ).all()
    return [OrganizationOut.model_validate(row).model_dump(mode="json") for row in rows]


@router.post("", response_model=OrganizationOut, status_code=201)
def create_organization(
    payload: OrganizationCreate,
    response: Response,
    user: User = Depends(current_user),
    _csrf=Depends(require_csrf),
    db: Session = Depends(get_db),
) -> OrganizationOut:
    tenant_id = uuid.uuid4()
    try:
        set_tenant_context(db, str(tenant_id), str(user.id))
        tenant = Tenant(
            id=tenant_id,
            name=payload.name.strip(),
            slug=_slug(payload.slug),
            display_currencies={"DZD": True, "USD": True},
            supported_ui_locales={"ar": True, "fr": True},
            default_ui_locale="ar",
            default_content_style="msa",
        )
        db.add(tenant)
        db.flush()
        db.add(TenantMembership(tenant_id=tenant_id, user_id=user.id, role="owner", status="active"))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Problem(409, "Conflict", "Organization slug already exists.", "conflict") from exc
    return OrganizationOut.model_validate(tenant)


@router.get("/{org_id}")
def get_organization(
    org_id: uuid.UUID,
    _membership=Depends(tenant_membership),
    db: Session = Depends(get_db),
) -> dict:
    tenant = db.get(Tenant, org_id)
    if tenant is None:
        raise Problem(404, "Not found", "Organization not found.", "not-found")
    return OrganizationOut.model_validate(tenant).model_dump(mode="json")


@router.patch("/{org_id}")
def update_organization(
    org_id: uuid.UUID,
    payload: OrganizationUpdate,
    _owner=Depends(require_owner),
    _csrf=Depends(require_csrf),
    db: Session = Depends(get_db),
) -> dict:
    tenant = db.get(Tenant, org_id)
    if tenant is None:
        raise Problem(404, "Not found", "Organization not found.", "not-found")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(tenant, key, value)
    db.commit()
    return OrganizationOut.model_validate(tenant).model_dump(mode="json")


@router.get("/{org_id}/members")
def list_members(
    org_id: uuid.UUID,
    _membership=Depends(tenant_membership),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.scalars(select(TenantMembership).where(TenantMembership.tenant_id == org_id)).all()
    return [MembershipOut.model_validate(row).model_dump(mode="json") for row in rows]


@router.post("/{org_id}/members", response_model=MembershipOut, status_code=201)
def add_member(
    org_id: uuid.UUID,
    payload: MemberCreate,
    owner_membership=Depends(require_owner),
    _csrf=Depends(require_csrf),
    db: Session = Depends(get_db),
) -> TenantMembership:
    user = db.scalar(select(User).where(User.email == str(payload.email).strip().lower()))
    if user is None:
        raise Problem(404, "Not found", "User not found.", "not-found")
    reviewer = payload.is_arabic_reviewer if payload.role in ("owner", "editor") else False
    membership = TenantMembership(
        tenant_id=org_id,
        user_id=user.id,
        role=payload.role,
        is_arabic_reviewer=reviewer,
        status="active",
    )
    db.add(membership)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Problem(409, "Conflict", "Membership already exists.", "conflict") from exc
    set_tenant_context(db, str(org_id), str(owner_membership.user_id))
    db.refresh(membership)
    return membership


@router.patch("/{org_id}/members/{user_id}")
def update_member(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: MemberUpdate,
    _owner=Depends(require_owner),
    _csrf=Depends(require_csrf),
    db: Session = Depends(get_db),
) -> dict:
    membership = db.get(TenantMembership, (org_id, user_id))
    if membership is None:
        raise Problem(404, "Not found", "Membership not found.", "not-found")
    updates = payload.model_dump(exclude_unset=True)
    if "is_arabic_reviewer" in updates and membership.role == "viewer":
        updates["is_arabic_reviewer"] = False
    if "role" in updates and updates["role"] == "viewer":
        membership.is_arabic_reviewer = False
    for key, value in updates.items():
        setattr(membership, key, value)
    db.commit()
    return MembershipOut.model_validate(membership).model_dump(mode="json")
