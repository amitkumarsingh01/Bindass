from fastapi import APIRouter, HTTPException, Depends, status
from models import User, BankDetails, BankDetailsCreate, UserResponse, UserCreate
from auth import get_current_user, resolve_user
from database import get_database
from pymongo import ReturnDocument
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
    update: dict,
    current_user: User = Depends(resolve_user)
):
    """Update user profile information (accepts JSON body)."""
    database = get_database()
    from datetime import datetime

    allowed_fields = {"userName", "city", "state", "profilePicture", "extraParameter1"}
    update_data = {k: v for k, v in (update or {}).items() if k in allowed_fields}

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    update_data["updatedAt"] = datetime.now()

    result = await database.users.update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

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
    """Add or update bank details for user (idempotent upsert)."""
    database = get_database()
    from datetime import datetime

    try:
        updates = bank_details.dict()
        updates["isVerified"] = False
        updates["updatedAt"] = datetime.now()

        # Upsert by userId, set createdAt only on insert
        doc = await database.bank_details.find_one_and_update(
            {"userId": current_user.id},
            {
                "$set": updates,
                "$setOnInsert": {
                    "userId": current_user.id,
                    "createdAt": datetime.now(),
                },
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        # Some motor versions require a second read after upsert to get the doc
        if not doc:
            doc = await database.bank_details.find_one({"userId": current_user.id})

        if not doc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save bank details")

        out = doc.copy()
        out["id"] = str(out.pop("_id"))
        # Normalize ObjectId fields for JSON safety
        if isinstance(out.get("userId"), ObjectId):
            out["userId"] = str(out["userId"])
        message = "Bank details saved"
        return {"message": message, "bankDetails": out}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error saving bank details for user {current_user.userId}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error saving bank details")

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
    if isinstance(bank_details.get("userId"), ObjectId):
        bank_details["userId"] = str(bank_details["userId"])
    
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

# Listing and lookup endpoints (no auth)

@router.get("/")
async def list_users(
    q: str | None = None,
    limit: int = 20,
    skip: int = 0,
    sort: str = "-createdAt"
):
    database = get_database()
    query: dict = {}
    if q:
        query = {
            "$or": [
                {"userName": {"$regex": q, "$options": "i"}},
                {"userId": {"$regex": q, "$options": "i"}},
                {"email": {"$regex": q, "$options": "i"}},
                {"phoneNumber": {"$regex": q, "$options": "i"}},
            ]
        }
    sort_dir = -1 if sort.startswith('-') else 1
    sort_field = sort[1:] if sort.startswith('-') else sort

    total = await database.users.count_documents(query)
    items = []
    cursor = database.users.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)
    async for u in cursor:
        u_out = u.copy()
        u_out["id"] = str(u_out.pop("_id"))
        u_out.pop("password", None)
        items.append(u_out)

    return {"total": total, "limit": limit, "skip": skip, "items": items}


@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    database = get_database()
    user = await database.users.find_one({"userId": user_id})
    if not user and ObjectId.is_valid(user_id):
        user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    bank = await database.bank_details.find_one({"userId": user["_id"]})
    out = user.copy()
    out["id"] = str(out.pop("_id"))
    out.pop("password", None)
    if bank:
        b = bank.copy()
        b["id"] = str(b.pop("_id"))
        out["bankDetails"] = b
    return out


# -------------------------------
# Basic admin-style user mutation
# -------------------------------

@router.post("/")
async def create_user(payload: UserCreate):
    database = get_database()
    exists = await database.users.find_one({
        "$or": [
            {"userId": payload.userId},
            {"email": payload.email},
            {"phoneNumber": payload.phoneNumber},
        ]
    })
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    doc = payload.dict()
    # Do NOT hash because security removed; if you prefer hashed, I can wire it back
    doc["walletBalance"] = 0.0
    doc["isActive"] = True
    from datetime import datetime
    doc["createdAt"] = datetime.now()
    doc["updatedAt"] = datetime.now()

    res = await database.users.insert_one(doc)
    return {"id": str(res.inserted_id)}


@router.put("/{user_id}")
async def update_user(user_id: str, update: dict):
    database = get_database()
    filter_q = {"userId": user_id}
    if ObjectId.is_valid(user_id):
        filter_q = {"_id": ObjectId(user_id)}

    update = {k: v for k, v in (update or {}).items() if k not in {"_id", "id", "password"}}
    if not update:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    from datetime import datetime
    update["updatedAt"] = datetime.now()
    res = await database.users.update_one(filter_q, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"updated": res.modified_count}


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    database = get_database()
    filter_q = {"userId": user_id}
    if ObjectId.is_valid(user_id):
        filter_q = {"_id": ObjectId(user_id)}
    # cascade deletes minimal (bank details)
    user = await database.users.find_one(filter_q)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await database.bank_details.delete_many({"userId": user["_id"]})
    res = await database.users.delete_one(filter_q)
    return {"deleted": res.deleted_count}
