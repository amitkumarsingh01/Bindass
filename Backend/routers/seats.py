from fastapi import APIRouter, HTTPException, Depends, status
from models import User, SeatPurchase, PurchasedSeat, PaymentMethod, PurchaseStatus
from auth import resolve_user
from database import get_database
from bson import ObjectId
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Category mapping for seat ranges
CATEGORY_RANGES = {
    1: {"name": "Bike", "start": 1, "end": 1000},
    2: {"name": "Auto", "start": 1001, "end": 2000},
    3: {"name": "Car", "start": 2001, "end": 3000},
    4: {"name": "Jeep", "start": 3001, "end": 4000},
    5: {"name": "Van", "start": 4001, "end": 5000},
    6: {"name": "Bus", "start": 5001, "end": 6000},
    7: {"name": "Lorry", "start": 6001, "end": 7000},
    8: {"name": "Train", "start": 7001, "end": 8000},
    9: {"name": "Helicopter", "start": 8001, "end": 9000},
    10: {"name": "Airplane", "start": 9001, "end": 10000}
}

def get_category_for_seat(seat_number: int) -> dict:
    """Get category information for a seat number"""
    for category_id, info in CATEGORY_RANGES.items():
        if info["start"] <= seat_number <= info["end"]:
            return {"categoryId": category_id, "categoryName": info["name"]}
    raise ValueError(f"Invalid seat number: {seat_number}")

@router.get("/{contest_id}/available")
async def get_available_seats(
    contest_id: str,
    category_id: int = None,
    limit: int = 100,
    skip: int = 0
):
    """Get available seats for a contest, optionally filtered by category"""
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    # Check if contest exists and is active
    contest = await database.contests.find_one({"_id": ObjectId(contest_id)})
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )
    
    if contest["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contest is not active"
        )
    
    # Get purchased seats
    query = {"contestId": ObjectId(contest_id), "status": "purchased"}
    if category_id:
        query["categoryId"] = category_id
    
    purchased_seats = set()
    cursor = database.purchased_seats.find(query, {"seatNumber": 1})
    async for seat in cursor:
        purchased_seats.add(seat["seatNumber"])
    
    # Generate available seats
    available_seats = []
    if category_id:
        if category_id not in CATEGORY_RANGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category ID"
            )
        start = CATEGORY_RANGES[category_id]["start"]
        end = CATEGORY_RANGES[category_id]["end"]
    else:
        start = 1
        end = 10000
    
    count = 0
    for seat_num in range(start, end + 1):
        if seat_num not in purchased_seats:
            available_seats.append(seat_num)
            count += 1
            if count >= limit:
                break
    
    return {
        "contestId": contest_id,
        "categoryId": category_id,
        "availableSeats": available_seats,
        "totalAvailable": len(available_seats),
        "limit": limit,
        "skip": skip
    }

@router.post("/purchase")
async def purchase_seats(
    seat_purchase: SeatPurchase,
    current_user: User = Depends(resolve_user)
):
    """Purchase seats for a contest"""
    database = get_database()
    
    if not ObjectId.is_valid(seat_purchase.contestId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    # Check if contest exists and is active
    contest = await database.contests.find_one({"_id": ObjectId(seat_purchase.contestId)})
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )
    
    if contest["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contest is not active"
        )
    
    # Validate seat numbers
    for seat_num in seat_purchase.seatNumbers:
        if not (1 <= seat_num <= 10000):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid seat number: {seat_num}. Must be between 1-10000"
            )
    
    # Check if seats are already purchased
    existing_seats = await database.purchased_seats.find({
        "contestId": ObjectId(seat_purchase.contestId),
        "seatNumber": {"$in": seat_purchase.seatNumbers},
        "status": "purchased"
    }).to_list(length=None)
    
    if existing_seats:
        occupied_seats = [seat["seatNumber"] for seat in existing_seats]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Seats already purchased: {occupied_seats}"
        )
    
    # Calculate total amount
    total_amount = len(seat_purchase.seatNumbers) * contest["ticketPrice"]
    
    # Check wallet balance if payment method is wallet
    if seat_purchase.paymentMethod == PaymentMethod.WALLET:
        if current_user.walletBalance < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance"
            )
    
    # Generate transaction ID
    transaction_id = str(uuid.uuid4())
    
    # Create purchased seat records
    purchased_seats = []
    for seat_num in seat_purchase.seatNumbers:
        category_info = get_category_for_seat(seat_num)
        
        seat_record = {
            "contestId": ObjectId(seat_purchase.contestId),
            "userId": current_user.id,
            "seatNumber": seat_num,
            "categoryId": category_info["categoryId"],
            "categoryName": category_info["categoryName"],
            "ticketPrice": contest["ticketPrice"],
            "purchaseDate": datetime.now(),
            "transactionId": transaction_id,
            "paymentMethod": seat_purchase.paymentMethod,
            "status": PurchaseStatus.PURCHASED,
            "isWinner": False,
            "prizeAmount": 0.0,
            "createdAt": datetime.now()
        }
        purchased_seats.append(seat_record)
    
    # Start transaction
    try:
        # Insert purchased seats
        await database.purchased_seats.insert_many(purchased_seats)
        
        # Update contest statistics
        await database.contests.update_one(
            {"_id": ObjectId(seat_purchase.contestId)},
            {
                "$inc": {
                    "purchasedSeats": len(seat_purchase.seatNumbers),
                    "availableSeats": -len(seat_purchase.seatNumbers)
                }
            }
        )
        
        # Update category statistics
        category_updates = {}
        for seat_record in purchased_seats:
            cat_id = seat_record["categoryId"]
            if cat_id not in category_updates:
                category_updates[cat_id] = 0
            category_updates[cat_id] += 1
        
        for cat_id, count in category_updates.items():
            await database.contests.update_one(
                {
                    "_id": ObjectId(seat_purchase.contestId),
                    "categories.categoryId": cat_id
                },
                {
                    "$inc": {
                        "categories.$.purchasedSeats": count,
                        "categories.$.availableSeats": -count
                    }
                }
            )
        
        # Handle wallet payment
        if seat_purchase.paymentMethod == PaymentMethod.WALLET:
            # Deduct from wallet
            new_balance = current_user.walletBalance - total_amount
            await database.users.update_one(
                {"_id": current_user.id},
                {"$set": {"walletBalance": new_balance}}
            )
            
            # Create wallet transaction
            wallet_transaction = {
                "userId": current_user.id,
                "transactionId": transaction_id,
                "transactionType": "debit",
                "amount": total_amount,
                "description": f"Ticket purchase for contest: {contest['contestName']}",
                "category": "ticket_purchase",
                "balanceBefore": current_user.walletBalance,
                "balanceAfter": new_balance,
                "status": "completed",
                "referenceId": str(seat_purchase.contestId),
                "createdAt": datetime.now()
            }
            await database.wallet_transactions.insert_one(wallet_transaction)
        
        return {
            "message": "Seats purchased successfully",
            "transactionId": transaction_id,
            "totalAmount": total_amount,
            "purchasedSeats": seat_purchase.seatNumbers,
            "contestName": contest["contestName"]
        }
        
    except Exception as e:
        logger.error(f"Error purchasing seats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to purchase seats"
        )

@router.get("/{contest_id}/purchased")
async def get_purchased_seats(
    contest_id: str,
    category_id: int = None,
    current_user: User = Depends(resolve_user)
):
    """Get purchased seats for a contest (for display)"""
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    query = {"contestId": ObjectId(contest_id), "status": "purchased"}
    if category_id:
        query["categoryId"] = category_id
    
    purchased_seats = []
    cursor = database.purchased_seats.find(query, {"seatNumber": 1, "categoryId": 1, "categoryName": 1})
    
    async for seat in cursor:
        purchased_seats.append({
            "seatNumber": seat["seatNumber"],
            "categoryId": seat["categoryId"],
            "categoryName": seat["categoryName"]
        })
    
    return {
        "contestId": contest_id,
        "categoryId": category_id,
        "purchasedSeats": purchased_seats,
        "totalPurchased": len(purchased_seats)
    }

@router.get("/{contest_id}/category/{category_id}")
async def get_category_seats(
    contest_id: str,
    category_id: int,
    current_user: User = Depends(resolve_user)
):
    """Get seat status for a specific category"""
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    if category_id not in CATEGORY_RANGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category ID"
        )
    
    # Get contest
    contest = await database.contests.find_one({"_id": ObjectId(contest_id)})
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )
    
    # Get purchased seats for this category
    purchased_seats = set()
    cursor = database.purchased_seats.find({
        "contestId": ObjectId(contest_id),
        "categoryId": category_id,
        "status": "purchased"
    }, {"seatNumber": 1})
    
    async for seat in cursor:
        purchased_seats.add(seat["seatNumber"])
    
    # Generate seat status
    category_info = CATEGORY_RANGES[category_id]
    seat_status = []
    
    for seat_num in range(category_info["start"], category_info["end"] + 1):
        seat_status.append({
            "seatNumber": seat_num,
            "isPurchased": seat_num in purchased_seats,
            "isAvailable": seat_num not in purchased_seats
        })
    
    return {
        "contestId": contest_id,
        "categoryId": category_id,
        "categoryName": category_info["name"],
        "seatRange": {
            "start": category_info["start"],
            "end": category_info["end"]
        },
        "seatStatus": seat_status,
        "totalSeats": category_info["end"] - category_info["start"] + 1,
        "purchasedSeats": len(purchased_seats),
        "availableSeats": (category_info["end"] - category_info["start"] + 1) - len(purchased_seats)
    }
