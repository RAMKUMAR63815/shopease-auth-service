from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.auth_schema import RegisterRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


# Custom exception for authentication business logic
class AuthServiceError(Exception):

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

        super().__init__(detail)


# --------------------------------------------------
# 1. REGISTER USER
# --------------------------------------------------

def register_user(db: Session, data: RegisterRequest) -> User:
    """
    Register a new user.

    Steps:
    1. Normalize the email.
    2. Check whether the email already exists.
    3. Hash the password.
    4. Create the user.
    5. Save the user in MySQL.
    """

    email = str(data.email).strip().lower()

    # Check for an existing email
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise AuthServiceError(
            409,
            "Email address is already registered",
        )

    # Hash the password before storing it
    password_hash = hash_password(data.password)

    # Create a new user
    new_user = User(
        full_name=data.full_name.strip(),
        email=email,
        password_hash=password_hash,
        role="CUSTOMER",
        is_active=True,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        # Handle duplicate email even if another request
        # registered it between our check and database insert.
        db.rollback()

        raise AuthServiceError(
            409,
            "Email address is already registered",
        )

    except Exception:
        db.rollback()
        raise


# --------------------------------------------------
# 2. LOGIN USER
# --------------------------------------------------

def login_user(db: Session, email: str, password: str):
    """
    Authenticate a user and generate a JWT.

    Steps:
    1. Find the user by email.
    2. Verify the entered password.
    3. Check whether the account is active.
    4. Generate an access token.
    """

    email = email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    # Do not reveal whether the email or password was wrong
    if user is None or not verify_password(
        password,
        user.password_hash,
    ):
        raise AuthServiceError(
            401,
            "Invalid email or password",
        )

    # Prevent inactive accounts from logging in
    if not user.is_active:
        raise AuthServiceError(
            403,
            "Your account is inactive",
        )

    # Generate JWT using the user's ID and role
    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return user, access_token


# --------------------------------------------------
# 3. GET USER BY ID
# --------------------------------------------------

def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Retrieve a user using the database primary key.
    """

    user = db.get(User, user_id)

    if user is None:
        raise AuthServiceError(
            404,
            "User not found",
        )

    return user


# --------------------------------------------------
# 4. GET AUTHENTICATED USER FROM JWT
# --------------------------------------------------

def get_user_from_token(db: Session, token: str):
    """
    Validate a JWT and retrieve its associated user.

    This is used by protected endpoints such as /me
    and /verify-token.
    """

    payload = decode_access_token(token)

    if payload is None:
        raise AuthServiceError(
            401,
            "Invalid or expired access token",
        )

    user_id = int(payload["sub"])

    user = db.get(User, user_id)

    if user is None:
        raise AuthServiceError(
            401,
            "User associated with this token does not exist",
        )

    if not user.is_active:
        raise AuthServiceError(
            403,
            "Your account is inactive",
        )

    # Reject tokens containing an outdated role
    if payload["role"] != user.role:
        raise AuthServiceError(
            401,
            "Access token is no longer valid",
        )

    return user, payload


# --------------------------------------------------
# 5. VERIFY ACCESS TOKEN
# --------------------------------------------------

def verify_user_token(db: Session, token: str):
    """
    Verify the token and confirm that its user
    still exists and is active.
    """

    user, payload = get_user_from_token(db, token)

    return {
        "valid": True,
        "message": "Access token is valid",
        "user_id": user.id,
        "role": user.role,
    }


# --------------------------------------------------
# 6. CHANGE PASSWORD
# --------------------------------------------------

def change_user_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
):
    """
    Change the authenticated user's password.

    Steps:
    1. Verify the current password.
    2. Hash the new password.
    3. Update the database.
    """

    # Check the current password
    if not verify_password(
        current_password,
        user.password_hash,
    ):
        raise AuthServiceError(
            400,
            "Current password is incorrect",
        )

    # Hash the new password before saving
    user.password_hash = hash_password(new_password)

    try:
        db.commit()
        db.refresh(user)

        return {
            "message": "Password changed successfully"
        }

    except Exception:
        db.rollback()
        raise
