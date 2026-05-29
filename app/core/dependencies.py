from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import decode_access_token
from app.core.database import get_db
from app.models.user import User

# Tells FastAPI where the token comes from
# When you hit /docs, it adds an Authorize button pointing to /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Core dependency — extracts and validates the JWT token.
    Used by every protected route.
    FastAPI calls this automatically when a route depends on it.
    """
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    return user


# ── Role-based dependency factories ─────────────────────────────────────────
# These are reusable — drop any of them into any route as a dependency

def require_role(*roles: str):
    """
    Factory that returns a dependency checking for specific roles.

    Usage in a route:
        async def create_doctor(
            current_user: User = Depends(require_role("admin"))
        )

    Multiple roles:
        Depends(require_role("admin", "receptionist"))
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {list(roles)}"
            )
        return current_user
    return role_checker


# Pre-built role dependencies — import and use directly in routes
require_admin = require_role("admin")
require_doctor = require_role("doctor", "admin")
require_receptionist = require_role("receptionist", "admin")
require_any_role = require_role("admin", "doctor", "receptionist")