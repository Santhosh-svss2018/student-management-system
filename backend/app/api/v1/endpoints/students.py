"""
Students API Endpoints
Handles student record CRUD, search, pagination, and student self-profile retrieval.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.api.deps import (
    get_db,
    require_admin,
    require_authenticated_user,
    require_teacher_or_admin,
)
from app.models.student import (
    StudentCreate,
    StudentPaginationResponse,
    StudentResponse,
    StudentUpdate,
)
from app.models.user import UserInDB, UserRole
from app.services.student_service import (
    create_student,
    deactivate_student,
    get_student_by_email,
    get_student_by_identifier,
    get_students,
    update_student,
)

logger = logging.getLogger("edumanage.api.students")
router = APIRouter()


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student record",
    description="Registers a new student profile in the system. Restricted to Admins only.",
)
def register_student(
    student_in: StudentCreate,
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> StudentResponse:
    """
    Creates a new student record in MongoDB.
    Validates unique constraints on student_id, email, and roll_number.
    """
    student_db = create_student(db=db, student_in=student_in)
    return StudentResponse.model_validate(student_db)


@router.get(
    "/me",
    response_model=StudentResponse,
    summary="Get Current Student Profile",
    description="Allows an authenticated student to retrieve their own student profile record.",
)
def get_my_student_profile(
    current_user: UserInDB = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
) -> StudentResponse:
    """
    Retrieves the student record linked to the authenticated user's email.
    Only students can access their student profile via this endpoint.
    """
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role != UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only student accounts can access the student self-profile endpoint.",
        )

    student = get_student_by_email(db, email=current_user.email)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for the authenticated user.",
        )

    return StudentResponse.model_validate(student)


@router.get(
    "/",
    response_model=StudentPaginationResponse,
    summary="List and search students",
    description="Returns a paginated list of students. Supports regex search across name, email, student ID, and roll number. Accessible by Admins and Teachers.",
)
def list_students(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page limit (max 100)"),
    search: Optional[str] = Query(None, description="Search query string"),
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> StudentPaginationResponse:
    """
    Fetches paginated student records with optional search filter.
    """
    items, total, pages = get_students(db=db, page=page, limit=limit, search=search)
    return StudentPaginationResponse(
        items=[StudentResponse.model_validate(s) for s in items],
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get a student by ID or student_id",
    description="Retrieves a specific student record. Accessible by Admins and Teachers.",
)
def read_student(
    student_id: str,
    current_user: UserInDB = Depends(require_teacher_or_admin),
    db: Database = Depends(get_db),
) -> StudentResponse:
    """
    Fetches a student by institutional student_id or BSON _id.
    """
    student = get_student_by_identifier(db=db, identifier=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )
    return StudentResponse.model_validate(student)


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update a student record",
    description="Updates existing student attributes. Restricted to Admins only.",
)
def modify_student(
    student_id: str,
    student_update: StudentUpdate,
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> StudentResponse:
    """
    Updates student record fields and refreshes updated_at timestamp.
    """
    updated_student = update_student(
        db=db,
        identifier=student_id,
        student_update=student_update,
    )
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )
    return StudentResponse.model_validate(updated_student)


@router.delete(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Deactivate a student record",
    description="Soft-deletes a student by marking is_active=False. Restricted to Admins only.",
)
def remove_student(
    student_id: str,
    current_user: UserInDB = Depends(require_admin),
    db: Database = Depends(get_db),
) -> StudentResponse:
    """
    Marks the student record as inactive (soft-delete).
    """
    deactivated = deactivate_student(db=db, identifier=student_id)
    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )
    return StudentResponse.model_validate(deactivated)
