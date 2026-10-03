"""
Authentication & Token Schemas
Defines request and response schemas for login and JWT token representations.
"""

from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Request payload schema for user authentication."""
    email: EmailStr = Field(
        ...,
        description="User's registered email address",
        examples=["user@edumanage.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Plaintext password",
        examples=["SecureP@ssw0rd123"],
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        """Normalizes email to lowercase and strips outer whitespace."""
        if isinstance(v, str):
            return v.strip().lower()
        return v


class Token(BaseModel):
    """Response payload schema for successful authentication."""
    access_token: str = Field(
        ...,
        description="Signed JWT access token",
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (bearer)",
    )


class TokenPayload(BaseModel):
    """Internal schema for decoded JWT payload contents."""
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
