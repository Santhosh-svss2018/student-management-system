"""
AI Insights & Student Risk Analysis API Endpoints
Provides student risk analysis, diagnostic factor generation, and institutional risk overview.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.api.deps import (
    get_db,
    require_admin,
    require_student,
    require_teacher_or_admin,
)
from app.models.ai_insights import (
    InstitutionalRiskSummary,
    StudentRiskAnalysis,
)
from app.models.user import UserInDB
from app.services.ai_insights_service import (
    calculate_student_risk,
    get_institutional_risk_summary,
)
from app.services.student_service import get_student_by_email

logger = logging.getLogger("edumanage.api.ai_insights")
router = APIRouter()


@router.get(
    "/students",
    response_model=InstitutionalRiskSummary,
    summary="Get institutional student risk overview",
    description="Calculates and returns risk distribution and student alerts across the institution. Restricted to Admin and Teacher roles.",
)
def get_institutional_overview(
    risk_level: Optional[str] = Query(None, description="Filter by risk severity band (LOW, MEDIUM, HIGH, CRITICAL)"),
    department: Optional[str] = Query(None, description="Filter by academic department"),
    limit: int = Query(50, ge=1, le=100, description="Max student alert items to return"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> InstitutionalRiskSummary:
    """
    Computes institutional risk scores and summary counts across active student records.
    """
    return get_institutional_risk_summary(
        db=db,
        risk_level=risk_level,
        department=department,
        limit=limit,
    )


@router.get(
    "/me",
    response_model=StudentRiskAnalysis,
    summary="Get current student's academic risk analysis",
    description="Allows authenticated students to inspect their own academic risk evaluation and personal study recommendations. Restricted to Student role only.",
)
def get_my_risk_analysis(
    current_user: UserInDB = Depends(require_student),
    db: Database = Depends(get_db),
) -> StudentRiskAnalysis:
    """
    Identifies authenticated student from JWT and computes their risk analysis.
    """
    student = get_student_by_email(db, email=current_user.email)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for the authenticated user.",
        )

    return calculate_student_risk(db=db, identifier=student.student_id)


@router.get(
    "/student/{student_id}",
    response_model=StudentRiskAnalysis,
    summary="Get risk analysis for a specific student",
    description="Returns detailed risk diagnosis, score, factors, and recommendations for a student. Restricted to Admin and Teacher roles.",
)
def get_student_risk(
    student_id: str,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> StudentRiskAnalysis:
    """
    Calculates explainable risk score and recommendations for the specified student identifier.
    """
    return calculate_student_risk(db=db, identifier=student_id)
