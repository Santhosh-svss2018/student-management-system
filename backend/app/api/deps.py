"""
API Dependencies Module
Provides dependency injection for MongoDB database handles and JWT authentication.
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from pymongo.database import Database

from app.core.security import decode_access_token
from app.db.mongodb import get_database
from app.models.user import UserInDB, UserRole
from app.services.user_service import get_user_by_id

logger = logging.getLogger("edumanage.api.deps")

# HTTP Bearer security scheme for reading Authorization header
http_bearer = HTTPBearer(auto_error=False)


def get_db() -> Database:
    """
    Dependency that resolves the active MongoDB database.
    Raises HTTP 503 if MongoDB client/database is currently offline.
    """
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is currently unavailable. Please verify MongoDB service status.",
        )
    return db


def get_current_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Database = Depends(get_db),
) -> UserInDB:
    """
    Reusable FastAPI dependency that validates the JWT Bearer token in the Authorization header,
    decodes claims, extracts user ID (sub), and fetches the User from MongoDB.
    Raises HTTP 401 if token is missing, invalid, expired, or user is inactive/not found.
    """
    if auth_credentials is None or not auth_credentials.credentials:
        logger.warning("Authentication failed: Missing Authorization Bearer header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Missing Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            logger.warning("Authentication failed: Token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, jwt.PyJWTError) as exc:
        logger.warning("Authentication failed: Invalid JWT token - %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        logger.warning("Authentication failed: User with ID '%s' not found", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning("Authentication failed: User '%s' is inactive", user.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_authenticated_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """
    Dependency ensuring the user is authenticated and active.
    Returns the active user instance.
    """
    return current_user


def require_admin(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """
    Dependency requiring the authenticated user to have the ADMIN role.
    Raises HTTP 403 Forbidden if user is not an admin.
    """
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role != UserRole.ADMIN.value:
        logger.warning("Access forbidden: User '%s' (role: %s) denied Admin access", current_user.email, user_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin access required.",
        )
    return current_user


def require_teacher_or_admin(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """
    Dependency requiring the authenticated user to have TEACHER or ADMIN role.
    Raises HTTP 403 Forbidden if user is not a teacher or admin.
    """
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in [UserRole.TEACHER.value, UserRole.ADMIN.value]:
        logger.warning("Access forbidden: User '%s' (role: %s) denied Teacher/Admin access", current_user.email, user_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Teacher or Admin access required.",
        )
    return current_user


def require_student(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """
    Dependency requiring the authenticated user to have the STUDENT role.
    Raises HTTP 403 Forbidden if user is not a student.
    """
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role != UserRole.STUDENT.value:
        logger.warning("Access forbidden: User '%s' (role: %s) denied Student access", current_user.email, user_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Student access required.",
        )
    return current_user

