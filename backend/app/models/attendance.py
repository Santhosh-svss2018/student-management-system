"""
Attendance Models and Pydantic v2 Schemas
Defines domain models, validation schemas, and database mappings for Attendance records.
"""

from datetime import date as dt_date, datetime, timezone
from enum import Enum
import re
from typing import Any, List, Optional
from bson import ObjectId
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)
from app.models.user import PyObjectId


class AttendanceStatus(str, Enum):
    """Supported attendance status values."""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AttendanceBase(BaseModel):
    """Base schema with shared attendance attributes."""
    student_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique institutional student identifier",
        examples=["STU-2024-001"],
    )
    date: str = Field(
        ...,
        description="Session date formatted as YYYY-MM-DD",
        examples=["2026-10-03"],
    )
    status: AttendanceStatus = Field(
        ...,
        description="Attendance status (present, absent, late, excused)",
        examples=["present"],
    )
    remarks: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional teacher/admin notes or remarks",
        examples=["Present on time"],
    )

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v: str) -> str:
        """Ensures student_id is non-empty after stripping whitespace."""
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("student_id cannot be empty or solely whitespace.")
            return v_stripped
        return v

    @field_validator("date", mode="before")
    @classmethod
    def validate_and_normalize_date(cls, v: Any) -> str:
        """Validates that date is in YYYY-MM-DD format."""
        if isinstance(v, dt_date):
            return v.isoformat()
        if isinstance(v, str):
            v_stripped = v.strip()
            # Validate YYYY-MM-DD format
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", v_stripped):
                raise ValueError("Date must be formatted as YYYY-MM-DD (e.g. 2026-10-03).")
            # Validate that it is a real calendar date
            try:
                datetime.strptime(v_stripped, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"'{v_stripped}' is not a valid calendar date.")
            return v_stripped
        raise ValueError("Invalid date value provided.")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> Any:
        """Normalizes status string to lowercase for Enum matching."""
        if isinstance(v, str):
            return v.strip().lower()
        return v


class AttendanceCreate(AttendanceBase):
    """Request schema for recording new attendance."""
    attendance_id: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Optional custom attendance identifier",
        examples=["ATT-20261003-001"],
    )


class AttendanceUpdate(BaseModel):
    """Request schema for modifying an existing attendance record."""
    status: Optional[AttendanceStatus] = None
    remarks: Optional[str] = Field(default=None, max_length=255)
    date: Optional[str] = None

    @field_validator("date", mode="before")
    @classmethod
    def validate_and_normalize_date(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, dt_date):
            return v.isoformat()
        if isinstance(v, str):
            v_stripped = v.strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", v_stripped):
                raise ValueError("Date must be formatted as YYYY-MM-DD (e.g. 2026-10-03).")
            try:
                datetime.strptime(v_stripped, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"'{v_stripped}' is not a valid calendar date.")
            return v_stripped
        raise ValueError("Invalid date value provided.")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class AttendanceInDB(AttendanceBase):
    """
    Database model representing the document stored in MongoDB attendance collection.
    """
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    attendance_id: str = Field(
        ...,
        description="Unique attendance identifier",
        examples=["ATT-20261003-001"],
    )
    marked_by: str = Field(
        ...,
        description="Email or user ID of the staff member who marked attendance",
        examples=["teacher@edumanage.edu"],
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of attendance creation",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last record update",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class AttendanceResponse(AttendanceBase):
    """
    Public response schema for attendance records.
    """
    id: PyObjectId = Field(
        default_factory=ObjectId,
        validation_alias=AliasChoices("_id", "id"),
        description="Attendance unique database identifier",
    )
    attendance_id: str
    marked_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class AttendancePaginationResponse(BaseModel):
    """Paginated list response schema for Attendance queries."""
    items: List[AttendanceResponse] = Field(..., description="List of attendance records for current page")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page limit")
    total: int = Field(..., ge=0, description="Total number of matching attendance records")
    pages: int = Field(..., ge=0, description="Total number of pages")


class AttendanceSummaryResponse(BaseModel):
    """Consolidated summary metrics schema for student attendance."""
    student_id: Optional[str] = Field(default=None, description="Student institutional identifier")
    total_days: int = Field(..., ge=0, description="Total recorded attendance sessions")
    present_days: int = Field(..., ge=0, description="Total present sessions")
    absent_days: int = Field(..., ge=0, description="Total absent sessions")
    late_days: int = Field(..., ge=0, description="Total late sessions")
    excused_days: int = Field(..., ge=0, description="Total excused sessions")
    attendance_percentage: float = Field(..., ge=0.0, le=100.0, description="Calculated attendance percentage")
