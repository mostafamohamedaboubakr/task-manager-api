"""
Auth endpoints: register, login, and "who am I".

A router groups related endpoints. main.py plugs each router into the app.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate, UserOut
from app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new account."""
    # Reject duplicates with 409 Conflict (a clearer error than a DB crash).
    existing = db.scalar(
        select(User).where(or_(User.username == user_in.username, User.email == user_in.email))
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # reload to get the generated id and created_at
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Log in and receive a JWT access token.

    Uses the standard OAuth2 form format (username + password as form fields),
    which is what the "Authorize" button on /docs sends.
    """
    user = db.scalar(select(User).where(User.username == form.username))
    # Same error for "no such user" and "wrong password" so attackers
    # can't discover which usernames exist.
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    """Return the logged-in user. A simple way to test that your token works."""
    return current_user
