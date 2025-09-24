from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from models import Contest, ContestCreate, PrizeStructure, HomeSlider, Withdrawal, WithdrawalStatus
from database import get_database
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import logging
from lottery_logic import conduct_lottery_draw, get_contest_statistics

logger = logging.getLogger(__name__)
router = APIRouter()
@router.get("/contests/{contest_id}/overview")
async def get_contest_overview(contest_id: str):
    """Return contest document with derived totals and categories."""
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(status_code=400, detail="Invalid contest ID")
    db = get_database()
    contest = await db.contests.find_one({"_id": ObjectId(contest_id)})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    contest["id"] = str(contest["_id"]);
    del contest["_id"]
    return contest

@router.get("/contests/{contest_id}/purchases")
async def get_contest_purchases(contest_id: str, categoryId: int | None = None, limit: int = 100, skip: int = 0):
    """List purchased seats with buyer details, optional category filter."""
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(status_code=400, detail="Invalid contest ID")
    db = get_database()
    match = {"contestId": ObjectId(contest_id), "status": "purchased"}
    if categoryId:
        match["categoryId"] = categoryId

    pipeline = [
        {"$match": match},
        {"$sort": {"categoryId": 1, "seatNumber": 1}},
        {"$skip": int(skip)},
        {"$limit": int(limit)},
        {"$lookup": {"from": "users", "localField": "userId", "foreignField": "_id", "as": "user"}},
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "seatNumber": 1,
            "categoryId": 1,
            "categoryName": 1,
            "ticketPrice": 1,
            "userId": "$user.userId",
            "userName": "$user.userName",
            "email": "$user.email",
            "phoneNumber": "$user.phoneNumber",
        }}
    ]
    items = await db.purchased_seats.aggregate(pipeline).to_list(length=None)

    total = await db.purchased_seats.count_documents(match)

    # category breakdown
    cat_pipeline = [
        {"$match": match},
        {"$group": {"_id": "$categoryId", "categoryName": {"$first": "$categoryName"}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    categories = await db.purchased_seats.aggregate(cat_pipeline).to_list(length=None)
    return {"total": total, "items": items, "byCategory": categories}

# Admin authentication removed - all admin endpoints are now public

@router.post("/contests", response_model=dict)
async def create_contest(contest: dict):
    """Create a new contest. Accepts full contest JSON with optional categories.

    If `categories` are not provided, default 10 categories will be created.
    If provided, totals are derived when missing.
    """
    database = get_database()

    contest_dict = dict(contest)

    # Minimal required fields: totalPrizeMoney, ticketPrice. contestName optional
    if "totalPrizeMoney" not in contest_dict:
        raise HTTPException(status_code=400, detail="totalPrizeMoney is required")
    if "ticketPrice" not in contest_dict:
        raise HTTPException(status_code=400, detail="ticketPrice is required")

    # Categories
    if not contest_dict.get("categories"):
        contest_dict["categories"] = [
            {"categoryId": 1, "categoryName": "Bike", "seatRangeStart": 1, "seatRangeEnd": 1000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 2, "categoryName": "Auto", "seatRangeStart": 1001, "seatRangeEnd": 2000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 3, "categoryName": "Car", "seatRangeStart": 2001, "seatRangeEnd": 3000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 4, "categoryName": "Jeep", "seatRangeStart": 3001, "seatRangeEnd": 4000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 5, "categoryName": "Van", "seatRangeStart": 4001, "seatRangeEnd": 5000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 6, "categoryName": "Bus", "seatRangeStart": 5001, "seatRangeEnd": 6000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 7, "categoryName": "Lorry", "seatRangeStart": 6001, "seatRangeEnd": 7000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 8, "categoryName": "Train", "seatRangeStart": 7001, "seatRangeEnd": 8000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 9, "categoryName": "Helicopter", "seatRangeStart": 8001, "seatRangeEnd": 9000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
            {"categoryId": 10, "categoryName": "Airplane", "seatRangeStart": 9001, "seatRangeEnd": 10000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0}
        ]

    # Set defaults
    from datetime import timedelta
    now = datetime.now()
    contest_dict.setdefault("contestName", f"Rs {int(contest_dict['ticketPrice'])} Contest")
    contest_dict.setdefault("totalWinners", 0)
    contest_dict.setdefault("cashbackforhighest", None)
    contest_dict.setdefault("status", "active")
    contest_dict.setdefault("contestStartDate", now)
    contest_dict.setdefault("contestEndDate", now + timedelta(days=7))
    contest_dict.setdefault("drawDate", now + timedelta(days=8))

    # Derive totals if not present
    if "totalSeats" not in contest_dict or "availableSeats" not in contest_dict:
        total_seats = sum(int(c.get("totalSeats", 0)) for c in contest_dict["categories"])
        purchased = sum(int(c.get("purchasedSeats", 0)) for c in contest_dict["categories"])
        contest_dict["totalSeats"] = contest_dict.get("totalSeats", total_seats)
        contest_dict["availableSeats"] = contest_dict.get("availableSeats", total_seats - purchased)
        contest_dict["purchasedSeats"] = contest_dict.get("purchasedSeats", purchased)

    contest_dict["createdAt"] = datetime.now()
    contest_dict["updatedAt"] = datetime.now()

    result = await database.contests.insert_one(contest_dict)

    return {
        "message": "Contest created successfully",
        "contestId": str(result.inserted_id),
        "contestName": contest_dict.get("contestName")
    }

@router.delete("/contests/{contest_id}")
async def delete_contest(contest_id: str):
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(status_code=400, detail="Invalid contest ID")
    database = get_database()
    res = await database.contests.delete_one({"_id": ObjectId(contest_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contest not found")
    return {"message": "Contest deleted"}

@router.post("/contests/{contest_id}/prize-structure")
async def add_prize_structure(
    contest_id: str,
    prize_ranks: List[dict]
):
    """Add prize structure to a contest.

    Accepts a list of objects with fields: prizeRank (position), prizeAmount,
    numberOfWinners, optional winnersSeatNumbers (array of seat numbers).
    """
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    # Check if contest exists
    contest = await database.contests.find_one({"_id": ObjectId(contest_id)})
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )
    
    # Replace existing prize structure for this contest to avoid duplicates
    await database.prize_structure.delete_many({"contestId": ObjectId(contest_id)})

    # Create prize structure records
    prize_records = []
    for prize in prize_ranks:
        prize_record = {
            "contestId": ObjectId(contest_id),
            "prizeRank": prize["prizeRank"],
            "prizeAmount": prize["prizeAmount"],
            "numberOfWinners": prize["numberOfWinners"],
            "prizeDescription": prize.get("prizeDescription", f"Rank {prize['prizeRank']}"),
            "winnersSeatNumbers": prize.get("winnersSeatNumbers"),
            "createdAt": datetime.now()
        }
        prize_records.append(prize_record)
    
    await database.prize_structure.insert_many(prize_records)
    
    return {
        "message": "Prize structure added successfully",
        "contestId": contest_id,
        "prizesAdded": len(prize_records)
    }

@router.get("/contests/{contest_id}/prize-structure")
async def get_prize_structure(contest_id: str):
    """Return saved prize structure for a contest, sorted by prizeRank."""
    database = get_database()

    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )

    cursor = database.prize_structure.find({"contestId": ObjectId(contest_id)}).sort("prizeRank", 1)
    items: list[dict] = []
    async for doc in cursor:
        items.append({
            "id": str(doc.get("_id")),
            "prizeRank": doc.get("prizeRank"),
            "prizeAmount": doc.get("prizeAmount"),
            "numberOfWinners": doc.get("numberOfWinners"),
            "prizeDescription": doc.get("prizeDescription"),
            "winnersSeatNumbers": doc.get("winnersSeatNumbers") or []
        })

    return {"items": items}

@router.post("/contests/{contest_id}/announce-prize")
async def announce_prize_winners(contest_id: str):
    """Announce prize winners and credit amounts to wallets"""
    try:
        result = await conduct_lottery_draw(contest_id)
        # Update the response to reflect prize announcement
        result["announceTime"] = result.get("drawDate")
        result["message"] = "Prize winners announced and amounts credited to wallets successfully"
        return result
    except Exception as e:
        logger.error(f"Error announcing prize winners: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/contests/{contest_id}/statistics")
async def get_contest_admin_stats(contest_id: str):
    """Get detailed contest statistics for admin"""
    try:
        stats = await get_contest_statistics(contest_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting contest statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/withdrawals")
async def get_all_withdrawals(
    status: Optional[WithdrawalStatus] = None,
    limit: int = 20,
    skip: int = 0
):
    """Get all withdrawal requests - returns all withdrawals with full details"""
    try:
        database = get_database()
        
        query = {}
        if status:
            query["status"] = status
        
        withdrawals = []
        cursor = database.withdrawals.find(query).sort("createdAt", -1).skip(skip).limit(limit)
        
        async for withdrawal in cursor:
            try:
                # Get user details
                user = await database.users.find_one({"_id": withdrawal["userId"]})
                # Get bank details
                bank_details = await database.bank_details.find_one({"_id": withdrawal["bankDetailsId"]})
                
                withdrawal["id"] = str(withdrawal["_id"])
                del withdrawal["_id"]
                # Normalize non-JSON types
                if isinstance(withdrawal.get("userId"), ObjectId):
                    withdrawal["userId"] = str(withdrawal["userId"])
                if isinstance(withdrawal.get("bankDetailsId"), ObjectId):
                    withdrawal["bankDetailsId"] = str(withdrawal["bankDetailsId"])
                # Ensure enums are serialized to string values
                if isinstance(withdrawal.get("status"), WithdrawalStatus):
                    withdrawal["status"] = withdrawal["status"].value
                if isinstance(withdrawal.get("withdrawalMethod"), str) is False and withdrawal.get("withdrawalMethod") is not None:
                    try:
                        withdrawal["withdrawalMethod"] = str(withdrawal["withdrawalMethod"])  # .value if Enum
                    except Exception:
                        pass
                withdrawal["user"] = {
                    "userId": user["userId"] if user else "N/A",
                    "userName": user["userName"] if user else "N/A",
                    "phoneNumber": user["phoneNumber"] if user else "N/A",
                    "email": user.get("email", "N/A") if user else "N/A"
                }
                withdrawal["bankDetails"] = {
                    "id": str(bank_details["_id"]) if bank_details else None,
                    "accountNumber": bank_details.get("accountNumber", "N/A") if bank_details else "N/A",
                    "accountHolderName": bank_details.get("accountHolderName", "N/A") if bank_details else "N/A",
                    "bankName": bank_details.get("bankName", "N/A") if bank_details else "N/A",
                    "ifscCode": bank_details.get("ifscCode", "N/A") if bank_details else "N/A",
                    "upiId": bank_details.get("upiId", "N/A") if bank_details else "N/A",
                    "place": bank_details.get("place", "N/A") if bank_details else "N/A",
                    "extraParameter1": bank_details.get("extraParameter1", "") if bank_details else "",
                    "isVerified": bank_details.get("isVerified", True) if bank_details else True,
                    "verifiedAt": bank_details.get("verifiedAt") if bank_details else None,
                    "createdAt": bank_details.get("createdAt") if bank_details else None,
                    "updatedAt": bank_details.get("updatedAt") if bank_details else None
                }
                
                withdrawals.append(withdrawal)
            except Exception as e:
                logger.error(f"Error processing withdrawal {withdrawal.get('_id', 'unknown')}: {e}")
                continue
        
        # Get total count for pagination
        try:
            total_count = await database.withdrawals.count_documents(query)
        except Exception as e:
            logger.warning(f"count_documents failed, using manual count: {e}")
            # Fallback: count manually if count_documents fails
            total_count = len([doc async for doc in database.withdrawals.find(query)])
        
        return {
            "withdrawals": withdrawals,
            "total": total_count,
            "limit": limit,
            "skip": skip,
            "hasMore": (skip + limit) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error in get_all_withdrawals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch withdrawals: {str(e)}"
        )

# =========================
# New public utility APIs
# =========================

@router.get("/contact")
async def get_contact_info():
    """Public: Get contact information (single document)."""
    db = get_database()
    doc = await db.settings.find_one({"key": "contact"})
    if not doc:
        return {"contactNo": "", "email": "", "website": ""}
    data = doc.get("value", {})
    return {
        "contactNo": data.get("contactNo", ""),
        "email": data.get("email", ""),
        "website": data.get("website", "")
    }

@router.put("/contact")
async def update_contact_info(payload: dict):
    """Public: Update contact information (no auth)."""
    db = get_database()
    value = {
        "contactNo": payload.get("contactNo", ""),
        "email": payload.get("email", ""),
        "website": payload.get("website", "")
    }
    await db.settings.update_one(
        {"key": "contact"},
        {"$set": {"key": "contact", "value": value, "updatedAt": datetime.now()}},
        upsert=True
    )
    return {"message": "Contact info saved"}

@router.get("/how-to-play")
async def get_how_to_play():
    """Public: Get how to play content in multiple languages."""
    db = get_database()
    doc = await db.settings.find_one({"key": "how_to_play"})
    if not doc:
        return {
            "english": "",
            "hindi": "",
            "kannada": ""
        }
    data = doc.get("value", {})
    return {
        "english": data.get("english", ""),
        "hindi": data.get("hindi", ""),
        "kannada": data.get("kannada", "")
    }

@router.put("/how-to-play")
async def update_how_to_play(payload: dict):
    """Public: Update how to play content (no auth)."""
    db = get_database()
    value = {
        "english": payload.get("english", ""),
        "hindi": payload.get("hindi", ""),
        "kannada": payload.get("kannada", "")
    }
    await db.settings.update_one(
        {"key": "how_to_play"},
        {"$set": {"key": "how_to_play", "value": value, "updatedAt": datetime.now()}},
        upsert=True
    )
    return {"message": "How to play content saved"}

@router.get("/payments")
async def get_payments(userId: Optional[str] = None, limit: int = 100, skip: int = 0):
    """Return wallet transactions. If userId provided, filter by that user.

    No auth. Returns credits and debits with pagination.
    """
    db = get_database()
    query = {}
    if userId:
        # Resolve by users.userId (string) to _id
        user = await db.users.find_one({"userId": userId})
        if not user:
            return {"total": 0, "items": []}
        query["userId"] = user["_id"]

    cursor = db.wallet_transactions.find(query).sort("createdAt", -1).skip(skip).limit(limit)
    items = []
    async for tx in cursor:
        tx["id"] = str(tx.pop("_id"))
        tx["userId"] = str(tx["userId"]) if isinstance(tx.get("userId"), ObjectId) else tx.get("userId")
        items.append(tx)

    total = await db.wallet_transactions.count_documents(query)
    return {"total": total, "items": items, "limit": limit, "skip": skip}

@router.get("/users/{user_id}/purchases")
async def get_user_purchases(user_id: str, limit: int = 100, skip: int = 0):
    """Get all seat purchases for a specific user by userId (string).
    
    Returns contest details, seat info, and purchase history.
    """
    db = get_database()
    
    # Find user by userId (string)
    user = await db.users.find_one({"userId": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all purchases for this user
    pipeline = [
        {"$match": {"userId": user["_id"], "status": "purchased"}},
        {"$sort": {"purchaseDate": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "contests",
                "localField": "contestId",
                "foreignField": "_id",
                "as": "contest"
            }
        },
        {"$unwind": {"path": "$contest", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "purchaseId": {"$toString": "$_id"},
                "seatNumber": 1,
                "categoryId": 1,
                "categoryName": 1,
                "ticketPrice": 1,
                "purchaseDate": 1,
                "contest": {
                    "id": {"$toString": "$contest._id"},
                    "contestName": "$contest.contestName",
                    "totalPrizeMoney": "$contest.totalPrizeMoney",
                    "status": "$contest.status",
                    "contestStartDate": "$contest.contestStartDate",
                    "contestEndDate": "$contest.contestEndDate",
                    "drawDate": "$contest.drawDate"
                }
            }
        }
    ]
    
    items = await db.purchased_seats.aggregate(pipeline).to_list(length=None)
    
    # Get total count
    total = await db.purchased_seats.count_documents({
        "userId": user["_id"], 
        "status": "purchased"
    })
    
    # Get summary stats
    stats_pipeline = [
        {"$match": {"userId": user["_id"], "status": "purchased"}},
        {
            "$group": {
                "_id": None,
                "totalPurchases": {"$sum": 1},
                "totalSpent": {"$sum": "$ticketPrice"},
                "contestsParticipated": {"$addToSet": "$contestId"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "totalPurchases": 1,
                "totalSpent": 1,
                "contestsParticipated": {"$size": "$contestsParticipated"}
            }
        }
    ]
    
    stats_result = await db.purchased_seats.aggregate(stats_pipeline).to_list(length=1)
    stats = stats_result[0] if stats_result else {
        "totalPurchases": 0,
        "totalSpent": 0,
        "contestsParticipated": 0
    }
    
    return {
        "userId": user_id,
        "userName": user.get("userName", ""),
        "total": total,
        "items": items,
        "limit": limit,
        "skip": skip,
        "stats": stats
    }

@router.post("/users/{user_id}/profile-picture")
async def upload_profile_picture(user_id: str, image: UploadFile = File(...)):
    """Upload/replace profile picture for a user identified by users.userId (string)."""
    db = get_database()
    user = await db.users.find_one({"userId": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    import os
    os.makedirs("static/uploads", exist_ok=True)
    base_name = os.path.basename(image.filename or "profile.jpg")
    timestamp = int(datetime.now().timestamp())
    file_name = f"pf_{user_id}_{timestamp}_{base_name}"
    file_path = os.path.join("static/uploads", file_name)
    with open(file_path, "wb") as f:
        f.write(await image.read())
    public_url = f"/static/uploads/{file_name}"

    await db.users.update_one({"_id": user["_id"]}, {"$set": {"profilePicture": public_url, "updatedAt": datetime.now()}})
    return {"message": "Profile picture updated", "imageUrl": public_url}

@router.delete("/users/{user_id}/profile-picture")
async def remove_profile_picture(user_id: str):
    """Remove profile picture (sets to None) for a user identified by users.userId (string)."""
    db = get_database()
    user = await db.users.find_one({"userId": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"profilePicture": None, "updatedAt": datetime.now()}})
    return {"message": "Profile picture removed"}

@router.get("/contests/{contest_id}/prizes-summary")
async def get_prizes_summary(contest_id: str):
    """Return prize structure with a winnersCount per prizeRank for the given contest.

    No auth. Uses contestId.
    """
    db = get_database()
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(status_code=400, detail="Invalid contest ID")

    # Prize structure
    prizes = []
    cursor = db.prize_structure.find({"contestId": ObjectId(contest_id)}).sort("prizeRank", 1)
    async for doc in cursor:
        prizes.append({
            "id": str(doc.get("_id")),
            "prizeRank": doc.get("prizeRank"),
            "prizeAmount": doc.get("prizeAmount"),
            "numberOfWinners": doc.get("numberOfWinners"),
            "prizeDescription": doc.get("prizeDescription"),
            "winnersSeatNumbers": doc.get("winnersSeatNumbers") or []
        })

    # Winners per prizeRank
    pipeline = [
        {"$match": {"contestId": ObjectId(contest_id)}},
        {"$group": {"_id": "$prizeRank", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    counts = {i["_id"]: i["count"] async for i in db.winners.aggregate(pipeline)}

    # Merge
    for p in prizes:
        p["winnersCount"] = counts.get(p["prizeRank"], 0)

    # Totals
    total_winners = sum(p.get("winnersCount", 0) for p in prizes)
    total_prize = sum((p.get("prizeAmount", 0) or 0) * (p.get("numberOfWinners", 0) or 0) for p in prizes)

    return {
        "contestId": contest_id,
        "totalWinners": total_winners,
        "totalPrizeConfigured": total_prize,
        "prizes": prizes
    }

@router.put("/contests/{contest_id}/prize-settings")
async def update_prize_settings(contest_id: str, payload: dict):
    """Update totalWinners and cashbackforhighest for a contest.
    
    Accepts: { "totalWinners": int, "cashbackforhighest": float }
    """
    db = get_database()
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(status_code=400, detail="Invalid contest ID")
    
    # Check if contest exists
    contest = await db.contests.find_one({"_id": ObjectId(contest_id)})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    update_data = {"updatedAt": datetime.now()}
    
    if "totalWinners" in payload:
        update_data["totalWinners"] = int(payload["totalWinners"])
    
    if "cashbackforhighest" in payload:
        update_data["cashbackforhighest"] = float(payload["cashbackforhighest"]) if payload["cashbackforhighest"] is not None else None
    
    await db.contests.update_one(
        {"_id": ObjectId(contest_id)},
        {"$set": update_data}
    )
    
    return {"message": "Prize settings updated successfully"}

@router.put("/withdrawals/{withdrawal_id}/status")
async def update_withdrawal_status(
    withdrawal_id: str,
    status: WithdrawalStatus,
    admin_notes: str = None
):
    """Update withdrawal status - automatically marks bank as verified"""
    database = get_database()
    
    if not ObjectId.is_valid(withdrawal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid withdrawal ID"
        )
    
    withdrawal = await database.withdrawals.find_one({"_id": ObjectId(withdrawal_id)})
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found"
        )
    
    update_data = {
        "status": status,
        "updatedAt": datetime.now()
    }
    
    if admin_notes:
        update_data["adminNotes"] = admin_notes
    
    if status == WithdrawalStatus.COMPLETED:
        update_data["processedDate"] = datetime.now()
        update_data["transactionId"] = f"TXN_{int(datetime.now().timestamp())}"
        
        # Auto-verify bank details when withdrawal is completed
        await database.bank_details.update_one(
            {"_id": withdrawal["bankDetailsId"]},
            {"$set": {"isVerified": True, "verifiedAt": datetime.now()}}
        )
        # Nothing to do on wallet here; debited at request time
        
    elif status == WithdrawalStatus.REJECTED:
        update_data["processedDate"] = datetime.now()
        # Refund the reserved amount if previously debited
        debited_txn = await database.wallet_transactions.find_one({
            "referenceId": str(withdrawal["_id"]),
            "category": "withdrawal",
            "transactionType": "debit"
        })
        already_refunded = await database.wallet_transactions.find_one({
            "referenceId": str(withdrawal["_id"]),
            "category": "withdrawal",
            "transactionType": "credit"
        })
        if debited_txn and not already_refunded:
            user = await database.users.find_one({"_id": withdrawal["userId"]})
            if user:
                amount = float(withdrawal.get("amount", 0) or 0)
                current_balance = float(user.get("walletBalance", 0) or 0)
                new_balance = current_balance + amount
                await database.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"walletBalance": new_balance}}
                )
                refund_txn = {
                    "userId": user["_id"],
                    "transactionId": f"WD_REFUND_{str(withdrawal['_id'])}",
                    "transactionType": "credit",
                    "amount": amount,
                    "description": "Withdrawal rejected - amount refunded",
                    "category": "withdrawal",
                    "balanceBefore": current_balance,
                    "balanceAfter": new_balance,
                    "status": "completed",
                    "referenceId": str(withdrawal["_id"]),
                    "createdAt": datetime.now()
                }
                await database.wallet_transactions.insert_one(refund_txn)
    
    await database.withdrawals.update_one(
        {"_id": ObjectId(withdrawal_id)},
        {"$set": update_data}
    )
    
    return {"message": f"Withdrawal status updated to {status}"}

@router.post("/home-sliders")
async def create_home_slider(
    title: str = Form(...),
    image: UploadFile = File(None),
    image_url: str | None = Form(None),
    link_url: str | None = Form(None),
    description: str | None = Form(None),
    order: int = Form(0)
):
    """Create home slider.

    Accepts either an uploaded file (`image`) or a direct `image_url`.
    If a file is uploaded, it is saved under `static/uploads/` and its
    public URL is returned as `/static/uploads/<filename>`.
    """
    database = get_database()

    saved_image_url = None
    if image is not None:
        # Save uploaded file
        uploads_dir = "static/uploads"
        import os
        os.makedirs(uploads_dir, exist_ok=True)
        # Make filename unique
        base_name = os.path.basename(image.filename or "upload.jpg")
        timestamp = int(datetime.now().timestamp())
        safe_name = f"{timestamp}_{base_name}"
        file_path = os.path.join(uploads_dir, safe_name)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        saved_image_url = f"/static/uploads/{safe_name}"
    elif image_url:
        saved_image_url = image_url
    else:
        raise HTTPException(status_code=400, detail="Either image file or image_url is required")

    slider = {
        "title": title,
        "imageUrl": saved_image_url,
        "linkUrl": link_url,
        "description": description,
        "order": order,
        "isActive": True,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }

    result = await database.home_sliders.insert_one(slider)

    return {
        "message": "Home slider created successfully",
        "sliderId": str(result.inserted_id),
        "imageUrl": saved_image_url
    }

@router.get("/home-sliders")
async def get_home_sliders():
    """Get all home sliders"""
    database = get_database()
    
    sliders = []
    cursor = database.home_sliders.find().sort("order", 1)
    
    async for slider in cursor:
        slider["id"] = str(slider["_id"])
        del slider["_id"]
        sliders.append(slider)
    
    return {"sliders": sliders}

@router.put("/home-sliders/{slider_id}")
async def update_home_slider(
    slider_id: str,
    title: str = None,
    image_url: str = None,
    link_url: str = None,
    description: str = None,
    order: int = None,
    is_active: bool = None
):
    """Update home slider"""
    database = get_database()
    
    if not ObjectId.is_valid(slider_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid slider ID"
        )
    
    update_data = {"updatedAt": datetime.now()}
    
    if title is not None:
        update_data["title"] = title
    if image_url is not None:
        update_data["imageUrl"] = image_url
    if link_url is not None:
        update_data["linkUrl"] = link_url
    if description is not None:
        update_data["description"] = description
    if order is not None:
        update_data["order"] = order
    if is_active is not None:
        update_data["isActive"] = is_active
    
    result = await database.home_sliders.update_one(
        {"_id": ObjectId(slider_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slider not found"
        )
    
    return {"message": "Home slider updated successfully"}

@router.delete("/home-sliders/{slider_id}")
async def delete_home_slider(slider_id: str):
    """Delete home slider"""
    database = get_database()
    
    if not ObjectId.is_valid(slider_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid slider ID"
        )
    
    result = await database.home_sliders.delete_one({"_id": ObjectId(slider_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slider not found"
        )
    
    return {"message": "Home slider deleted successfully"}

@router.get("/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard statistics"""
    database = get_database()
    
    # Get total users
    total_users = await database.users.count_documents({})
    active_users = await database.users.count_documents({"isActive": True})
    
    # Get total contests
    total_contests = await database.contests.count_documents({})
    active_contests = await database.contests.count_documents({"status": "active"})
    
    # Get total transactions
    total_transactions = await database.wallet_transactions.count_documents({})
    
    # Get pending withdrawals
    pending_withdrawals = await database.withdrawals.count_documents({"status": "pending"})
    
    # Get total prize money distributed
    pipeline = [
        {"$match": {"category": "prize_credit"}},
        {"$group": {"_id": None, "totalAmount": {"$sum": "$amount"}}}
    ]
    
    prize_money_result = await database.wallet_transactions.aggregate(pipeline).to_list(length=1)
    total_prize_money = prize_money_result[0]["totalAmount"] if prize_money_result else 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users
        },
        "contests": {
            "total": total_contests,
            "active": active_contests
        },
        "transactions": {
            "total": total_transactions
        },
        "withdrawals": {
            "pending": pending_withdrawals
        },
        "prizeMoney": {
            "totalDistributed": total_prize_money
        }
    }
