from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    # Check duplicate email
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {data.email} already exists"
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, data: LoginRequest) -> TokenResponse:
    # Step 1 — find user by email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # Step 2 — verify password
    # WHY check both in one condition?
    # If we returned "user not found" separately, attackers could enumerate
    # valid emails by checking which error they get. Always return the same
    # error for both cases — this is called "username enumeration protection"
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Step 3 — create JWT token
    token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        full_name=user.full_name,
    )