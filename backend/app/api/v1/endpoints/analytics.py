"""
Analytics & Institutional Metrics API Endpoints
Provides real-time dashboards metrics for Admin, Teacher, and Student roles.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.api.deps import (
    get_db,
    require_admin,
    require_student,
    require_teacher_or_admin,
)
from app.models.analytics import (
    AdminAcademicAnalytics,
    AdminAttendanceAnalytics,
    AdminDepartmentsAnalytics,
    AdminOverviewAnalytics,
    StudentAnalyticsResponse,
    TeacherOverviewAnalytics,
)
from app.models.user import UserInDB
from app.services.analytics_service import (
    get_admin_academic_analytics,
    get_admin_attendance_analytics,
    get_admin_departments_analytics,
    get_admin_overview_analytics,
    get_student_self_analytics,
    get_teacher_overview_analytics,
)

logger = logging.getLogger("edumanage.api.analytics")
router = APIRouter()


@router.get(
    "/admin/overview",
    response_model=AdminOverviewAnalytics,
    summary="Get comprehensive institutional metrics overview",
    description="Returns aggregate KPI stats, department distributions, attendance breakdown, and risk totals. Restricted to Admin role.",
)
def get_admin_overview(
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> AdminOverviewAnalytics:
    """
    Computes real-time institutional overview from MongoDB.
    """
    return get_admin_overview_analytics(db=db)


@router.get(
    "/admin/departments",
    response_model=AdminDepartmentsAnalytics,
    summary="Get department-level performance metrics",
    description="Returns student counts, attendance percentages, academic averages, and risk counts per department. Restricted to Admin role.",
)
def get_admin_departments(
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> AdminDepartmentsAnalytics:
    """
    Computes dynamic department-level statistics from MongoDB.
    """
    return get_admin_departments_analytics(db=db)


@router.get(
    "/admin/academic",
    response_model=AdminAcademicAnalytics,
    summary="Get institutional academic performance breakdown",
    description="Returns grade distributions, subject performance rankings, semester trends, and pass/fail ratios. Restricted to Admin role.",
)
def get_admin_academic(
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> AdminAcademicAnalytics:
    """
    Computes institutional academic evaluation analytics from MongoDB.
    """
    return get_admin_academic_analytics(db=db)


@router.get(
    "/admin/attendance",
    response_model=AdminAttendanceAnalytics,
    summary="Get institutional attendance metrics and defaulters",
    description="Returns overall attendance rates, status breakdowns, date trends, department comparisons, and defaulters list (<75%). Restricted to Admin role.",
)
def get_admin_attendance(
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> AdminAttendanceAnalytics:
    """
    Computes institutional attendance analytics and identifies defaulters.
    """
    return get_admin_attendance_analytics(db=db)


@router.get(
    "/teacher/overview",
    response_model=TeacherOverviewAnalytics,
    summary="Get faculty teaching metrics overview",
    description="Returns enrolled student count, class attendance rates, academic performance, grade spread, and students requiring attention. Accessible by Teacher and Admin roles.",
)
def get_teacher_overview(
    department: Optional[str] = Query(None, description="Optional department filter"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> TeacherOverviewAnalytics:
    """
    Computes authorized class/faculty metrics from MongoDB.
    """
    return get_teacher_overview_analytics(
        db=db,
        current_user_email=current_user.email,
        department=department,
    )


@router.get(
    "/student/me",
    response_model=StudentAnalyticsResponse,
    summary="Get personal student academic and attendance analytics",
    description="Returns authenticated student's attendance summary, marks overview, grade distribution, and AI risk analysis. Strictly isolated to current Student role.",
)
def get_student_analytics(
    current_user: UserInDB = Depends(require_student),
    db: Database = Depends(get_db),
) -> StudentAnalyticsResponse:
    """
    Retrieves personal analytics for the authenticated student account.
    """
    return get_student_self_analytics(
        db=db,
        current_user_email=current_user.email,
    )
