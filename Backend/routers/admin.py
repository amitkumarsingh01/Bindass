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

# Admin authentication removed - all admin endpoints are now public

@router.post("/contests", response_model=dict)
async def create_contest(contest: ContestCreate):
    """Create a new contest"""
    database = get_database()
    
    # Create contest with default categories
    contest_dict = contest.dict()
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
    contest_dict["createdAt"] = datetime.now()
    contest_dict["updatedAt"] = datetime.now()
    
    result = await database.contests.insert_one(contest_dict)
    
    return {
        "message": "Contest created successfully",
        "contestId": str(result.inserted_id),
        "contestName": contest.contestName
    }

@router.post("/contests/{contest_id}/prize-structure")
async def add_prize_structure(
    contest_id: str,
    prize_ranks: List[dict]
):
    """Add prize structure to a contest"""
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
    
    # Create prize structure records
    prize_records = []
    for prize in prize_ranks:
        prize_record = {
            "contestId": ObjectId(contest_id),
            "prizeRank": prize["prizeRank"],
            "prizeAmount": prize["prizeAmount"],
            "numberOfWinners": prize["numberOfWinners"],
            "prizeDescription": prize.get("prizeDescription", f"Rank {prize['prizeRank']}"),
            "createdAt": datetime.now()
        }
        prize_records.append(prize_record)
    
    await database.prize_structure.insert_many(prize_records)
    
    return {
        "message": "Prize structure added successfully",
        "contestId": contest_id,
        "prizesAdded": len(prize_records)
    }

@router.post("/contests/{contest_id}/draw")
async def conduct_draw(contest_id: str):
    """Conduct lottery draw for a contest"""
    try:
        result = await conduct_lottery_draw(contest_id)
        return result
    except Exception as e:
        logger.error(f"Error conducting draw: {e}")
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
    """Get all withdrawal requests"""
    database = get_database()
    
    query = {}
    if status:
        query["status"] = status
    
    withdrawals = []
    cursor = database.withdrawals.find(query).sort("createdAt", -1).skip(skip).limit(limit)
    
    async for withdrawal in cursor:
        # Get user details
        user = await database.users.find_one({"_id": withdrawal["userId"]})
        # Get bank details
        bank_details = await database.bank_details.find_one({"_id": withdrawal["bankDetailsId"]})
        
        withdrawal["id"] = str(withdrawal["_id"])
        del withdrawal["_id"]
        withdrawal["user"] = {
            "userId": user["userId"] if user else "N/A",
            "userName": user["userName"] if user else "N/A",
            "phoneNumber": user["phoneNumber"] if user else "N/A"
        }
        withdrawal["bankDetails"] = bank_details
        
        withdrawals.append(withdrawal)
    
    return {
        "withdrawals": withdrawals,
        "total": len(withdrawals),
        "limit": limit,
        "skip": skip
    }

@router.put("/withdrawals/{withdrawal_id}/status")
async def update_withdrawal_status(
    withdrawal_id: str,
    status: WithdrawalStatus,
    admin_notes: str = None
):
    """Update withdrawal status"""
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
    elif status == WithdrawalStatus.REJECTED:
        update_data["processedDate"] = datetime.now()
    
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
