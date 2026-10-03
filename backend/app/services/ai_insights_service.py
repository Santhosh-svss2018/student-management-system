"""
AI Insights & Student Risk Analysis Service Module
Calculates deterministic, explainable student academic risk scores based on MongoDB Attendance and Marks data.
"""

from datetime import datetime, timezone
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from pymongo.database import Database

from app.models.ai_insights import (
    InstitutionalRiskSummary,
    RiskLevel,
    StudentRiskAnalysis,
    determine_risk_level,
)
from app.services.attendance_service import calculate_attendance_summary
from app.services.marks_service import calculate_student_marks_summary
from app.services.student_service import get_student_by_identifier

logger = logging.getLogger("edumanage.services.ai_insights")


def calculate_student_risk(db: Database, identifier: str) -> StudentRiskAnalysis:
    """
    Calculates an explainable institutional academic risk score for a student.
    Integrates 40% attendance weight and 60% academic performance weight with penalties for failed assessments.
    """
    student = get_student_by_identifier(db=db, identifier=identifier.strip())
    if not student:
        logger.warning("Risk analysis rejected: Student '%s' not found", identifier)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{identifier}' was not found.",
        )

    canonical_id = student.student_id

    # 1. Fetch real attendance metrics
    att_summary = calculate_attendance_summary(db=db, student_id=canonical_id)
    total_days = att_summary.total_days
    attendance_pct = att_summary.attendance_percentage
    attendance_score = attendance_pct if total_days > 0 else 100.0

    # 2. Fetch real marks performance metrics
    marks_summary = calculate_student_marks_summary(db=db, student_id=canonical_id)
    total_assessments = marks_summary.total_subjects
    academic_pct = marks_summary.overall_percentage
    failed_assessments = marks_summary.failed_subjects
    academic_score = academic_pct if total_assessments > 0 else 100.0

    # 3. Calculate bounded risk score (0 - 100)
    if total_days == 0 and total_assessments == 0:
        # Default baseline when no academic tracking events exist yet
        risk_score = 0.0
        risk_level = RiskLevel.LOW
    else:
        if total_days > 0 and total_assessments > 0:
            performance_score = (attendance_score * 0.40) + (academic_score * 0.60)
        elif total_days > 0:
            performance_score = attendance_score
        else:
            performance_score = academic_score

        base_risk = 100.0 - performance_score
        # Penalty of 5.0 points per failed assessment (max 20 points penalty)
        penalty = min(20.0, failed_assessments * 5.0)
        calculated_risk = base_risk + penalty
        risk_score = max(0.0, min(100.0, round(calculated_risk, 2)))
        risk_level = determine_risk_level(risk_score)

    # 4. Generate explainable key diagnostic factors
    key_factors: List[str] = []

    if total_days > 0:
        if attendance_pct < 75.0:
            key_factors.append(
                f"Attendance ({attendance_pct}%) is below the mandatory 75% institutional threshold."
            )
        elif attendance_pct >= 90.0:
            key_factors.append(
                f"Attendance is excellent at {attendance_pct}% ({att_summary.present_days}/{total_days} sessions attended)."
            )
    else:
        key_factors.append("No attendance sessions recorded in database yet.")

    if total_assessments > 0:
        if failed_assessments > 0:
            key_factors.append(
                f"Student has failed {failed_assessments} assessment{'s' if failed_assessments > 1 else ''} (score < 40%)."
            )
        if academic_pct < 50.0:
            key_factors.append(
                f"Overall academic score ({academic_pct}%) is critically below the 50% passing expectation."
            )
        elif academic_pct >= 80.0:
            key_factors.append(
                f"Strong academic performance with an overall average score of {academic_pct}%."
            )
    else:
        key_factors.append("No assessment marks recorded in database yet.")

    if not key_factors:
        key_factors.append("Academic performance and attendance trajectories are currently stable.")

    # 5. Generate actionable recommendations
    recommendations: List[str] = []

    if total_days > 0 and attendance_pct < 75.0:
        recommendations.append(
            "Improve class attendance and maintain at least the 75% institutional requirement to avoid semester detention."
        )

    if total_assessments > 0 and failed_assessments > 0:
        recommendations.append(
            "Review failed course modules with subject faculty and schedule remedial tutorial sessions."
        )

    if total_assessments > 0 and academic_pct < 60.0:
        recommendations.append(
            "Focus on subjects with lower scores and schedule supplementary study sessions."
        )

    if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        recommendations.append(
            "Initiate academic counselor meeting and alert batch faculty advisor for early intervention."
        )
    elif risk_level == RiskLevel.LOW:
        recommendations.append(
            "Maintain current attendance consistency and coursework pace for continued academic distinction."
        )

    if not recommendations:
        recommendations.append("Continue current study routine and periodic self-assessments.")

    return StudentRiskAnalysis(
        student_id=canonical_id,
        student_name=student.full_name,
        department=student.department,
        year=student.year,
        roll_number=student.roll_number,
        risk_score=risk_score,
        risk_level=risk_level,
        attendance_percentage=attendance_pct,
        academic_percentage=academic_pct,
        attendance_score=attendance_score,
        academic_score=academic_score,
        failed_assessments=failed_assessments,
        total_assessments=total_assessments,
        total_attendance_days=total_days,
        key_factors=key_factors,
        recommendations=recommendations,
        generated_at=datetime.now(timezone.utc),
    )


def get_institutional_risk_summary(
    db: Database,
    risk_level: Optional[str] = None,
    department: Optional[str] = None,
    limit: int = 50,
) -> InstitutionalRiskSummary:
    """
    Computes institutional risk analyses across active students in MongoDB.
    Aggregates critical, high, medium, and low counts and average institutional risk score.
    """
    query = {"is_active": True}
    if department and department.strip() and department != "All":
        query["department"] = department.strip()

    students_cursor = db.students.find(query).limit(100)
    analyses: List[StudentRiskAnalysis] = []

    for s_doc in students_cursor:
        student_id = s_doc.get("student_id")
        if student_id:
            try:
                analysis = calculate_student_risk(db=db, identifier=student_id)
                analyses.append(analysis)
            except Exception as exc:
                logger.error("Error analyzing student %s: %s", student_id, exc)

    total_analyzed = len(analyses)
    critical_count = sum(1 for a in analyses if a.risk_level == RiskLevel.CRITICAL)
    high_count = sum(1 for a in analyses if a.risk_level == RiskLevel.HIGH)
    medium_count = sum(1 for a in analyses if a.risk_level == RiskLevel.MEDIUM)
    low_count = sum(1 for a in analyses if a.risk_level == RiskLevel.LOW)

    avg_score = (
        round(sum(a.risk_score for a in analyses) / total_analyzed, 2)
        if total_analyzed > 0
        else 0.0
    )

    filtered = analyses
    if risk_level and risk_level.strip() and risk_level != "All":
        target_level = risk_level.strip().upper()
        filtered = [a for a in analyses if a.risk_level.value == target_level]

    # Sort descending by risk_score so highest risk students appear first
    sorted_items = sorted(filtered, key=lambda x: x.risk_score, reverse=True)[:limit]

    return InstitutionalRiskSummary(
        total_students_analyzed=total_analyzed,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        average_risk_score=avg_score,
        items=sorted_items,
    )
