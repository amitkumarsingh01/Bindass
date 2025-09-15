from fastapi import APIRouter, HTTPException, Depends, status
from models import User, BankDetails, BankDetailsCreate, UserResponse
from auth import get_current_user, resolve_user
from database import get_database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(resolve_user)):
    """Get user profile information"""
    user_dict = current_user.dict()
    user_dict["id"] = str(user_dict["id"])
    del user_dict["password"]
    return UserResponse(**user_dict)

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    userName: str = None,
    city: str = None,
    state: str = None,
    profilePicture: str = None,
    extraParameter1: str = None,
    current_user: User = Depends(resolve_user)
):
    """Update user profile information"""
    database = get_database()
    
    update_data = {}
    if userName is not None:
        update_data["userName"] = userName
    if city is not None:
        update_data["city"] = city
    if state is not None:
        update_data["state"] = state
    if profilePicture is not None:
        update_data["profilePicture"] = profilePicture
    if extraParameter1 is not None:
        update_data["extraParameter1"] = extraParameter1
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updatedAt"] = current_user.updatedAt
    
    result = await database.users.update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    # Fetch updated user
    updated_user = await database.users.find_one({"_id": current_user.id})
    user_dict = User(**updated_user).dict()
    user_dict["id"] = str(user_dict["id"])
    del user_dict["password"]
    
    return UserResponse(**user_dict)

@router.post("/bank-details")
async def add_bank_details(
    bank_details: BankDetailsCreate,
    current_user: User = Depends(resolve_user)
):
    """Add or update bank details for user"""
    database = get_database()
    
    bank_details_dict = bank_details.dict()
    bank_details_dict["userId"] = current_user.id
    bank_details_dict["isVerified"] = False
    
    # Check if user already has bank details
    existing_bank = await database.bank_details.find_one({"userId": current_user.id})
    
    if existing_bank:
        # Update existing bank details
        result = await database.bank_details.update_one(
            {"userId": current_user.id},
            {"$set": bank_details_dict}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update bank details"
            )
        message = "Bank details updated successfully"
    else:
        # Create new bank details
        result = await database.bank_details.insert_one(bank_details_dict)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add bank details"
            )
        message = "Bank details added successfully"
    
    return {"message": message}

@router.get("/bank-details")
async def get_bank_details(current_user: User = Depends(resolve_user)):
    """Get user's bank details"""
    database = get_database()
    
    bank_details = await database.bank_details.find_one({"userId": current_user.id})
    
    if not bank_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank details not found"
        )
    
    bank_details["id"] = str(bank_details["_id"])
    del bank_details["_id"]
    
    return bank_details

@router.delete("/bank-details")
async def delete_bank_details(current_user: User = Depends(resolve_user)):
    """Delete user's bank details"""
    database = get_database()
    
    result = await database.bank_details.delete_one({"userId": current_user.id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank details not found"
        )
    
    return {"message": "Bank details deleted successfully"}

@router.get("/wallet/balance")
async def get_wallet_balance(current_user: User = Depends(resolve_user)):
    """Get user's wallet balance"""
    return {
        "userId": current_user.userId,
        "walletBalance": current_user.walletBalance,
        "isActive": current_user.isActive
    }
