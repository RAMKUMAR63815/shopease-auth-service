import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


# Reusable password security validation
def validate_strong_password(value: str) -> str:
    if len(value.encode("utf-8")) > 72: #converts the password string into UTF-8 bytes
        raise ValueError("Password must not exceed 72 UTF-8 bytes")

    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one number")

    if not re.search(r"[^A-Za-z0-9]", value):
        raise ValueError("Password must contain at least one special character")

    return value


# Registration request
class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str = Field(min_length=8, max_length=72)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Full name cannot be empty")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_strong_password(value)

    @model_validator(mode="after")
    def validate_password_confirmation(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password do not match")

        return self


# Login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


# Public user information
# Password and password_hash are intentionally excluded
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Registration response
class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


# Login response
class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Verify-token request
class VerifyTokenRequest(BaseModel):
    access_token: str = Field(min_length=1)


# Verify-token response
class VerifyTokenResponse(BaseModel):
    valid: bool
    message: str
    user_id: int | None = None
    role: str | None = None


# Change-password request
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return validate_strong_password(value)

    @model_validator(mode="after")
    def validate_new_password_is_different(self):
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from current password")

        return self


# Generic password-change response
class MessageResponse(BaseModel):
    message: str
