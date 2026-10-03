"""
Reports & Data Export API Endpoints
Provides filtered institutional report queries and CSV/PDF export endpoints.
"""

from datetime import datetime, timezone
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
import io
from pymongo.database import Database

from app.api.deps import (
    get_current_user,
    get_db,
    require_admin,
    require_teacher_or_admin,
)
from app.models.reports import (
    AcademicSummaryReportResponse,
    AttendanceReportResponse,
    MarksReportResponse,
    StudentReportResponse,
)
from app.models.user import UserInDB, UserRole
from app.services.reports_service import (
    export_attendance_csv,
    export_marks_csv,
    export_students_csv,
    generate_student_pdf_bytes,
    get_academic_summary_report,
    get_attendance_report,
    get_marks_report,
    get_students_report,
)
from app.services.student_service import get_student_by_email, get_student_by_identifier

logger = logging.getLogger("edumanage.api.reports")
router = APIRouter()


@router.get(
    "/students",
    response_model=StudentReportResponse,
    summary="Get filtered student demographic & performance report",
    description="Returns filtered, paginated student records with real attendance and academic percentages. Restricted to Admin and Teacher roles.",
)
def get_students_report_endpoint(
    department: Optional[str] = Query(None, description="Filter by department"),
    year: Optional[int] = Query(None, ge=1, le=8, description="Filter by academic year"),
    section: Optional[str] = Query(None, description="Filter by section"),
    is_active: Optional[bool] = Query(None, description="Filter active/inactive status"),
    search: Optional[str] = Query(None, description="Search by name, ID, roll, or email"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=500, description="Items per page"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> StudentReportResponse:
    """
    Retrieves filtered student report data from MongoDB.
    """
    return get_students_report(
        db=db,
        department=department,
        year=year,
        section=section,
        is_active=is_active,
        search=search,
        page=page,
        limit=limit,
    )


@router.get(
    "/attendance",
    response_model=AttendanceReportResponse,
    summary="Get filtered attendance tracking report",
    description="Returns filtered attendance records enriched with student profile metadata. Restricted to Admin and Teacher roles.",
)
def get_attendance_report_endpoint(
    department: Optional[str] = Query(None, description="Filter by department"),
    year: Optional[int] = Query(None, ge=1, le=8, description="Filter by academic year"),
    section: Optional[str] = Query(None, description="Filter by section"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    student_id: Optional[str] = Query(None, description="Filter by specific student"),
    status: Optional[str] = Query(None, description="Filter by status (present, absent, late, excused)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=500, description="Items per page"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> AttendanceReportResponse:
    """
    Retrieves filtered attendance report records.
    """
    return get_attendance_report(
        db=db,
        department=department,
        year=year,
        section=section,
        date_from=date_from,
        date_to=date_to,
        student_id=student_id,
        status=status,
        page=page,
        limit=limit,
    )


@router.get(
    "/marks",
    response_model=MarksReportResponse,
    summary="Get filtered academic marks & grades report",
    description="Returns filtered evaluation marks records with student metadata and grades. Restricted to Admin and Teacher roles.",
)
def get_marks_report_endpoint(
    department: Optional[str] = Query(None, description="Filter by department"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester"),
    subject_code: Optional[str] = Query(None, description="Filter by subject code"),
    exam_type: Optional[str] = Query(None, description="Filter by exam type"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    student_id: Optional[str] = Query(None, description="Filter by specific student"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=500, description="Items per page"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> MarksReportResponse:
    """
    Retrieves filtered marks report records.
    """
    return get_marks_report(
        db=db,
        department=department,
        semester=semester,
        subject_code=subject_code,
        exam_type=exam_type,
        academic_year=academic_year,
        student_id=student_id,
        page=page,
        limit=limit,
    )


@router.get(
    "/academic-summary",
    response_model=AcademicSummaryReportResponse,
    summary="Get consolidated institutional academic summary report",
    description="Returns aggregate averages, grade distribution, and student cohort listing. Restricted to Admin and Teacher roles.",
)
def get_academic_summary_report_endpoint(
    department: Optional[str] = Query(None, description="Filter by department"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=500, description="Items per page"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> AcademicSummaryReportResponse:
    """
    Computes consolidated academic summary report.
    """
    return get_academic_summary_report(
        db=db,
        department=department,
        semester=semester,
        academic_year=academic_year,
        page=page,
        limit=limit,
    )


# ==================================================
# CSV EXPORT ENDPOINTS
# ==================================================

@router.get(
    "/students/export",
    summary="Export students report as CSV file",
    description="Streams a formatted RFC 4180 compliant CSV of student records and academic performance metrics.",
)
def export_students_csv_endpoint(
    department: Optional[str] = Query(None),
    year: Optional[int] = Query(None, ge=1, le=8),
    section: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
):
    """
    Generates and streams students CSV export.
    """
    csv_content = export_students_csv(
        db=db,
        department=department,
        year=year,
        section=section,
        is_active=is_active,
    )

    filename = f"edumanage_students_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )


@router.get(
    "/attendance/export",
    summary="Export attendance report as CSV file",
    description="Streams a formatted RFC 4180 compliant CSV of attendance records.",
)
def export_attendance_csv_endpoint(
    department: Optional[str] = Query(None),
    year: Optional[int] = Query(None, ge=1, le=8),
    section: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    student_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
):
    """
    Generates and streams attendance CSV export.
    """
    csv_content = export_attendance_csv(
        db=db,
        department=department,
        year=year,
        section=section,
        date_from=date_from,
        date_to=date_to,
        student_id=student_id,
        status=status,
    )

    filename = f"edumanage_attendance_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )


@router.get(
    "/marks/export",
    summary="Export marks & evaluations report as CSV file",
    description="Streams a formatted RFC 4180 compliant CSV of marks records.",
)
def export_marks_csv_endpoint(
    department: Optional[str] = Query(None),
    semester: Optional[int] = Query(None, ge=1, le=8),
    subject_code: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    student_id: Optional[str] = Query(None),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
):
    """
    Generates and streams marks CSV export.
    """
    csv_content = export_marks_csv(
        db=db,
        department=department,
        semester=semester,
        subject_code=subject_code,
        exam_type=exam_type,
        academic_year=academic_year,
        student_id=student_id,
    )

    filename = f"edumanage_marks_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )


# ==================================================
# PDF EXPORT ENDPOINT
# ==================================================

@router.get(
    "/student/{student_id}/pdf",
    summary="Download student academic performance report as PDF",
    description="Generates an official ISO 32000-1 PDF document with attendance, evaluations, grades, and risk analysis. Admin/Teacher can access any student; Student role can only access their own record.",
)
def export_student_pdf_endpoint(
    student_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Generates and streams an official student PDF academic report with strict RBAC.
    """
    target_student = get_student_by_identifier(db, student_id.strip())
    if not target_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )

    # Student RBAC check: Student can ONLY export their own report
    if current_user.role == UserRole.STUDENT:
        my_student = get_student_by_email(db, current_user.email)
        if not my_student or my_student.student_id != target_student.student_id:
            logger.warning(
                "Unauthorized student PDF export attempt: User '%s' requested student '%s'",
                current_user.email,
                student_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: You are only authorized to export your own academic report.",
            )

    pdf_bytes = generate_student_pdf_bytes(db=db, student_id=target_student.student_id)
    filename = f"edumanage_{target_student.student_id}_report.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )
