from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    RECEPTIONIST = "receptionist"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.RECEPTIONIST


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str


class TokenData(BaseModel):
    """
    What we store INSIDE the JWT payload.
    Small and non-sensitive — remember anyone can decode a JWT.
    Never put passwords or sensitive PII here.
    """
    user_id: int
    email: str
    role: str