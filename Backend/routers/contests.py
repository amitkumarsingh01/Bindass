from fastapi import APIRouter, HTTPException, Depends, status
from models import Contest, ContestCreate, User, Category, ContestStatus
from auth import get_current_user
from database import get_database
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Default contest categories
DEFAULT_CATEGORIES = [
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

@router.get("/", response_model=List[dict])
async def get_contests(
    status: Optional[ContestStatus] = None,
    limit: int = 10,
    skip: int = 0
):
    """Get all contests with optional filtering"""
    database = get_database()
    
    query = {}
    if status:
        query["status"] = status
    
    contests = []
    cursor = database.contests.find(query).skip(skip).limit(limit).sort("createdAt", -1)
    
    async for contest in cursor:
        contest["id"] = str(contest["_id"])
        del contest["_id"]
        contests.append(contest)
    
    return contests

@router.get("/{contest_id}", response_model=dict)
async def get_contest(contest_id: str):
    """Get specific contest by ID"""
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    contest = await database.contests.find_one({"_id": ObjectId(contest_id)})
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )
    
    contest["id"] = str(contest["_id"])
    del contest["_id"]
    
    return contest

@router.get("/{contest_id}/categories")
async def get_contest_categories(contest_id: str):
    """Get contest categories with seat availability"""
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    contest = await database.contests.find_one({"_id": ObjectId(contest_id)})
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )
    
    return {
        "contestId": contest_id,
        "contestName": contest["contestName"],
        "categories": contest.get("categories", DEFAULT_CATEGORIES)
    }

@router.get("/{contest_id}/leaderboard")
async def get_contest_leaderboard(
    contest_id: str,
    limit: int = 10
):
    """Get contest leaderboard (highest purchasers)"""
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    # Aggregation pipeline for leaderboard
    pipeline = [
        {"$match": {"contestId": ObjectId(contest_id), "status": "purchased"}},
        {
            "$group": {
                "_id": "$userId",
                "totalPurchases": {"$sum": 1},
                "seatNumbers": {"$push": "$seatNumber"},
                "totalAmount": {"$sum": "$ticketPrice"}
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$project": {
                "userId": "$user.userId",
                "userName": "$user.userName",
                "profilePicture": "$user.profilePicture",
                "totalPurchases": 1,
                "seatNumbers": 1,
                "totalAmount": 1
            }
        },
        {"$sort": {"totalPurchases": -1}},
        {"$limit": limit}
    ]
    
    leaderboard = []
    cursor = database.purchased_seats.aggregate(pipeline)
    
    async for item in cursor:
        leaderboard.append(item)
    
    return {
        "contestId": contest_id,
        "leaderboard": leaderboard
    }

@router.get("/{contest_id}/winners")
async def get_contest_winners(contest_id: str):
    """Get contest winners list"""
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
    
    # Get winners with user details
    pipeline = [
        {"$match": {"contestId": ObjectId(contest_id)}},
        {
            "$lookup": {
                "from": "users",
                "localField": "userId",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$project": {
                "seatNumber": 1,
                "categoryName": 1,
                "prizeRank": 1,
                "prizeAmount": 1,
                "prizeDescription": 1,
                "drawDate": 1,
                "isPrizeClaimed": 1,
                "userName": "$user.userName",
                "profilePicture": "$user.profilePicture",
                "phoneNumber": "$user.phoneNumber",
                "city": "$user.city",
                "state": "$user.state"
            }
        },
        {"$sort": {"prizeRank": 1}}
    ]
    
    winners = []
    cursor = database.winners.aggregate(pipeline)
    
    async for winner in cursor:
        winners.append(winner)
    
    return {
        "contestId": contest_id,
        "contestName": contest["contestName"],
        "totalWinners": len(winners),
        "winners": winners
    }

@router.get("/{contest_id}/my-purchases")
async def get_my_contest_purchases(
    contest_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user's purchased seats for a specific contest"""
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    # Get user's purchased seats
    pipeline = [
        {
            "$match": {
                "contestId": ObjectId(contest_id),
                "userId": current_user.id,
                "status": "purchased"
            }
        },
        {
            "$group": {
                "_id": "$categoryId",
                "categoryName": {"$first": "$categoryName"},
                "seats": {"$push": "$seatNumber"},
                "totalSeats": {"$sum": 1},
                "totalAmount": {"$sum": "$ticketPrice"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    purchases = []
    cursor = database.purchased_seats.aggregate(pipeline)
    
    async for purchase in cursor:
        purchases.append(purchase)
    
    # Get contest details
    contest = await database.contests.find_one({"_id": ObjectId(contest_id)})
    
    return {
        "contestId": contest_id,
        "contestName": contest["contestName"] if contest else "Unknown",
        "userId": current_user.userId,
        "userName": current_user.userName,
        "purchases": purchases
    }

@router.get("/{contest_id}/prize-structure")
async def get_contest_prize_structure(contest_id: str):
    """Get contest prize structure"""
    database = get_database()
    
    if not ObjectId.is_valid(contest_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contest ID"
        )
    
    prizes = []
    cursor = database.prize_structure.find({"contestId": ObjectId(contest_id)}).sort("prizeRank", 1)
    
    async for prize in cursor:
        prize["id"] = str(prize["_id"])
        del prize["_id"]
        prizes.append(prize)
    
    return {
        "contestId": contest_id,
        "prizeStructure": prizes
    }
