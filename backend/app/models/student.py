"""
Student Models and Pydantic v2 Schemas
Defines domain models, validation schemas, and database mappings for Student records.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional
from bson import ObjectId
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)
from app.models.user import PyObjectId


class StudentBase(BaseModel):
    """Base schema with shared student attributes."""
    student_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique institutional student identifier",
        examples=["STU-2024-089"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Student's full legal name",
        examples=["Arun Kumar"],
    )
    email: EmailStr = Field(
        ...,
        description="Unique student email address",
        examples=["arun.kumar@student.edumanage.edu"],
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Contact phone number",
        examples=["+1 (555) 234-5678"],
    )
    date_of_birth: Optional[str] = Field(
        default=None,
        description="Date of birth (YYYY-MM-DD)",
        examples=["2004-05-15"],
    )
    gender: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Gender identity",
        examples=["male"],
    )
    department: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Academic department / Major",
        examples=["Computer Science & Engineering"],
    )
    year: int = Field(
        ...,
        description="Academic year (e.g., 1 to 6)",
        examples=[3],
    )
    section: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Class section / cohort",
        examples=["A"],
    )
    roll_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique academic roll number",
        examples=["CS-22-089"],
    )
    address: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Residential address",
        examples=["45 University Ave, Boston, MA"],
    )
    is_active: bool = Field(
        default=True,
        description="Student enrollment status (active/inactive)",
        examples=[True],
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        """Normalizes email to lowercase and strips outer whitespace."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("student_id", "full_name", "roll_number", "department")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that required strings are non-empty after stripping."""
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Field cannot be empty or solely whitespace.")
            return v_stripped
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validates that academic year is a reasonable value (1-6 or 1900-2100)."""
        if not ((1 <= v <= 6) or (1900 <= v <= 2100)):
            raise ValueError("Year must be a valid academic level (1-6) or graduation year (1900-2100).")
        return v


class StudentCreate(StudentBase):
    """Request schema for creating a new student record."""
    pass


class StudentUpdate(BaseModel):
    """Request schema for updating student attributes (all fields optional)."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[str] = None
    gender: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = None
    section: Optional[str] = Field(None, max_length=20)
    roll_number: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("full_name", "roll_number", "department")
    @classmethod
    def validate_non_empty_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Field cannot be empty or solely whitespace.")
            return v_stripped
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if not ((1 <= v <= 6) or (1900 <= v <= 2100)):
                raise ValueError("Year must be a valid academic level (1-6) or graduation year (1900-2100).")
        return v


class StudentInDB(StudentBase):
    """
    Database model representing the document stored in MongoDB students collection.
    """
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of student record creation",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last record update",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class StudentResponse(StudentBase):
    """
    Public response schema for student records.
    Serializes _id to id safely.
    """
    id: PyObjectId = Field(
        default_factory=ObjectId,
        validation_alias=AliasChoices("_id", "id"),
        description="Student unique database identifier",
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class StudentPaginationResponse(BaseModel):
    """Paginated list response schema for Student queries."""
    items: List[StudentResponse] = Field(..., description="List of student records for current page")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page limit")
    total: int = Field(..., ge=0, description="Total number of matching student records")
    pages: int = Field(..., ge=0, description="Total number of pages")
