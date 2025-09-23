from fastapi import APIRouter, HTTPException, Depends, status, Query
from models import User, PaymentCreate, PaymentResponse, PaymentStatus
from auth import resolve_user
from services.payment_service import payment_service
from typing import Optional
from database import get_database
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(resolve_user)
):
    """Create a payment order for wallet top-up"""
    try:
        if payment_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )
        
        if payment_data.amount < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum payment amount is ₹10"
            )
        
        if payment_data.amount > 100000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum payment amount is ₹1,00,000"
            )
        
        result = await payment_service.create_payment_order(
            user_id=str(current_user.id),
            amount=payment_data.amount,
            customer_email=current_user.email,
            customer_phone=current_user.phoneNumber,
            description=payment_data.description
        )
        
        return PaymentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/verify/{order_id}")
async def verify_payment(
    order_id: str,
    current_user: User = Depends(resolve_user)
):
    """Verify payment status for a specific order"""
    try:
        result = await payment_service.verify_payment(order_id)
        
        # Check if payment is successful and process it
        if result["status"] == PaymentStatus.SUCCESS:
            success = await payment_service.process_successful_payment(order_id)
            if success:
                result["message"] = "Payment verified and wallet updated successfully"
            else:
                result["message"] = "Payment verified but failed to update wallet"
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history")
async def get_payment_history(
    current_user: User = Depends(resolve_user),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user's payment history"""
    try:
        result = await payment_service.get_payment_history(
            user_id=str(current_user.id),
            limit=limit,
            skip=skip
        )
        return result
        
    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment history"
        )

@router.get("/status/{order_id}")
async def get_payment_status(
    order_id: str,
    current_user: User = Depends(resolve_user)
):
    """Get payment status for a specific order"""
    try:
        result = await payment_service.verify_payment(order_id)
        return result
        
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/return")
async def payment_return(
    order_id: str = Query(..., description="Order ID from payment gateway"),
    cf_status: Optional[str] = Query(None, description="Cashfree status"),
    cf_message: Optional[str] = Query(None, description="Cashfree message")
):
    """Handle payment return from Cashfree"""
    try:
        # Verify payment status
        result = await payment_service.verify_payment(order_id)
        
        # Process successful payment
        if result["status"] == PaymentStatus.SUCCESS:
            success = await payment_service.process_successful_payment(order_id)
            if success:
                return {
                    "success": True,
                    "message": "Payment successful and wallet updated",
                    "order_id": order_id,
                    "status": result["status"]
                }
            else:
                return {
                    "success": False,
                    "message": "Payment successful but failed to update wallet",
                    "order_id": order_id,
                    "status": result["status"]
                }
        else:
            return {
                "success": False,
                "message": f"Payment {result['status'].lower()}",
                "order_id": order_id,
                "status": result["status"]
            }
            
    except Exception as e:
        logger.error(f"Error processing payment return: {e}")
        return {
            "success": False,
            "message": "Error processing payment",
            "order_id": order_id,
            "error": str(e)
        }

@router.post("/notify")
async def payment_notify(payload: dict):
    """Handle payment notifications from Cashfree (webhook)"""
    try:
        # Extract order ID from webhook payload
        order_id = payload.get("orderId") or payload.get("data", {}).get("order", {}).get("order_id")
        
        if not order_id:
            logger.warning("No order ID found in webhook payload")
            return {"status": "error", "message": "No order ID found"}
        
        # Verify payment status
        result = await payment_service.verify_payment(order_id)
        
        # Process successful payment
        if result["status"] == PaymentStatus.SUCCESS:
            success = await payment_service.process_successful_payment(order_id)
            if success:
                logger.info(f"Webhook: Successfully processed payment for order {order_id}")
            else:
                logger.error(f"Webhook: Failed to process payment for order {order_id}")
        
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Error processing payment webhook: {e}")
        return {"status": "error", "message": str(e)}


# Minimal Razorpay order creation without auth (for trusted/internal usage)
@router.post("/create-minimal", response_model=PaymentResponse)
async def create_payment_minimal(
    userId: str = Query(..., description="User identifier: userId/email/phone"),
    amount: float = Query(..., gt=0, description="Amount in INR"),
    description: Optional[str] = Query("Wallet top-up", description="Description")
):
    try:
        database = get_database()
        user = await database.users.find_one({
            "$or": [
                {"userId": userId},
                {"phoneNumber": userId},
                {"email": userId}
            ]
        })
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        result = await payment_service.create_payment_order(
            user_id=str(user["_id"]),
            amount=amount,
            customer_email=user.get("email") or "",
            customer_phone=user.get("phoneNumber") or "",
            description=description or "Wallet top-up"
        )
        return PaymentResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Minimal status check without auth
@router.get("/status-minimal/{order_id}")
async def get_payment_status_minimal(order_id: str):
    try:
        return await payment_service.verify_payment(order_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Minimal, authless endpoint to directly credit user's wallet
# WARNING: Use only in trusted/internal environments.
@router.post("/direct-credit")
async def direct_credit_wallet(
    userId: str = Query(..., description="User identifier: userId/email/phone"),
    amount: float = Query(..., gt=0, description="Amount to credit in INR"),
    description: Optional[str] = Query("Wallet direct credit", description="Optional description")
):
    """Directly credit money to a user's wallet without auth or gateway.
    Inputs via query for simplicity: userId, amount, optional description.
    """
    try:
        database = get_database()

        # Resolve user by any identifier
        user = await database.users.find_one({
            "$or": [
                {"userId": userId},
                {"phoneNumber": userId},
                {"email": userId}
            ]
        })
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than 0")

        previous_balance = user.get("walletBalance", 0.0)
        new_balance = float(previous_balance) + float(amount)

        # Update wallet balance
        await database.users.update_one({"_id": user["_id"]}, {"$set": {"walletBalance": new_balance}})

        # Insert wallet transaction
        wallet_txn = {
            "userId": user["_id"],
            "transactionId": f"DIRECT_{int(datetime.now().timestamp())}",
            "transactionType": "credit",
            "amount": float(amount),
            "description": description or "Wallet direct credit",
            "category": "deposit",
            "balanceBefore": previous_balance,
            "balanceAfter": new_balance,
            "status": "completed",
            "createdAt": datetime.now()
        }
        await database.wallet_transactions.insert_one(wallet_txn)

        return {
            "success": True,
            "message": "Wallet credited successfully",
            "userId": str(user.get("userId") or user.get("email") or user.get("phoneNumber")),
            "amount": float(amount),
            "balanceBefore": previous_balance,
            "balanceAfter": new_balance
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in direct credit: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
