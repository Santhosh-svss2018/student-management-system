"""
Tests for Security and Password Hashing Module
Verifies Argon2 hashing, salt uniqueness, and verification behavior.
"""

import pytest
from app.core.security import get_password_hash, verify_password


def test_password_hashing_basic():
    """Test that hashing creates an Argon2id hash."""
    raw_password = "SuperSecretPassword123!"
    hashed = get_password_hash(raw_password)

    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed.startswith("$argon2id$")
    assert hashed != raw_password


def test_password_verification_success():
    """Test that correct password verifies against its hash."""
    raw_password = "CorrectHorseBatteryStaple99"
    hashed = get_password_hash(raw_password)

    assert verify_password(raw_password, hashed) is True


def test_password_verification_failure():
    """Test that incorrect password does not verify."""
    raw_password = "OriginalPassword456"
    hashed = get_password_hash(raw_password)

    assert verify_password("WrongPassword456", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(raw_password, "invalid_hash") is False


def test_hash_salt_uniqueness():
    """Test that hashing the same password twice produces unique hashes (salting)."""
    raw_password = "SamePasswordEveryTime"
    hash1 = get_password_hash(raw_password)
    hash2 = get_password_hash(raw_password)

    assert hash1 != hash2
    assert verify_password(raw_password, hash1) is True
    assert verify_password(raw_password, hash2) is True


def test_empty_password_raises_error():
    """Test that attempting to hash empty strings raises ValueError."""
    with pytest.raises(ValueError):
        get_password_hash("")


def test_jwt_create_and_decode_token():
    """Test generating and decoding a JWT access token."""
    from app.core.security import create_access_token, decode_access_token
    token = create_access_token(subject="user_123", role="teacher")
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == "user_123"
    assert payload["role"] == "teacher"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_expired_token():
    """Test that decode_access_token raises ExpiredSignatureError for expired token."""
    from datetime import timedelta
    import jwt
    from app.core.security import create_access_token, decode_access_token

    expired_token = create_access_token(
        subject="user_expired",
        role="student",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)


def test_jwt_invalid_token():
    """Test that decode_access_token raises InvalidTokenError for malformed token."""
    import jwt
    from app.core.security import decode_access_token

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("completely.invalid.jwt")

