"""
Marks & Grades Domain Models and Pydantic v2 Schemas
Defines domain models, validation schemas, grade calculations, and database mappings for Marks records.
"""

from datetime import datetime, timezone
from enum import Enum
import re
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from app.models.user import PyObjectId


class ExamType(str, Enum):
    """Controlled assessment / exam types."""
    INTERNAL_1 = "internal_1"
    INTERNAL_2 = "internal_2"
    MODEL = "model"
    SEMESTER = "semester"
    ASSIGNMENT = "assignment"


def calculate_percentage(marks_obtained: float, max_marks: float) -> float:
    """
    Calculates percentage rounded to 2 decimal places.
    Raises ValueError if max_marks <= 0.
    """
    if max_marks <= 0:
        raise ValueError("max_marks must be greater than 0")
    return round((marks_obtained / max_marks) * 100.0, 2)


def calculate_grade(percentage: float) -> str:
    """
    Computes letter grade from percentage using the standardized grading policy:
    90–100   -> A+
    80–89.99 -> A
    70–79.99 -> B
    60–69.99 -> C
    50–59.99 -> D
    40–49.99 -> E
    Below 40 -> F
    """
    if percentage >= 90.0:
        return "A+"
    elif percentage >= 80.0:
        return "A"
    elif percentage >= 70.0:
        return "B"
    elif percentage >= 60.0:
        return "C"
    elif percentage >= 50.0:
        return "D"
    elif percentage >= 40.0:
        return "E"
    else:
        return "F"


class MarksBase(BaseModel):
    """Base schema with shared attributes across Marks operations."""
    student_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique institutional student identifier",
        examples=["STU-2024-001"],
    )
    subject_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Course/Subject code",
        examples=["CS-301"],
    )
    subject_name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Course/Subject name",
        examples=["Design & Analysis of Algorithms"],
    )
    semester: int = Field(
        ...,
        ge=1,
        le=8,
        description="Academic semester number (1 to 8)",
        examples=[5],
    )
    exam_type: ExamType = Field(
        ...,
        description="Assessment / Exam type",
        examples=["semester"],
    )
    marks_obtained: float = Field(
        ...,
        ge=0.0,
        description="Score achieved by the student (must be >= 0)",
        examples=[85.0],
    )
    max_marks: float = Field(
        ...,
        gt=0.0,
        description="Maximum achievable marks for this assessment (must be > 0)",
        examples=[100.0],
    )
    academic_year: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="Academic year (e.g. 2024-2025)",
        examples=["2024-2025"],
    )
    remarks: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional teacher/evaluator notes",
        examples=["Excellent performance in algorithms"],
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

    @field_validator("subject_code")
    @classmethod
    def validate_subject_code(cls, v: str) -> str:
        """Ensures subject_code is uppercase and non-empty."""
        if isinstance(v, str):
            v_stripped = v.strip().upper()
            if not v_stripped:
                raise ValueError("subject_code cannot be empty.")
            return v_stripped
        return v

    @field_validator("subject_name")
    @classmethod
    def validate_subject_name(cls, v: str) -> str:
        """Ensures subject_name is non-empty after stripping whitespace."""
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("subject_name cannot be empty.")
            return v_stripped
        return v

    @field_validator("exam_type", mode="before")
    @classmethod
    def normalize_exam_type(cls, v: Any) -> Any:
        """Normalizes exam_type string to lowercase."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("academic_year")
    @classmethod
    def validate_academic_year(cls, v: str) -> str:
        """Validates academic year string format (e.g. 2024-2025 or 2024)."""
        if isinstance(v, str):
            v_stripped = v.strip()
            if not re.match(r"^\d{4}(-\d{2,4})?$", v_stripped):
                raise ValueError("academic_year must be formatted as YYYY or YYYY-YYYY (e.g. '2024-2025').")
            return v_stripped
        return v

    @model_validator(mode="after")
    def validate_marks_within_limit(self) -> "MarksBase":
        """Ensures marks_obtained does not exceed max_marks."""
        if self.marks_obtained > self.max_marks:
            raise ValueError(
                f"marks_obtained ({self.marks_obtained}) cannot be greater than max_marks ({self.max_marks})."
            )
        return self


class MarksCreate(MarksBase):
    """Request schema for recording new assessment marks."""
    marks_id: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Optional custom marks identifier",
        examples=["MRK-2024-001"],
    )


class MarksUpdate(BaseModel):
    """Request schema for modifying an existing marks record."""
    subject_code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    subject_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    semester: Optional[int] = Field(default=None, ge=1, le=8)
    exam_type: Optional[ExamType] = None
    marks_obtained: Optional[float] = Field(default=None, ge=0.0)
    max_marks: Optional[float] = Field(default=None, gt=0.0)
    academic_year: Optional[str] = Field(default=None, min_length=4, max_length=20)
    remarks: Optional[str] = Field(default=None, max_length=255)

    @field_validator("subject_code")
    @classmethod
    def validate_subject_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip().upper()
            if not v_stripped:
                raise ValueError("subject_code cannot be empty.")
            return v_stripped
        return None

    @field_validator("subject_name")
    @classmethod
    def validate_subject_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("subject_name cannot be empty.")
            return v_stripped
        return None

    @field_validator("exam_type", mode="before")
    @classmethod
    def normalize_exam_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("academic_year")
    @classmethod
    def validate_academic_year(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip()
            if not re.match(r"^\d{4}(-\d{2,4})?$", v_stripped):
                raise ValueError("academic_year must be formatted as YYYY or YYYY-YYYY (e.g. '2024-2025').")
            return v_stripped
        return None

    @model_validator(mode="after")
    def validate_marks_bounds(self) -> "MarksUpdate":
        if self.marks_obtained is not None and self.max_marks is not None:
            if self.marks_obtained > self.max_marks:
                raise ValueError(
                    f"marks_obtained ({self.marks_obtained}) cannot be greater than max_marks ({self.max_marks})."
                )
        return self


class MarksInDB(MarksBase):
    """
    Database model representing document stored in MongoDB marks collection.
    """
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    marks_id: str = Field(
        ...,
        description="Unique marks identifier",
        examples=["MRK-2024-001"],
    )
    percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Calculated percentage score",
        examples=[85.0],
    )
    grade: str = Field(
        ...,
        description="Calculated letter grade (A+, A, B, C, D, E, F)",
        examples=["A"],
    )
    entered_by: str = Field(
        ...,
        description="Email or user ID of the staff member who entered the marks",
        examples=["teacher@edumanage.edu"],
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of record creation",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last record update",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class MarksResponse(MarksBase):
    """
    Public response schema for marks records.
    """
    id: PyObjectId = Field(
        default_factory=ObjectId,
        validation_alias=AliasChoices("_id", "id"),
        description="Database document identifier",
    )
    marks_id: str
    percentage: float
    grade: str
    entered_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class MarksPaginationResponse(BaseModel):
    """Paginated list response schema for Marks queries."""
    items: List[MarksResponse] = Field(..., description="List of marks records for current page")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page limit")
    total: int = Field(..., ge=0, description="Total matching records count")
    pages: int = Field(..., ge=0, description="Total number of pages")


class MarksSummaryResponse(BaseModel):
    """Consolidated marks performance summary schema for a student."""
    student_id: Optional[str] = Field(default=None, description="Institutional student identifier")
    total_subjects: int = Field(..., ge=0, description="Total evaluated assessments / subjects")
    total_marks_obtained: float = Field(..., ge=0.0, description="Sum of all marks scored")
    total_max_marks: float = Field(..., ge=0.0, description="Sum of all maximum possible marks")
    overall_percentage: float = Field(..., ge=0.0, le=100.0, description="Consolidated overall percentage")
    passed_subjects: int = Field(..., ge=0, description="Number of assessments scored >= 40%")
    failed_subjects: int = Field(..., ge=0, description="Number of assessments scored < 40%")
    grade_distribution: Dict[str, int] = Field(
        ...,
        description="Count of marks in each grade band (A+, A, B, C, D, E, F)",
    )
