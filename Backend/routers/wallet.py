from fastapi import APIRouter, HTTPException, Depends, status
from models import User, WalletTransaction, Withdrawal, WithdrawalCreate, TransactionType, TransactionCategory, TransactionStatus, WithdrawalMethod, WithdrawalStatus
from auth import resolve_user, get_user_with_password
from database import get_database
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/balance")
async def get_wallet_balance(current_user: User = Depends(resolve_user)):
    """Get user's wallet balance and summary"""
    database = get_database()
    
    # Get recent transactions count
    recent_transactions = await database.wallet_transactions.count_documents({
        "userId": current_user.id,
        "createdAt": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
    })
    
    return {
        "userId": current_user.userId,
        "userName": current_user.userName,
        "walletBalance": current_user.walletBalance,
        "isActive": current_user.isActive,
        "todayTransactions": recent_transactions
    }

@router.get("/transactions")
async def get_wallet_transactions(
    current_user: User = Depends(resolve_user),
    limit: int = 20,
    skip: int = 0,
    category: Optional[TransactionCategory] = None
):
    """Get user's wallet transaction history"""
    database = get_database()
    
    query = {"userId": current_user.id}
    if category:
        query["category"] = category
    
    transactions = []
    cursor = database.wallet_transactions.find(query).sort("createdAt", -1).skip(skip).limit(limit)
    
    async for transaction in cursor:
        transaction["id"] = str(transaction["_id"])
        del transaction["_id"]
        transactions.append(transaction)
    
    return {
        "userId": current_user.userId,
        "transactions": transactions,
        "total": len(transactions),
        "limit": limit,
        "skip": skip
    }

@router.post("/add-money")
async def add_money_to_wallet(
    amount: float = 0,
    description: str = "Wallet top-up",
    current_user: User = Depends(get_user_with_password)
):
    """Add money to user's wallet - minimal validation."""
    database = get_database()
    try:
        amount = float(amount)
    except Exception:
        amount = 0
    if amount < 0:
        amount = 0
    
    # Generate transaction ID
    transaction_id = str(uuid.uuid4())
    
    try:
        # Update wallet balance
        new_balance = (current_user.walletBalance or 0) + amount
        await database.users.update_one(
            {"_id": current_user.id},
            {"$set": {"walletBalance": new_balance}}
        )
        
        # Create wallet transaction
        wallet_transaction = {
            "userId": current_user.id,
            "transactionId": transaction_id,
            "transactionType": TransactionType.CREDIT,
            "amount": amount,
            "description": description,
            "category": TransactionCategory.DEPOSIT,
            "balanceBefore": current_user.walletBalance or 0,
            "balanceAfter": new_balance,
            "status": TransactionStatus.COMPLETED,
            "createdAt": datetime.now()
        }
        await database.wallet_transactions.insert_one(wallet_transaction)
        
        return {
            "message": "Money added to wallet successfully",
            "transactionId": transaction_id,
            "amount": amount,
            "newBalance": new_balance
        }
        
    except Exception as e:
        logger.error(f"Error adding money to wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add money to wallet"
        )

@router.post("/withdraw")
async def request_withdrawal(
    amount: float,
    bank_details_id: str,
    withdrawal_method: WithdrawalMethod = WithdrawalMethod.BANK_TRANSFER,
    current_user: User = Depends(resolve_user)
):
    """Request withdrawal from wallet"""
    database = get_database()
    
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )
    
    if amount > current_user.walletBalance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient wallet balance"
        )
    
    if amount < 100:  # Minimum withdrawal
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum withdrawal amount is ₹100"
        )
    
    # Check if bank details exist
    if not ObjectId.is_valid(bank_details_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bank details ID"
        )
    
    bank_details = await database.bank_details.find_one({
        "_id": ObjectId(bank_details_id),
        "userId": current_user.id
    })
    
    if not bank_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank details not found"
        )
    
    if not bank_details["isVerified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bank details not verified"
        )
    
    # Check for pending withdrawals
    pending_withdrawal = await database.withdrawals.find_one({
        "userId": current_user.id,
        "status": {"$in": [WithdrawalStatus.PENDING, WithdrawalStatus.PROCESSING]}
    })
    
    if pending_withdrawal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have a pending withdrawal request"
        )
    
    try:
        # Create withdrawal request
        withdrawal = {
            "userId": current_user.id,
            "amount": amount,
            "bankDetailsId": ObjectId(bank_details_id),
            "withdrawalMethod": withdrawal_method,
            "status": WithdrawalStatus.PENDING,
            "requestDate": datetime.now(),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = await database.withdrawals.insert_one(withdrawal)
        
        return {
            "message": "Withdrawal request submitted successfully",
            "withdrawalId": str(result.inserted_id),
            "amount": amount,
            "status": WithdrawalStatus.PENDING
        }
        
    except Exception as e:
        logger.error(f"Error creating withdrawal request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create withdrawal request"
        )

@router.get("/withdrawals")
async def get_withdrawal_history(
    current_user: User = Depends(resolve_user),
    limit: int = 10,
    skip: int = 0
):
    """Get user's withdrawal history"""
    database = get_database()
    
    withdrawals = []
    cursor = database.withdrawals.find({"userId": current_user.id}).sort("createdAt", -1).skip(skip).limit(limit)
    
    async for withdrawal in cursor:
        # Get bank details
        bank_details = await database.bank_details.find_one({"_id": withdrawal["bankDetailsId"]})
        
        withdrawal["id"] = str(withdrawal["_id"])
        del withdrawal["_id"]
        withdrawal["bankDetails"] = {
            "accountNumber": bank_details["accountNumber"][-4:].rjust(len(bank_details["accountNumber"]), "*") if bank_details else "N/A",
            "bankName": bank_details["bankName"] if bank_details else "N/A"
        }
        
        withdrawals.append(withdrawal)
    
    return {
        "userId": current_user.userId,
        "withdrawals": withdrawals,
        "total": len(withdrawals),
        "limit": limit,
        "skip": skip
    }

@router.get("/withdrawals/{withdrawal_id}")
async def get_withdrawal_details(
    withdrawal_id: str,
    current_user: User = Depends(resolve_user)
):
    """Get specific withdrawal details"""
    database = get_database()
    
    if not ObjectId.is_valid(withdrawal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid withdrawal ID"
        )
    
    withdrawal = await database.withdrawals.find_one({
        "_id": ObjectId(withdrawal_id),
        "userId": current_user.id
    })
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found"
        )
    
    # Get bank details
    bank_details = await database.bank_details.find_one({"_id": withdrawal["bankDetailsId"]})
    
    withdrawal["id"] = str(withdrawal["_id"])
    del withdrawal["_id"]
    withdrawal["bankDetails"] = bank_details
    
    return withdrawal

@router.post("/withdrawals/{withdrawal_id}/cancel")
async def cancel_withdrawal(
    withdrawal_id: str,
    current_user: User = Depends(resolve_user)
):
    """Cancel a pending withdrawal request"""
    database = get_database()
    
    if not ObjectId.is_valid(withdrawal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid withdrawal ID"
        )
    
    withdrawal = await database.withdrawals.find_one({
        "_id": ObjectId(withdrawal_id),
        "userId": current_user.id
    })
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found"
        )
    
    if withdrawal["status"] != WithdrawalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending withdrawals can be cancelled"
        )
    
    # Update withdrawal status
    await database.withdrawals.update_one(
        {"_id": ObjectId(withdrawal_id)},
        {
            "$set": {
                "status": WithdrawalStatus.CANCELLED,
                "updatedAt": datetime.now()
            }
        }
    )
    
    return {"message": "Withdrawal request cancelled successfully"}

@router.get("/summary")
async def get_wallet_summary(
    current_user: User = Depends(resolve_user),
    days: int = 30
):
    """Get wallet summary for the last N days"""
    database = get_database()
    
    from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    from_date = from_date.replace(day=from_date.day - days)
    
    # Get transaction summary
    pipeline = [
        {
            "$match": {
                "userId": current_user.id,
                "createdAt": {"$gte": from_date}
            }
        },
        {
            "$group": {
                "_id": "$category",
                "totalAmount": {"$sum": "$amount"},
                "transactionCount": {"$sum": 1},
                "creditAmount": {
                    "$sum": {
                        "$cond": [{"$eq": ["$transactionType", "credit"]}, "$amount", 0]
                    }
                },
                "debitAmount": {
                    "$sum": {
                        "$cond": [{"$eq": ["$transactionType", "debit"]}, "$amount", 0]
                    }
                }
            }
        }
    ]
    
    summary = []
    cursor = database.wallet_transactions.aggregate(pipeline)
    
    async for item in cursor:
        summary.append(item)
    
    # Get total stats
    total_credit = sum(item["creditAmount"] for item in summary)
    total_debit = sum(item["debitAmount"] for item in summary)
    
    return {
        "userId": current_user.userId,
        "currentBalance": current_user.walletBalance,
        "period": f"Last {days} days",
        "summary": summary,
        "totalCredit": total_credit,
        "totalDebit": total_debit,
        "netChange": total_credit - total_debit
    }
