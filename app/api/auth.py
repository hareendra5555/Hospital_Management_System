from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm      # ← add this
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import RegisterRequest, TokenResponse, LoginRequest
from app.services import auth_service
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register_user(db, data)
    return {"message": f"User {user.email} registered successfully", "role": user.role}


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),   # ← changed
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2PasswordRequestForm gives you form_data.username and form_data.password
    We treat username as email — standard practice when your "username" is an email
    """
    data = LoginRequest(email=form_data.username, password=form_data.password)
    return await auth_service.login_user(db, data)