"""Schema auth — persis kontrak api-spec.yaml (RegisterRequest, LoginRequest,
AuthResponse, User).

Response ditulis eksplisit field per field; model User berisi password_hash
sehingga TIDAK memakai from_attributes pada model itu (coding-standard §3.5).
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import User


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=80)
    role: Literal["TEACHER", "STUDENT"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Serializer eksplisit — password_hash tidak pernah keluar (FR-AUTH-02)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    display_name: str
    role: str
    organization_id: UUID
    created_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserOut":
        return cls(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            organization_id=user.organization_id,
            created_at=user.created_at,
        )


class AuthResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserOut
