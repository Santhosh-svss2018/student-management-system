"""
Marks & Grades API Endpoints
Provides assessment score recording, multi-parameter listing, student summary metrics, and student self-access.
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
from app.models.marks import (
    MarksCreate,
    MarksPaginationResponse,
    MarksResponse,
    MarksSummaryResponse,
    MarksUpdate,
)
from app.models.user import UserInDB
from app.services.marks_service import (
    calculate_student_marks_summary,
    create_marks,
    delete_marks,
    get_marks_by_id,
    get_marks_list,
    get_student_marks,
    update_marks,
)
from app.services.student_service import get_student_by_email

logger = logging.getLogger("edumanage.api.marks")
router = APIRouter()


@router.post(
    "/",
    response_model=MarksResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record student marks",
    description="Creates a new assessment marks record. Restricted to Admin and Teacher roles.",
)
def record_marks(
    marks_in: MarksCreate,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> MarksResponse:
    """
    Creates a marks record, calculates percentage and grade server-side, and enforces uniqueness.
    """
    entered_by = current_user.email
    marks_db = create_marks(
        db=db,
        marks_in=marks_in,
        entered_by=entered_by,
    )
    return MarksResponse.model_validate(marks_db)


@router.get(
    "/",
    response_model=MarksPaginationResponse,
    summary="List and filter marks records",
    description="Returns paginated marks records matching query filters. Restricted to Admin and Teacher roles.",
)
def list_marks(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page limit (max 100)"),
    student_id: Optional[str] = Query(None, description="Filter by institutional student ID"),
    subject_code: Optional[str] = Query(None, description="Filter by subject code (e.g. CS-301)"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester (1-8)"),
    exam_type: Optional[str] = Query(None, description="Filter by exam type (internal_1, internal_2, model, semester, assignment)"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year (e.g. 2024-2025)"),
    search: Optional[str] = Query(None, description="Search by subject name, code, student ID, or marks ID"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> MarksPaginationResponse:
    """
    Fetches paginated marks records matching query filters.
    """
    items, total, pages = get_marks_list(
        db=db,
        page=page,
        limit=limit,
        student_id=student_id,
        subject_code=subject_code,
        semester=semester,
        exam_type=exam_type,
        academic_year=academic_year,
        search=search,
    )
    return MarksPaginationResponse(
        items=[MarksResponse.model_validate(item) for item in items],
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/me",
    response_model=MarksPaginationResponse,
    summary="Get current student's marks records",
    description="Allows an authenticated student to retrieve their own marks records. Restricted to Student role only.",
)
def get_my_marks(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page limit"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester (1-8)"),
    exam_type: Optional[str] = Query(None, description="Filter by exam type"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_user: UserInDB = Depends(require_student),
    db: Database = Depends(get_db),
) -> MarksPaginationResponse:
    """
    Identifies student profile from authenticated JWT and retrieves their marks records.
    """
    student = get_student_by_email(db, email=current_user.email)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for the authenticated user.",
        )

    items, total, pages = get_marks_list(
        db=db,
        page=page,
        limit=limit,
        student_id=student.student_id,
        semester=semester,
        exam_type=exam_type,
        academic_year=academic_year,
    )
    return MarksPaginationResponse(
        items=[MarksResponse.model_validate(item) for item in items],
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/me/summary",
    response_model=MarksSummaryResponse,
    summary="Get current student's marks performance summary",
    description="Allows an authenticated student to retrieve their consolidated marks metrics. Restricted to Student role only.",
)
def get_my_marks_summary(
    semester: Optional[int] = Query(None, ge=1, le=8, description="Optional semester filter"),
    academic_year: Optional[str] = Query(None, description="Optional academic year filter"),
    current_user: UserInDB = Depends(require_student),
    db: Database = Depends(get_db),
) -> MarksSummaryResponse:
    """
    Calculates consolidated marks metrics for the authenticated student.
    """
    student = get_student_by_email(db, email=current_user.email)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for the authenticated user.",
        )

    return calculate_student_marks_summary(
        db=db,
        student_id=student.student_id,
        semester=semester,
        academic_year=academic_year,
    )


@router.get(
    "/student/{student_id}",
    response_model=MarksPaginationResponse,
    summary="Get marks records for a specific student",
    description="Retrieves paginated marks records for a student. Restricted to Admin and Teacher roles.",
)
def get_records_by_student(
    student_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page limit"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester"),
    exam_type: Optional[str] = Query(None, description="Filter by exam type"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> MarksPaginationResponse:
    """
    Fetches marks records for a specified student identifier.
    """
    items, total, pages = get_student_marks(
        db=db,
        student_id=student_id,
        page=page,
        limit=limit,
        semester=semester,
        exam_type=exam_type,
        academic_year=academic_year,
    )
    return MarksPaginationResponse(
        items=[MarksResponse.model_validate(item) for item in items],
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/student/{student_id}/summary",
    response_model=MarksSummaryResponse,
    summary="Get marks summary for a specific student",
    description="Calculates summary counts, totals, grade distribution, and overall percentage for a student. Restricted to Admin and Teacher roles.",
)
def get_summary_by_student(
    student_id: str,
    semester: Optional[int] = Query(None, ge=1, le=8, description="Optional semester filter"),
    academic_year: Optional[str] = Query(None, description="Optional academic year filter"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> MarksSummaryResponse:
    """
    Returns marks summary metrics for a student.
    """
    return calculate_student_marks_summary(
        db=db,
        student_id=student_id,
        semester=semester,
        academic_year=academic_year,
    )


@router.get(
    "/{marks_id}",
    response_model=MarksResponse,
    summary="Get a single marks record",
    description="Retrieves a specific marks record by ID. Restricted to Admin and Teacher roles.",
)
def read_marks(
    marks_id: str,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> MarksResponse:
    """
    Fetches a marks record by its marks_id or BSON _id.
    """
    record = get_marks_by_id(db=db, identifier=marks_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marks record with identifier '{marks_id}' was not found.",
        )
    return MarksResponse.model_validate(record)


@router.put(
    "/{marks_id}",
    response_model=MarksResponse,
    summary="Update a marks record",
    description="Modifies marks attributes, recalculates percentage/grade, and refreshes timestamp. Restricted to Admin and Teacher roles.",
)
def modify_marks(
    marks_id: str,
    marks_update: MarksUpdate,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> MarksResponse:
    """
    Updates marks fields, validates bounds, recalculates grades, and updates timestamp.
    """
    updated_record = update_marks(
        db=db,
        identifier=marks_id,
        marks_update=marks_update,
    )
    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marks record with identifier '{marks_id}' was not found.",
        )
    return MarksResponse.model_validate(updated_record)


@router.delete(
    "/{marks_id}",
    response_model=MarksResponse,
    summary="Delete a marks record",
    description="Permanently removes a marks record. Restricted to Admin role only.",
)
def remove_marks(
    marks_id: str,
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> MarksResponse:
    """
    Deletes a marks record.
    """
    deleted = delete_marks(db=db, identifier=marks_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marks record with identifier '{marks_id}' was not found.",
        )
    return MarksResponse.model_validate(deleted)
