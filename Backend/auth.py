from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Header
from models import TokenData, User
from database import get_database
from config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling (optional)
security = HTTPBearer(auto_error=False)

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

async def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """Verify JWT token if present; otherwise return None."""
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
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
            {"phoneNumber": candidate}
        ]
    })
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return User(**user)

async def authenticate_user(userId: str, password: str):
    """Authenticate user with userId/phoneNumber and password"""
    database = get_database()
    
    # Try to find user by userId first, then by phoneNumber
    user = await database.users.find_one({
        "$or": [
            {"userId": userId},
            {"phoneNumber": userId}
        ]
    })
    
    if not user:
        return False
    
    if not verify_password(password, user["password"]):
        return False
    
    return User(**user)
