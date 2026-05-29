from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.auth import LoginRequest
from app.services import auth_service
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new internal user.
    In production this would be admin-only — you don't want anyone
    registering themselves as an admin.
    """
    user = await auth_service.register_user(db, data)
    return {"message": f"User {user.email} registered successfully", "role": user.role}

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login with email + password.
    Returns a JWT token to use on all subsequent requests.
    """
    return await auth_service.login_user(db, data)