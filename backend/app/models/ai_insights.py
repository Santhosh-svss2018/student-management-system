"""
AI Insights & Student Risk Analysis Domain Models
Defines Pydantic v2 schemas for student risk evaluation, explainable factors, and institutional risk overviews.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    """Categorical risk severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def determine_risk_level(risk_score: float) -> RiskLevel:
    """
    Maps numerical risk score (0-100) to standard categorical risk severity:
    0–24.99   -> LOW
    25–49.99  -> MEDIUM
    50–74.99  -> HIGH
    75–100.0  -> CRITICAL
    """
    if risk_score >= 75.0:
        return RiskLevel.CRITICAL
    elif risk_score >= 50.0:
        return RiskLevel.HIGH
    elif risk_score >= 25.0:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


class StudentRiskAnalysis(BaseModel):
    """Comprehensive explainable risk analysis for an individual student."""
    student_id: str = Field(..., description="Institutional student identifier", examples=["STU-2024-001"])
    student_name: str = Field(..., description="Full student name", examples=["Student Alpha"])
    department: str = Field(..., description="Academic department / Major", examples=["Computer Science"])
    year: int = Field(..., description="Current academic year", examples=[3])
    roll_number: str = Field(..., description="Official roll number", examples=["CS-2024-001"])
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Calculated institutional risk score (0-100, higher is worse)", examples=[32.5])
    risk_level: RiskLevel = Field(..., description="Categorical risk band (LOW, MEDIUM, HIGH, CRITICAL)", examples=[RiskLevel.MEDIUM])
    attendance_percentage: float = Field(..., ge=0.0, le=100.0, description="Attendance percentage", examples=[78.5])
    academic_percentage: float = Field(..., ge=0.0, le=100.0, description="Overall academic score percentage", examples=[61.25])
    attendance_score: float = Field(..., ge=0.0, le=100.0, description="Normalized attendance performance score", examples=[78.5])
    academic_score: float = Field(..., ge=0.0, le=100.0, description="Normalized academic performance score", examples=[61.25])
    failed_assessments: int = Field(..., ge=0, description="Number of assessments scored below 40%", examples=[1])
    total_assessments: int = Field(..., ge=0, description="Total assessments recorded", examples=[4])
    total_attendance_days: int = Field(..., ge=0, description="Total attendance sessions recorded", examples=[20])
    key_factors: List[str] = Field(..., description="Explainable diagnostic factors derived from database data")
    recommendations: List[str] = Field(..., description="Actionable intervention recommendations")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of risk analysis generation",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class InstitutionalRiskSummary(BaseModel):
    """Institutional overview metrics and list of analyzed students for faculty/admins."""
    total_students_analyzed: int = Field(..., ge=0)
    critical_count: int = Field(..., ge=0)
    high_count: int = Field(..., ge=0)
    medium_count: int = Field(..., ge=0)
    low_count: int = Field(..., ge=0)
    average_risk_score: float = Field(..., ge=0.0, le=100.0)
    items: List[StudentRiskAnalysis] = Field(..., description="List of student risk analyses")
