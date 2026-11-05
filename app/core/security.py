from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from app.core.config import settings


# Configure bcrypt for password hashing
password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a bcrypt hash.
    Store only this hash in MySQL.
    """
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must not exceed 72 UTF-8 bytes")

    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare the password entered during login
    with the stored bcrypt hash.
    """
    try:
        return password_context.verify(
            plain_password,
            hashed_password,
        )
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, role: str) -> str:
    """
    Generate a signed JWT containing the user's ID and role.
    The token expires according to the configured lifetime.
    """
    now = datetime.now(timezone.utc)

    expiration = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": expiration,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    return token


def decode_access_token(token: str) -> dict | None:
    """
    Verify the JWT signature, algorithm and expiration.
    Return its claims when valid, otherwise return None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require": ["sub", "role", "iat", "exp"],
            },
        )

        # Confirm the subject is a valid integer user ID
        user_id = int(payload["sub"])

        if user_id <= 0:
            return None

        if not isinstance(payload["role"], str) or not payload["role"]:
            return None

        return payload

    except (InvalidTokenError, ValueError, TypeError, KeyError):
        return None
