"""
User Models and Pydantic v2 Schemas
Defines domain models, validation schemas, and database mappings for Users.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Optional
from bson import ObjectId
from pydantic import (
    AliasChoices,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    PlainSerializer,
    WithJsonSchema,
    field_validator,
)


def validate_object_id(v: Any) -> ObjectId:
    """Validates and converts input to BSON ObjectId."""
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError(f"Invalid ObjectId: {v}")


# Custom PyObjectId type for BSON ObjectId compatibility with Pydantic v2
PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str, when_used="json"),
    WithJsonSchema({"type": "string", "example": "64b1f2c3d4e5f6a7b8c9d0e1"}, mode="serialization"),
    WithJsonSchema({"type": "string", "example": "64b1f2c3d4e5f6a7b8c9d0e1"}, mode="validation"),
]


class UserRole(str, Enum):
    """Permitted user roles in the EduManage platform."""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class UserBase(BaseModel):
    """Base schema with shared user attributes."""
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's full name",
        examples=["Alex Johnson"],
    )
    email: EmailStr = Field(
        ...,
        description="User's unique email address",
        examples=["alex.johnson@edumanage.com"],
    )
    role: UserRole = Field(
        default=UserRole.STUDENT,
        description="User role (admin, teacher, or student)",
        examples=[UserRole.STUDENT],
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active",
        examples=[True],
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        """Normalizes email to lowercase and strips outer whitespace."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validates that full_name is non-empty after stripping whitespace."""
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Full name cannot be empty or solely whitespace.")
        return v_stripped


class UserCreate(UserBase):
    """Request schema for creating/registering a new user."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plaintext user password (minimum 8 characters)",
        examples=["SecureP@ssw0rd123"],
    )


class UserUpdate(BaseModel):
    """Request schema for updating existing user attributes."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Full name cannot be empty or solely whitespace.")
            return v_stripped
        return v


class UserInDB(BaseModel):
    """
    Database model representing the document stored in MongoDB.
    Contains hashed_password and BSON _id.
    """
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    full_name: str
    email: EmailStr
    hashed_password: str = Field(..., description="Argon2 hashed password")
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of account creation",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class UserResponse(BaseModel):
    """
    Public response schema for returning user details safely.
    Strictly excludes sensitive attributes like hashed_password.
    """
    id: PyObjectId = Field(
        default_factory=ObjectId,
        validation_alias=AliasChoices("_id", "id"),
        description="User identifier",
    )
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
