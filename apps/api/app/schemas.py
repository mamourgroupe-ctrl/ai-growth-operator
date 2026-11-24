import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=1, max_length=200)
    organization_name: str = Field(min_length=1, max_length=200)
    organization_slug: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str

    model_config = {"from_attributes": True}


class OrganizationOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    base_currency: str
    display_currencies: dict
    default_ui_locale: str
    supported_ui_locales: dict
    default_content_style: str
    timezone: str
    plan_code: str

    model_config = {"from_attributes": True}


class AuthOut(BaseModel):
    user: UserOut
    csrf_token: str
    organization: OrganizationOut | None = None


class MembershipOut(BaseModel):
    tenant_id: uuid.UUID
    role: str
    is_arabic_reviewer: bool
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
