"""
Users API Endpoints
Handles user creation, listing, and profile retrieval.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.api.deps import get_db
from app.models.user import UserCreate, UserResponse
from app.services.user_service import (
    create_user,
    get_user_by_id,
    get_users,
)

logger = logging.getLogger("edumanage.api.users")
router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Registers a new user with Argon2 password hashing and unique email validation.",
)
def register_user(
    user_in: UserCreate,
    db: Database = Depends(get_db),
) -> UserResponse:
    """
    Creates a new user account.
    - Validates email and password requirements.
    - Hashes password using Argon2.
    - Persists document in MongoDB with a unique index constraint.
    - Returns serialized user profile without exposing password hashes.
    """
    user_db = create_user(db=db, user_in=user_in)
    return UserResponse.model_validate(user_db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieves a single user profile by BSON ObjectId.",
)
def read_user_by_id(
    user_id: str,
    db: Database = Depends(get_db),
) -> UserResponse:
    """
    Fetches a user profile by MongoDB ObjectId.
    """
    user = get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' was not found.",
        )
    return UserResponse.model_validate(user)


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users",
    description="Returns a paginated list of users.",
)
def read_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max number of users to return"),
    db: Database = Depends(get_db),
) -> List[UserResponse]:
    """
    Lists users with pagination support.
    """
    users = get_users(db=db, skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]
