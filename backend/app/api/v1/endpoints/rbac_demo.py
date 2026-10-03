"""
Role-Based Access Control (RBAC) Demonstration Endpoints
Provides test endpoints to verify role-based permissions and access restrictions.
"""

from fastapi import APIRouter, Depends
from app.api.deps import (
    require_admin,
    require_authenticated_user,
    require_student,
    require_teacher_or_admin,
)
from app.models.user import UserInDB

router = APIRouter()


@router.get(
    "/admin",
    summary="Admin Only Test Endpoint",
    description="Accessible strictly by users with the ADMIN role.",
)
def get_admin_dashboard(
    current_user: UserInDB = Depends(require_admin),
):
    """Admin-only endpoint."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return {
        "message": "Admin access granted",
        "role": user_role,
    }


@router.get(
    "/teacher",
    summary="Teacher or Admin Test Endpoint",
    description="Accessible by users with TEACHER or ADMIN roles.",
)
def get_teacher_dashboard(
    current_user: UserInDB = Depends(require_teacher_or_admin),
):
    """Teacher/Admin endpoint."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return {
        "message": "Teacher/Admin access granted",
        "role": user_role,
    }


@router.get(
    "/student",
    summary="Student Only Test Endpoint",
    description="Accessible strictly by users with the STUDENT role.",
)
def get_student_dashboard(
    current_user: UserInDB = Depends(require_student),
):
    """Student-only endpoint."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return {
        "message": "Student access granted",
        "role": user_role,
    }


@router.get(
    "/authenticated",
    summary="Authenticated User Test Endpoint",
    description="Accessible by any active authenticated user regardless of role.",
)
def get_authenticated_profile(
    current_user: UserInDB = Depends(require_authenticated_user),
):
    """Any authenticated user endpoint."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return {
        "message": "Authenticated access granted",
        "role": user_role,
    }
