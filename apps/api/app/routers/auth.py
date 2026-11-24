import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import (
    SESSION_COOKIE,
    authenticate_user,
    create_session,
    current_user,
    require_csrf,
)
from ..config import get_settings
from ..db import get_db, set_tenant_context
from ..errors import Problem
from ..models import Tenant, TenantMembership, User
from ..schemas import AuthOut, LoginRequest, MembershipOut, OrganizationOut, RegisterRequest, UserOut
from ..security import hash_password

router = APIRouter(tags=["auth"])


def _set_session_cookie(response: Response, raw_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        raw_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.session_ttl_minutes * 60,
        path="/",
    )


def _slug(raw: str | None) -> str:
    if not raw:
        return f"org-{uuid.uuid4().hex[:12]}"
    candidate = "-".join(raw.strip().lower().replace("_", "-").split())
    return candidate or f"org-{uuid.uuid4().hex[:12]}"


@router.post("/auth/register", response_model=AuthOut, status_code=201)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> AuthOut:
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    email = str(payload.email).strip().lower()
    try:
        set_tenant_context(db, str(tenant_id), str(user_id))
        user = User(
            id=user_id,
            email=email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
        )
        db.add(user)
        db.flush()

        tenant = Tenant(
            id=tenant_id,
            name=payload.organization_name.strip(),
            slug=_slug(payload.organization_slug),
            display_currencies={"DZD": True, "USD": True},
            supported_ui_locales={"ar": True, "fr": True},
            default_ui_locale="ar",
            default_content_style="msa",
        )
        db.add(tenant)
        db.flush()
        db.add(TenantMembership(tenant_id=tenant_id, user_id=user_id, role="owner", status="active"))
        _, raw_token, csrf_token = create_session(db, user_id)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Problem(409, "Conflict", "Email or organization slug already exists.", "conflict") from exc

    _set_session_cookie(response, raw_token)
    return AuthOut(
        user=UserOut.model_validate(user),
        csrf_token=csrf_token,
        organization=OrganizationOut.model_validate(tenant),
    )


@router.post("/auth/login", response_model=AuthOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthOut:
    user = authenticate_user(db, str(payload.email), payload.password)
    if user is None:
        raise Problem(401, "Unauthorized", "Invalid email or password.", "invalid-credentials")
    _, raw_token, csrf_token = create_session(db, user.id)
    db.commit()
    _set_session_cookie(response, raw_token)
    return AuthOut(user=UserOut.model_validate(user), csrf_token=csrf_token)


@router.post("/auth/logout", status_code=204)
def logout(
    response: Response,
    auth=Depends(require_csrf),
    db: Session = Depends(get_db),
) -> Response:
    _, session = auth
    session.revoked_at = datetime.now(UTC)
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.status_code = 204
    return response


@router.get("/auth/me")
def me(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    memberships = db.scalars(
        select(TenantMembership).where(
            TenantMembership.user_id == user.id,
            TenantMembership.status == "active",
        )
    ).all()
    return {
        "user": UserOut.model_validate(user).model_dump(mode="json"),
        "memberships": [MembershipOut.model_validate(row).model_dump(mode="json") for row in memberships],
    }
