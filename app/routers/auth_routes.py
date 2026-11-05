from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user_model import User
from app.schemas.auth_schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    UserResponse,
    VerifyTokenRequest,
    VerifyTokenResponse,
    ChangePasswordRequest,
    MessageResponse,
)
from app.services.auth_service import (
    AuthServiceError,
    register_user,
    login_user,
    get_user_from_token,
    verify_user_token,
    change_user_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# Read Bearer tokens from the Authorization header
bearer_scheme = HTTPBearer(auto_error=False)


# --------------------------------------------------
# AUTHENTICATED USER DEPENDENCY
# --------------------------------------------------

def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Read the JWT from the Authorization header,
    validate it and return the authenticated user.
    """

    # Reject requests without a Bearer token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user, payload = get_user_from_token(
            db,
            credentials.credentials,
        )

        return user

    except AuthServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
            headers={"WWW-Authenticate": "Bearer"}
            if exc.status_code == 401 else None,
        ) from exc


# Reusable dependency declaration
CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


# --------------------------------------------------
# 1. REGISTER USER
# --------------------------------------------------

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: DatabaseSession,
):
    try:
        user = register_user(db, data)

        return RegisterResponse(
            message="User registered successfully",
            user=user,
        )

    except AuthServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        ) from exc


# --------------------------------------------------
# 2. LOGIN USER
# --------------------------------------------------

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    data: LoginRequest,
    db: DatabaseSession,
):
    try:
        user, access_token = login_user(
            db,
            str(data.email),
            data.password,
        )

        return LoginResponse(
            message="Login successful",
            access_token=access_token,
            token_type="bearer",
            user=user,
        )

    except AuthServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        ) from exc


# --------------------------------------------------
# 3. GET CURRENT USER PROFILE
# --------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_me(
    current_user: CurrentUser,
):
    return current_user


# --------------------------------------------------
# 4. VERIFY ACCESS TOKEN
# --------------------------------------------------

@router.post(
    "/verify-token",
    response_model=VerifyTokenResponse,
    status_code=status.HTTP_200_OK,
)
def verify_token(
    data: VerifyTokenRequest,
    db: DatabaseSession,
):
    try:
        result = verify_user_token(
            db,
            data.access_token,
        )

        return VerifyTokenResponse(**result)

    except AuthServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
            headers={"WWW-Authenticate": "Bearer"}
            if exc.status_code == 401 else None,
        ) from exc


# --------------------------------------------------
# 5. CHANGE PASSWORD
# --------------------------------------------------

@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        result = change_user_password(
            db=db,
            user=current_user,
            current_password=data.current_password,
            new_password=data.new_password,
        )

        return MessageResponse(**result)

    except AuthServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        ) from exc
