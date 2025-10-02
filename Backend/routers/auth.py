from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta, datetime
from models import UserCreate, UserLogin, UserResponse, Token, User, UserRegisterSimple
from auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from database import get_database
from config import settings
from services.email_service import EmailService
from pydantic import BaseModel, EmailStr
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/check-user")
async def check_user(email: str | None = None, userId: str | None = None, phoneNumber: str | None = None):
    """Quick availability check. Returns which identifiers already exist."""
    database = get_database()
    result = {"existsEmail": False, "existsUserId": False, "existsPhone": False}
    if email:
        normalized = (email or "").strip().lower()
        result["existsEmail"] = bool(await database.users.find_one({"email": normalized}, {"_id": 1}))
    if userId:
        result["existsUserId"] = bool(await database.users.find_one({"userId": userId}, {"_id": 1}))
    if phoneNumber:
        result["existsPhone"] = bool(await database.users.find_one({"phoneNumber": phoneNumber}, {"_id": 1}))
    return result

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register a new user"""
    database = get_database()
    
    # Normalize email
    normalized_email = (user.email or "").strip().lower()
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user document
    user_dict = user.dict()
    user_dict["email"] = normalized_email
    user_dict["password"] = hashed_password
    user_dict["walletBalance"] = 0.0
    user_dict["isActive"] = True
    
    # Insert user
    # Insert user (catch duplicate email at DB level)
    try:
        result = await database.users.insert_one(user_dict)
    except Exception as e:
        # Handle DuplicateKeyError for email unique index
        if hasattr(e, "details") and isinstance(getattr(e, "code", None), int):
            pass
        # Fallback string check
        if "duplicate key" in str(e).lower() and "email" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
        raise
    
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

    # Normalize email
    normalized_email = (payload.email or "").strip().lower()

    hashed_password = get_password_hash(payload.password)

    from datetime import datetime
    now = datetime.now()

    doc = {
        "userName": payload.userName,
        "userId": payload.userId,
        "email": normalized_email,
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

    # Insert user (catch duplicate email at DB level)
    try:
        res = await database.users.insert_one(doc)
    except Exception as e:
        if "duplicate key" in str(e).lower() and "email" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
        raise
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

# Forgot Password Models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email to user"""
    try:
        database = get_database()
        
        # Normalize email
        email = request.email.lower().strip()
        
        # Check if user exists
        user = await database.users.find_one({"email": email})
        if not user:
            # Don't reveal if email exists or not for security
            return {
                "message": "If an account with this email exists, you will receive a password reset link shortly.",
                "success": True
            }
        
        # Send reset email
        success = await EmailService.send_password_reset_email(email)
        
        if success:
            return {
                "message": "If an account with this email exists, you will receive a password reset link shortly.",
                "success": True
            }
        else:
            # Don't reveal email sending failure for security
            return {
                "message": "If an account with this email exists, you will receive a password reset link shortly.",
                "success": True
            }
            
    except Exception as e:
        logger.error(f"Error in forgot password: {e}")
        # Don't reveal internal errors
        return {
            "message": "If an account with this email exists, you will receive a password reset link shortly.",
            "success": True
        }

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset user password using token"""
    try:
        # Validate passwords match
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Validate password length (minimum 6 characters)
        if len(request.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Verify token
        try:
            user_info = await EmailService.verify_reset_token(request.token)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Update password
        database = get_database()
        hashed_password = get_password_hash(request.new_password)
        
        from bson import ObjectId
        result = await database.users.update_one(
            {"_id": ObjectId(user_info["userId"])},
            {
                "$set": {
                    "password": hashed_password,
                    "updatedAt": datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        # Mark token as used
        await EmailService.use_reset_token(request.token)
        
        logger.info(f"Password reset successful for user: {user_info['email']}")
        
        return {
            "message": "Password reset successful. You can now login with your new password.",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in reset password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting password"
        )

@router.get("/verify-reset-token/{token}")
async def verify_reset_token(token: str):
    """Verify if a reset token is valid (for frontend validation)"""
    try:
        user_info = await EmailService.verify_reset_token(token)
        return {
            "valid": True,
            "email": user_info["email"],
            "userName": user_info["userName"]
        }
    except ValueError:
        return {"valid": False}
