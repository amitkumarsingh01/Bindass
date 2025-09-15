from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import TokenData, User
from database import get_database
from config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()

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

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user data"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        userId: str = payload.get("sub")
        if userId is None:
            raise credentials_exception
        token_data = TokenData(userId=userId)
    except JWTError:
        raise credentials_exception
    
    return token_data

async def get_current_user(token_data: TokenData = Depends(verify_token)):
    """Get current authenticated user"""
    database = get_database()
    
    # Try to find user by userId first, then by phoneNumber
    user = await database.users.find_one({
        "$or": [
            {"userId": token_data.userId},
            {"phoneNumber": token_data.userId}
        ]
    })
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
