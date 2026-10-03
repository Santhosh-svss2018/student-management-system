"""
Attendance API Endpoints
Handles attendance marking, search, date range filtering, student summaries, and student self-access.
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
from app.models.attendance import (
    AttendanceCreate,
    AttendancePaginationResponse,
    AttendanceResponse,
    AttendanceSummaryResponse,
    AttendanceUpdate,
)
from app.models.user import UserInDB, UserRole
from app.services.attendance_service import (
    calculate_attendance_summary,
    create_attendance,
    delete_attendance,
    get_attendance_by_id,
    get_attendance_list,
    get_student_attendance,
    update_attendance,
)
from app.services.student_service import get_student_by_email

logger = logging.getLogger("edumanage.api.attendance")
router = APIRouter()


@router.post(
    "/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record student attendance",
    description="Creates a new attendance record for a student. Restricted to Admin and Teacher roles.",
)
def record_attendance(
    attendance_in: AttendanceCreate,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> AttendanceResponse:
    """
    Creates an attendance record. Ensures student existence and prevents duplicate attendance for the same date.
    """
    marked_by = current_user.email
    attendance_db = create_attendance(
        db=db,
        attendance_in=attendance_in,
        marked_by=marked_by,
    )
    return AttendanceResponse.model_validate(attendance_db)


@router.get(
    "/",
    response_model=AttendancePaginationResponse,
    summary="List and filter attendance records",
    description="Returns paginated attendance records. Supports filtering by student, single date, date range, and status. Restricted to Admin and Teacher roles.",
)
def list_attendance(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page limit (max 100)"),
    student_id: Optional[str] = Query(None, description="Filter by institutional student ID"),
    date: Optional[str] = Query(None, description="Filter by specific date (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, description="Start date for range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for range filter (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status (present, absent, late, excused)"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> AttendancePaginationResponse:
    """
    Fetches paginated attendance records matching query filters.
    """
    items, total, pages = get_attendance_list(
        db=db,
        page=page,
        limit=limit,
        student_id=student_id,
        date=date,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )
    return AttendancePaginationResponse(
        items=[AttendanceResponse.model_validate(item) for item in items],
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/me",
    response_model=AttendancePaginationResponse,
    summary="Get current student's attendance records",
    description="Allows an authenticated student to retrieve their own attendance records. Restricted to Student role only.",
)
def get_my_attendance(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page limit"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Status filter (present, absent, late, excused)"),
    current_user: UserInDB = Depends(require_student),
    db: Database = Depends(get_db),
) -> AttendancePaginationResponse:
    """
    Determines student profile from authenticated student JWT and retrieves their attendance records.
    """
    student = get_student_by_email(db, email=current_user.email)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for the authenticated user.",
        )

    items, total, pages = get_attendance_list(
        db=db,
        page=page,
        limit=limit,
        student_id=student.student_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )
    return AttendancePaginationResponse(
        items=[AttendanceResponse.model_validate(item) for item in items],
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/me/summary",
    response_model=AttendanceSummaryResponse,
    summary="Get current student's attendance summary",
    description="Allows an authenticated student to retrieve their consolidated attendance metrics. Restricted to Student role only.",
)
def get_my_attendance_summary(
    current_user: UserInDB = Depends(require_student),
    db: Database = Depends(get_db),
) -> AttendanceSummaryResponse:
    """
    Calculates attendance summary metrics for the authenticated student.
    """
    student = get_student_by_email(db, email=current_user.email)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for the authenticated user.",
        )

    return calculate_attendance_summary(db=db, student_id=student.student_id)


@router.get(
    "/student/{student_id}",
    response_model=AttendancePaginationResponse,
    summary="Get attendance records for a specific student",
    description="Retrieves paginated attendance records for a student. Restricted to Admin and Teacher roles.",
)
def get_records_by_student(
    student_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page limit"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Status filter"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> AttendancePaginationResponse:
    """
    Fetches attendance records for a specified student identifier.
    """
    items, total, pages = get_student_attendance(
        db=db,
        student_id=student_id,
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )
    return AttendancePaginationResponse(
        items=[AttendanceResponse.model_validate(item) for item in items],
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/student/{student_id}/summary",
    response_model=AttendanceSummaryResponse,
    summary="Get attendance summary for a specific student",
    description="Calculates summary counts and percentage for a student. Restricted to Admin and Teacher roles.",
)
def get_summary_by_student(
    student_id: str,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> AttendanceSummaryResponse:
    """
    Returns total days, present, absent, late, excused days, and percentage for a student.
    """
    return calculate_attendance_summary(db=db, student_id=student_id)


@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Get a single attendance record",
    description="Retrieves a specific attendance record by ID. Restricted to Admin and Teacher roles.",
)
def read_attendance(
    attendance_id: str,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> AttendanceResponse:
    """
    Fetches an attendance record by its attendance_id or BSON _id.
    """
    record = get_attendance_by_id(db=db, identifier=attendance_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with identifier '{attendance_id}' was not found.",
        )
    return AttendanceResponse.model_validate(record)


@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Update an attendance record",
    description="Modifies status, remarks, or date for an attendance record. Restricted to Admin and Teacher roles.",
)
def modify_attendance(
    attendance_id: str,
    attendance_update: AttendanceUpdate,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> AttendanceResponse:
    """
    Updates attendance fields and refreshes updated_at timestamp.
    """
    updated_record = update_attendance(
        db=db,
        identifier=attendance_id,
        attendance_update=attendance_update,
    )
    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with identifier '{attendance_id}' was not found.",
        )
    return AttendanceResponse.model_validate(updated_record)


@router.delete(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Delete an attendance record",
    description="Permanently removes an attendance record. Restricted to Admins only.",
)
def remove_attendance(
    attendance_id: str,
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> AttendanceResponse:
    """
    Deletes an attendance record.
    """
    deleted = delete_attendance(db=db, identifier=attendance_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with identifier '{attendance_id}' was not found.",
        )
    return AttendanceResponse.model_validate(deleted)
