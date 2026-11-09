"""
Security: password hashing and JWT tokens.

How login works in this API (the "Bearer token" flow):
1. The user sends username + password to POST /auth/login.
2. We check the password against the stored hash.
3. If it matches, we create a JWT (JSON Web Token) — a signed string that
   says "this is user X, valid until time Y".
4. The client sends that token on every later request in the header:
       Authorization: Bearer <token>
5. We verify the signature; if it's valid and not expired, we know who the
   user is without asking for the password again.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.database import get_db
from app.models import User

# Tells FastAPI (and the /docs page) where clients get a token from.
# This is what adds the "Authorize" button in Swagger UI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------- Passwords ----------
def hash_password(password: str) -> str:
    """Turn a plain password into a salted bcrypt hash (one-way, can't be reversed)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check whether a plain password matches a stored hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


# ---------- JWT tokens ----------
def create_access_token(user_id: int) -> str:
    """Create a signed token that identifies the user and expires later."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # "sub" (subject) and "exp" (expiry) are standard JWT field names.
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency for protected endpoints.

    Any endpoint that adds `current_user: User = Depends(get_current_user)`
    can only be called with a valid token — otherwise the client gets 401.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        # Covers bad signature, expired token, and malformed payload.
        raise credentials_error

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_error
    return user
