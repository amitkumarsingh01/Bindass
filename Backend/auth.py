from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi import Header, Query
from models import TokenData, User
from database import get_database
from config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def verify_token(authorization: str | None = Header(None)):
    """Verify JWT token from Authorization header if present; otherwise return None.
    This avoids registering a security scheme in OpenAPI.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    try:
        token = authorization.split(" ", 1)[1]
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str | None = payload.get("sub")
        if not user_id:
            return None
        return TokenData(userId=user_id)
    except JWTError:
        return None

async def get_current_user(x_user_id: str | None = Header(None), token_data: TokenData | None = Depends(verify_token)):
    """Resolve current user by header `X-User-Id` (preferred) or optional JWT token.
    This removes the hard dependency on Authorization and allows simple userId-based access.
    """
    database = get_database()

    # 1) Prefer header-provided userId
    candidate = x_user_id or (token_data.userId if token_data else None)
    if not candidate:
        # As a last resort, allow anonymous 'guest' if exists
        guest = await database.users.find_one({"userId": "guest"})
        if guest:
            return User(**guest)
        # Otherwise signal missing identity
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide X-User-Id header")

    user = await database.users.find_one({
        "$or": [
            {"userId": candidate},
            {"phoneNumber": candidate},
            {"email": candidate}
        ]
    })
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return User(**user)

async def resolve_user(
    userId: str | None = Query(None),
    x_user_id: str | None = Header(None),
    token_data: TokenData | None = Depends(verify_token)
):
    """Resolve a user by explicit query param `userId`, header `X-User-Id`, or optional JWT.
    Prefer query param > header > token. No Authorization required.
    """
    chosen = userId or x_user_id or (token_data.userId if token_data else None)
    if not chosen:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide userId query or X-User-Id header")
    database = get_database()
    user = await database.users.find_one({
        "$or": [
            {"userId": chosen},
            {"phoneNumber": chosen},
            {"email": chosen}
        ]
    })
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return User(**user)

def _password_matches(stored: str, provided: str) -> bool:
    if not provided:
        return False
    try:
        if stored and stored.startswith('$2'):
            return pwd_context.verify(provided, stored)
    except Exception:
        pass
    return stored == provided

async def get_user_with_password(
    userId: str | None = Query(None),
    x_user_id: str | None = Header(None),
    x_user_password: str | None = Header(None),
    token_data: TokenData | None = Depends(verify_token)
):
    """Resolve user (query/header) and VERIFY password."""
    u = await resolve_user(userId=userId, x_user_id=x_user_id, token_data=token_data)
    if not x_user_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password required")
    database = get_database()
    user_doc = await database.users.find_one({"_id": u.id})
    if not user_doc or not verify_password(x_user_password, user_doc.get("password", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    return u

async def authenticate_user(userId: str, password: str):
    """Authenticate user with email/phoneNumber/userId and password"""
    database = get_database()
    
    # Try to find user by any identifier
    user = await database.users.find_one({
        "$or": [
            {"userId": userId},
            {"phoneNumber": userId},
            {"email": userId}
        ]
    })
    
    if not user:
        return False
    
    if not verify_password(password, user["password"]):
        return False
    
    return User(**user)
