import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db, set_tenant_context
from .errors import Problem
from .models import Session as UserSession
from .models import TenantMembership, User
from .security import csrf_matches, hash_token, new_csrf_token, new_opaque_token, verify_password

SESSION_COOKIE = "ago_session"


def create_session(db: Session, user_id: uuid.UUID) -> tuple[UserSession, str, str]:
    settings = get_settings()
    now = datetime.now(UTC)
    raw_token, token_hash = new_opaque_token()
    csrf_token = new_csrf_token()
    session = UserSession(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        csrf_token_hash=hash_token(csrf_token),
        expires_at=now + timedelta(minutes=settings.session_ttl_minutes),
        absolute_expires_at=now + timedelta(days=settings.session_absolute_days),
    )
    db.add(session)
    db.flush()
    return session, raw_token, csrf_token


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not verify_password(user.password_hash, password):
        return None
    return user


def current_auth(
    request: Request, db: Session = Depends(get_db)
) -> tuple[User, UserSession]:
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        raise Problem(401, "Unauthorized", "A session cookie is required.", "unauthorized")
    now = datetime.now(UTC)
    session = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == hash_token(raw),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
            UserSession.absolute_expires_at > now,
        )
    )
    if session is None:
        raise Problem(401, "Unauthorized", "The session is invalid or expired.", "unauthorized")
    user = db.get(User, session.user_id)
    if user is None:
        raise Problem(401, "Unauthorized", "The session owner no longer exists.", "unauthorized")
    set_tenant_context(db, None, str(user.id))
    return user, session


def require_csrf(request: Request, auth: tuple[User, UserSession] = Depends(current_auth)) -> tuple[User, UserSession]:
    _, session = auth
    if not csrf_matches(request.headers.get("X-CSRF-Token"), session.csrf_token_hash):
        raise Problem(403, "Forbidden", "A valid CSRF token is required.", "csrf-failed")
    return auth


def current_user(auth: tuple[User, UserSession] = Depends(current_auth)) -> User:
    return auth[0]


def tenant_membership(
    org_id: uuid.UUID,
    auth: tuple[User, UserSession] = Depends(current_auth),
    db: Session = Depends(get_db),
) -> TenantMembership:
    user, _ = auth
    membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.tenant_id == org_id,
            TenantMembership.user_id == user.id,
            TenantMembership.status == "active",
        )
    )
    if membership is None:
        raise Problem(404, "Not found", "Organization not found.", "not-found")
    set_tenant_context(db, str(org_id), str(user.id))
    return membership


def tenant_db(
    membership: TenantMembership = Depends(tenant_membership),
    db: Session = Depends(get_db),
) -> Generator[Session, None, None]:
    yield db
