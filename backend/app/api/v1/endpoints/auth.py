"""
Authentication API Endpoints
Handles user login, JWT generation, and token-based identity verification.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token, verify_password
from app.models.auth import LoginRequest, Token
from app.models.user import UserInDB, UserResponse
from app.services.user_service import get_user_by_email

logger = logging.getLogger("edumanage.api.auth")
router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticates user credentials and issues a signed JWT access token.",
)
def login(
    login_data: LoginRequest,
    db: Database = Depends(get_db),
) -> Token:
    """
    Authenticates user with normalized email and Argon2 hashed password verification.
    Returns a JWT access token with user ID (sub), role, and expiration.
    """
    normalized_email = str(login_data.email).strip().lower()

    # Look up user by normalized email
    user = get_user_by_email(db, normalized_email)
    if not user:
        logger.warning("Failed login attempt: email not found '%s'", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password against Argon2 hash
    if not verify_password(login_data.password, user.hashed_password):
        logger.warning("Failed login attempt: incorrect password for '%s'", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user account is active
    if not user.is_active:
        logger.warning("Failed login attempt: user '%s' is inactive", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract role string
    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)

    # Generate JWT access token
    access_token = create_access_token(
        subject=str(user.id),
        role=role_str,
    )

    logger.info("Successful login for user '%s' (Role: %s)", normalized_email, role_str)
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Returns the profile of the currently authenticated user based on JWT Bearer token.",
)
def read_current_user_profile(
    current_user: UserInDB = Depends(get_current_user),
) -> UserResponse:
    """
    Fetches the authenticated user profile using the get_current_user dependency.
    """
    return UserResponse.model_validate(current_user)
