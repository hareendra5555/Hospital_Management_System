from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import get_settings

settings = get_settings()

# CryptContext tells passlib which algorithm to use
# bcrypt is the industry standard for password hashing
# auto means it will automatically use the latest recommended settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


# ── Password utilities ───────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Converts "mysecretpass" → "$2b$12$randomsalthashstring..."
    bcrypt adds a random salt automatically — two hashes of the
    same password will always be different. This prevents rainbow table attacks.
    You NEVER store plain passwords. Ever.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a stored hash.
    passlib handles the salt extraction automatically.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT utilities ────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT token.

    data = {"sub": str(user_id), "role": "admin", "email": "user@x.com"}

    The token has 3 parts: header.payload.signature
    - header: algorithm used
    - payload: your data + expiry (readable by anyone)
    - signature: HMAC of header+payload using SECRET_KEY (only your server can verify)

    WHY is this secure?
    Anyone can READ the payload — it's just base64 encoded.
    But they can't FORGE a valid signature without the SECRET_KEY.
    So even if someone changes "role": "admin" in the payload,
    the signature won't match and the token is rejected.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Verifies and decodes a JWT token.
    Raises 401 if token is invalid, expired, or tampered with.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )