import random
import logging
from datetime import datetime
from typing import List, Dict, Tuple
from database import get_database
from bson import ObjectId
from models import Winner, PrizeStructure, PurchasedSeat, WalletTransaction, TransactionType, TransactionCategory, TransactionStatus

logger = logging.getLogger(__name__)

class LotteryDraw:
    def __init__(self, contest_id: str):
        self.contest_id = ObjectId(contest_id)
        self.database = get_database()
    
    async def conduct_draw(self) -> Dict:
        """Conduct lottery draw for a contest"""
        try:
            # Get contest details
            contest = await self.database.contests.find_one({"_id": self.contest_id})
            if not contest:
                raise ValueError("Contest not found")
            
            if contest["isDrawCompleted"]:
                raise ValueError("Draw already completed for this contest")
            
            # Get prize structure
            prize_structure = await self.database.prize_structure.find(
                {"contestId": self.contest_id}
            ).sort("prizeRank", 1).to_list(length=None)
            
            if not prize_structure:
                raise ValueError("No prize structure found for this contest")
            
            # Get all purchased seats
            purchased_seats = await self.database.purchased_seats.find({
                "contestId": self.contest_id,
                "status": "purchased"
            }).to_list(length=None)
            
            if not purchased_seats:
                raise ValueError("No purchased seats found for this contest")
            
            # Select winners
            winners = await self._select_winners(purchased_seats, prize_structure)
            
            # Update contest status
            await self.database.contests.update_one(
                {"_id": self.contest_id},
                {
                    "$set": {
                        "isDrawCompleted": True,
                        "status": "completed",
                        "updatedAt": datetime.now()
                    }
                }
            )
            
            # Update purchased seats with winner status
            await self._update_purchased_seats(winners)
            
            # Credit prizes to winners' wallets
            await self._credit_prizes(winners)
            
            # Create winner records
            await self._create_winner_records(winners)
            
            # Send notifications
            await self._send_winner_notifications(winners)
            
            return {
                "success": True,
                "contestId": str(self.contest_id),
                "totalWinners": len(winners),
                "winners": winners,
                "drawDate": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error conducting lottery draw: {e}")
            raise
    
    async def _select_winners(self, purchased_seats: List[Dict], prize_structure: List[Dict]) -> List[Dict]:
        """Select winners based on prize structure"""
        winners = []
        available_seats = purchased_seats.copy()
        
        for prize in prize_structure:
            prize_rank = prize["prizeRank"]
            prize_amount = prize["prizeAmount"]
            number_of_winners = prize["numberOfWinners"]
            prize_description = prize.get("prizeDescription", f"Rank {prize_rank}")
            
            # Select winners for this prize rank
            selected_winners = random.sample(available_seats, min(number_of_winners, len(available_seats)))
            
            for winner in selected_winners:
                winner_info = {
                    "userId": winner["userId"],
                    "seatNumber": winner["seatNumber"],
                    "categoryName": winner["categoryName"],
                    "prizeRank": prize_rank,
                    "prizeAmount": prize_amount,
                    "prizeDescription": prize_description,
                    "drawDate": datetime.now()
                }
                winners.append(winner_info)
                
                # Remove selected seat from available seats
                available_seats.remove(winner)
            
            # If we've selected all available seats, break
            if not available_seats:
                break
        
        return winners
    
    async def _update_purchased_seats(self, winners: List[Dict]):
        """Update purchased seats with winner information"""
        for winner in winners:
            await self.database.purchased_seats.update_one(
                {
                    "contestId": self.contest_id,
                    "userId": winner["userId"],
                    "seatNumber": winner["seatNumber"]
                },
                {
                    "$set": {
                        "isWinner": True,
                        "prizeAmount": winner["prizeAmount"]
                    }
                }
            )
    
    async def _credit_prizes(self, winners: List[Dict]):
        """Credit prize amounts to winners' wallets"""
        for winner in winners:
            # Get user's current balance
            user = await self.database.users.find_one({"_id": winner["userId"]})
            if not user:
                continue
            
            new_balance = user["walletBalance"] + winner["prizeAmount"]
            
            # Update user's wallet balance
            await self.database.users.update_one(
                {"_id": winner["userId"]},
                {"$set": {"walletBalance": new_balance}}
            )
            
            # Create wallet transaction
            transaction_id = f"PRIZE_{winner['userId']}_{winner['seatNumber']}_{int(datetime.now().timestamp())}"
            
            wallet_transaction = {
                "userId": winner["userId"],
                "transactionId": transaction_id,
                "transactionType": TransactionType.CREDIT,
                "amount": winner["prizeAmount"],
                "description": f"Prize money - {winner['prizeDescription']} (Seat: {winner['seatNumber']})",
                "category": TransactionCategory.PRIZE_CREDIT,
                "balanceBefore": user["walletBalance"],
                "balanceAfter": new_balance,
                "status": TransactionStatus.COMPLETED,
                "referenceId": str(self.contest_id),
                "createdAt": datetime.now()
            }
            
            await self.database.wallet_transactions.insert_one(wallet_transaction)
    
    async def _create_winner_records(self, winners: List[Dict]):
        """Create winner records in the database"""
        winner_records = []
        for winner in winners:
            winner_record = {
                "contestId": self.contest_id,
                "userId": winner["userId"],
                "seatNumber": winner["seatNumber"],
                "categoryName": winner["categoryName"],
                "prizeRank": winner["prizeRank"],
                "prizeAmount": winner["prizeAmount"],
                "prizeDescription": winner["prizeDescription"],
                "drawDate": winner["drawDate"],
                "isPrizeClaimed": False,
                "prizeClaimedDate": None,
                "createdAt": datetime.now()
            }
            winner_records.append(winner_record)
        
        if winner_records:
            await self.database.winners.insert_many(winner_records)
    
    async def _send_winner_notifications(self, winners: List[Dict]):
        """Send notifications to winners"""
        for winner in winners:
            notification = {
                "userId": winner["userId"],
                "title": "Congratulations! You Won!",
                "message": f"Congratulations! You won ₹{winner['prizeAmount']} in {winner['prizeDescription']} with seat number {winner['seatNumber']}",
                "type": "winner",
                "isRead": False,
                "createdAt": datetime.now()
            }
            await self.database.notifications.insert_one(notification)

async def conduct_lottery_draw(contest_id: str) -> Dict:
    """Conduct lottery draw for a contest"""
    lottery = LotteryDraw(contest_id)
    return await lottery.conduct_draw()

async def get_contest_statistics(contest_id: str) -> Dict:
    """Get contest statistics"""
    database = get_database()
    
    # Get contest details
    contest = await database.contests.find_one({"_id": ObjectId(contest_id)})
    if not contest:
        raise ValueError("Contest not found")
    
    # Get total purchased seats
    total_purchased = await database.purchased_seats.count_documents({
        "contestId": ObjectId(contest_id),
        "status": "purchased"
    })
    
    # Get total winners
    total_winners = await database.winners.count_documents({
        "contestId": ObjectId(contest_id)
    })
    
    # Get prize distribution
    prize_distribution = []
    cursor = database.winners.aggregate([
        {"$match": {"contestId": ObjectId(contest_id)}},
        {
            "$group": {
                "_id": "$prizeRank",
                "prizeAmount": {"$first": "$prizeAmount"},
                "prizeDescription": {"$first": "$prizeDescription"},
                "winnerCount": {"$sum": 1},
                "totalAmount": {"$sum": "$prizeAmount"}
            }
        },
        {"$sort": {"_id": 1}}
    ])
    
    async for item in cursor:
        prize_distribution.append(item)
    
    return {
        "contestId": str(contest_id),
        "contestName": contest["contestName"],
        "totalSeats": contest["totalSeats"],
        "purchasedSeats": total_purchased,
        "availableSeats": contest["totalSeats"] - total_purchased,
        "totalWinners": total_winners,
        "isDrawCompleted": contest["isDrawCompleted"],
        "prizeDistribution": prize_distribution
    }
