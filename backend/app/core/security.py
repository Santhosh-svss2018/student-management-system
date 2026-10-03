"""
Security & Authentication Module
Implements secure password hashing (Argon2) and JWT token generation/validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from bson import ObjectId
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings

# Initialize password hasher with Argon2 as the primary and recommended algorithm
password_hasher = PasswordHash((Argon2Hasher(),))


def get_password_hash(password: str) -> str:
    """
    Generates a secure Argon2 hash for the given plaintext password.
    Never stores or returns plaintext passwords.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against an Argon2 hashed password.
    Returns True if match, False otherwise.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(
    subject: Union[str, ObjectId],
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generates a signed JWT access token containing:
    - sub: user ID
    - role: user role
    - exp: expiration timestamp (UTC)
    - iat: issued at timestamp (UTC)
    """
    now = datetime.now(timezone.utc)
    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "role": str(role),
        "exp": expire,
        "iat": now,
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates the signature and expiration of a JWT access token.
    Raises jwt.ExpiredSignatureError if token expired.
    Raises jwt.InvalidTokenError if token is malformed/invalid.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
