from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta
from models import UserCreate, UserLogin, UserResponse, Token, User, UserRegisterSimple
from auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from database import get_database
from config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register a new user"""
    database = get_database()
    
    # Only enforce uniqueness on email
    existing_by_email = await database.users.find_one({"email": user.email})
    if existing_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user document
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["walletBalance"] = 0.0
    user_dict["isActive"] = True
    
    # Insert user
    result = await database.users.insert_one(user_dict)
    
    # Fetch created user
    created_user = await database.users.find_one({"_id": result.inserted_id})
    
    # Remove password from response
    created_user["id"] = str(created_user["_id"])
    del created_user["_id"]
    del created_user["password"]
    
    return UserResponse(**created_user)

@router.post("/register-simple", response_model=UserResponse)
async def register_user_simple(payload: UserRegisterSimple):
    """Complete registration accepting all user parameters."""
    database = get_database()

    # Only enforce uniqueness on email
    existing_by_email = await database.users.find_one({"email": payload.email})
    if existing_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    hashed_password = get_password_hash(payload.password)

    from datetime import datetime
    now = datetime.now()

    doc = {
        "userName": payload.userName,
        "userId": payload.userId,
        "email": payload.email,
        "phoneNumber": payload.phoneNumber,
        "password": hashed_password,
        "profilePicture": payload.profilePicture,
        "city": payload.city or "",
        "state": payload.state or "",
        "walletBalance": 0.0,
        "isActive": True,
        "extraParameter1": payload.extraParameter1,
        "createdAt": now,
        "updatedAt": now,
    }

    res = await database.users.insert_one(doc)
    created = await database.users.find_one({"_id": res.inserted_id})
    created["id"] = str(created["_id"])
    del created["_id"]
    del created["password"]
    return UserResponse(**created)

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Login user and return access token"""
    # identifier can be email / phoneNumber / userId
    user = await authenticate_user(user_credentials.identifier, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect userId/phoneNumber or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.userId}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    user_dict = current_user.dict()
    user_dict["id"] = str(user_dict["id"])
    del user_dict["password"]
    return UserResponse(**user_dict)
