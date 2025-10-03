from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional
from database import get_database
from datetime import datetime
import httpx
import uuid
import logging
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple models for the new API
class SimplePaymentCreate(BaseModel):
    user_id: str
    amount: float
    description: Optional[str] = "Wallet top-up"

class SimplePaymentResponse(BaseModel):
    success: bool
    order_id: str
    razorpay_order_id: str
    razorpay_key_id: str
    payment_link: str
    amount: float
    message: str

class SimplePaymentStatus(BaseModel):
    order_id: str
    status: str
    amount: float
    message: str

# Simple Razorpay service
class SimpleRazorpayService:
    def __init__(self):
        self.key_id = settings.razorpay_key_id
        self.key_secret = settings.razorpay_key_secret
        self.api_base = settings.razorpay_api_base
        self.orders_url = f"{self.api_base}/orders"

    def _get_auth(self) -> tuple[str, str]:
        return (self.key_id, self.key_secret)

    async def create_order(self, amount: float, receipt: str) -> dict:
        """Create Razorpay order"""
        amount_paise = int(round(amount * 100))
        
        order_data = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1,
            "notes": {
                "receipt": receipt,
                "amount": str(amount)
            }
        }

        async with httpx.AsyncClient(timeout=30.0, auth=self._get_auth()) as client:
            response = await client.post(self.orders_url, json=order_data)
            if response.status_code not in (200, 201):
                raise Exception(f"Razorpay API error: {response.status_code} - {response.text}")
            return response.json()

    async def create_payment_link(self, amount: float, receipt: str, description: str) -> dict:
        """Create Razorpay payment link"""
        amount_paise = int(round(amount * 100))
        
        payment_link_data = {
            "amount": amount_paise,
            "currency": "INR",
            "description": description,
            "customer": {
                "name": "Customer",
                "email": "customer@example.com"
            },
            "notify": {
                "sms": False,
                "email": False
            },
            "reminder_enable": True,
            "callback_url": "https://yourdomain.com/payment/callback",
            "callback_method": "get"
        }

        async with httpx.AsyncClient(timeout=30.0, auth=self._get_auth()) as client:
            response = await client.post(f"{self.api_base}/payment_links", json=payment_link_data)
            if response.status_code not in (200, 201):
                raise Exception(f"Razorpay payment link API error: {response.status_code} - {response.text}")
            return response.json()

    async def get_order_status(self, razorpay_order_id: str) -> dict:
        """Get Razorpay order status"""
        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self._get_auth()) as client:
                url = f"{self.orders_url}/{razorpay_order_id}"
                logger.info(f"🔍 Fetching Razorpay order status from: {url}")
                response = await client.get(url)
                if response.status_code not in (200, 201):
                    logger.error(f"❌ Razorpay order status API error: {response.status_code} - {response.text}")
                    raise Exception(f"Failed to fetch order: {response.status_code}")
                data = response.json()
                logger.info(f"✅ Razorpay order data: {data}")
                return data
        except Exception as e:
            logger.error(f"💥 Error fetching Razorpay order status: {e}")
            raise

    async def get_order_payments(self, razorpay_order_id: str) -> list:
        """Get payments for an order"""
        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self._get_auth()) as client:
                url = f"{self.orders_url}/{razorpay_order_id}/payments"
                logger.info(f"🔍 Fetching Razorpay payments from: {url}")
                response = await client.get(url)
                if response.status_code in (200, 201):
                    data = response.json()
                    payments = data.get("items", [])
                    logger.info(f"✅ Razorpay payments: {payments}")
                    return payments
                else:
                    logger.error(f"❌ Razorpay payments API error: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"💥 Error fetching Razorpay payments: {e}")
            return []

# Global service instance
simple_razorpay = SimpleRazorpayService()

@router.get("/test")
async def test_razorpay_connection():
    """Test Razorpay API connection"""
    try:
        # Test with a small amount
        test_order = await simple_razorpay.create_order(1.0, "test_order")
        return {
            "success": True,
            "message": "Razorpay connection successful",
            "key_id": simple_razorpay.key_id,
            "test_order_id": test_order.get("id")
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Razorpay connection failed: {str(e)}",
            "key_id": simple_razorpay.key_id
        }

@router.get("/debug/{order_id}")
async def debug_payment_status(order_id: str):
    """Debug payment status and wallet credit"""
    try:
        database = get_database()
        
        # Get payment record
        payment = await database.simple_payments.find_one({"order_id": order_id})
        if not payment:
            return {"error": "Payment not found"}
        
        # Get user info
        user = await database.users.find_one({"_id": payment["user_id"]})
        user_info = {
            "id": str(user["_id"]) if user else None,
            "email": user.get("email") if user else None,
            "wallet_balance": user.get("walletBalance", 0) if user else None
        }
        
        # Get wallet transactions
        wallet_txns = []
        async for txn in database.wallet_transactions.find({"userId": payment["user_id"]}).sort("createdAt", -1).limit(5):
            txn["_id"] = str(txn["_id"])
            wallet_txns.append(txn)
        
        return {
            "payment": {
                "order_id": payment["order_id"],
                "status": payment["status"],
                "amount": payment["amount"],
                "user_id": payment["user_id"],
                "created_at": payment["created_at"]
            },
            "user": user_info,
            "recent_wallet_transactions": wallet_txns
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/create", response_model=SimplePaymentResponse)
async def create_simple_payment(
    user_id: str = Query(..., description="User ID"),
    amount: float = Query(..., gt=0, description="Amount in INR"),
    description: str = Query("Wallet top-up", description="Description")
):
    """Create a simple Razorpay payment order"""
    try:
        database = get_database()
        
        # Check if user exists
        user = await database.users.find_one({
            "$or": [
                {"userId": user_id},
                {"email": user_id},
                {"phoneNumber": user_id}
            ]
        })
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"User not found: {user_id}"
            )

        # Generate unique order ID
        order_id = f"SP_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # Create Razorpay order
        razorpay_order = await simple_razorpay.create_order(amount, order_id)
        razorpay_order_id = razorpay_order.get("id")
        
        if not razorpay_order_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create Razorpay order"
            )

        # Save to simple_payments collection
        payment_record = {
            "order_id": order_id,
            "user_id": str(user["_id"]),
            "user_identifier": user_id,
            "amount": amount,
            "description": description,
            "razorpay_order_id": razorpay_order_id,
            "status": "PENDING",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        await database.simple_payments.insert_one(payment_record)
        
        return SimplePaymentResponse(
            success=True,
            order_id=order_id,
            razorpay_order_id=razorpay_order_id,
            razorpay_key_id=simple_razorpay.key_id,
            payment_link="",  # Not needed for Flutter SDK
            amount=amount,
            message="Razorpay order created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating simple payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )

@router.get("/status/{order_id}", response_model=SimplePaymentStatus)
async def get_simple_payment_status(order_id: str):
    """Get payment status"""
    try:
        database = get_database()
        
        # Get payment record
        payment = await database.simple_payments.find_one({"order_id": order_id})
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        razorpay_order_id = payment.get("razorpay_order_id")
        if not razorpay_order_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Razorpay order ID missing"
            )
        
        # Get Razorpay order status and payments
        order_data = await simple_razorpay.get_order_status(razorpay_order_id)
        payments_list = await simple_razorpay.get_order_payments(razorpay_order_id)
        
        # Log for debugging
        logger.info(f"Razorpay order status for {razorpay_order_id}: {order_data.get('status')}")
        logger.info(f"Razorpay payments for {razorpay_order_id}: {[p.get('status') for p in payments_list]}")
        
        # Add a small delay to allow Razorpay to process payment data
        # Sometimes payments are captured but not immediately reflected in API
        import asyncio
        await asyncio.sleep(1)
        
        # Re-fetch payments after small delay if no payments found initially
        if not payments_list and order_data.get("status") in ["attempted", "paid"]:
            logger.info(f"🔄 No payments found initially, re-fetching after delay...")
            payments_list = await simple_razorpay.get_order_payments(razorpay_order_id)
            if payments_list:
                logger.info(f"✅ Found payments on retry: {len(payments_list)} payments")
        
        # Determine status - be more thorough in checking
        status_value = "PENDING"
        order_status = order_data.get("status", "").lower()
        
        # Check order status first
        if order_status == "paid":
            status_value = "SUCCESS"
            logger.info(f"Order marked as paid for {razorpay_order_id}")
        elif order_status == "cancelled":
            status_value = "CANCELLED"
            logger.info(f"Order cancelled for {razorpay_order_id}")
        elif order_status == "attempted":
            # Order attempted but check payments
            logger.info(f"Order attempted for {razorpay_order_id}, checking payments...")
        
        # Check individual payments (this is more reliable than order status)
        for payment_item in payments_list:
            payment_status = payment_item.get("status", "").lower()
            payment_id = payment_item.get("id", "unknown")
            amount = payment_item.get("amount", 0)
            
            logger.info(f"💳 Payment {payment_id}: status={payment_status}, amount={amount}")
            
            # Success states (any of these means payment successful)
            if payment_status in ["captured", "authorized"]:
                status_value = "SUCCESS"
                logger.info(f"✅ Payment {payment_id} successful (status: {payment_status}) for order {razorpay_order_id}")
                break
                
            # Failure states
            elif payment_status == "failed":
                status_value = "FAILED"
                logger.info(f"❌ Payment {payment_id} failed for order {razorpay_order_id}")
                break
                
            elif payment_status == "refunded":
                status_value = "FAILED"
                logger.info(f"💰 Payment {payment_id} refunded for order {razorpay_order_id}")
                break
                
            elif payment_status == "cancelled":
                status_value = "CANCELLED"
                logger.info(f"🚫 Payment {payment_id} cancelled for order {razorpay_order_id}")
                break
                
            # Pending states - continue checking
            elif payment_status in ["created", "attempted", "pending"]:
                logger.info(f"⏳ Payment {payment_id} still processing (status: {payment_status})")
                continue
        
        # If we didn't find any payments but order is marked as paid
        if not payments_list and order_status == "paid":
            status_value = "SUCCESS"
            logger.info(f"✅ Order {razorpay_order_id} marked as paid but no payments found")
        
        # Update our record
        await database.simple_payments.update_one(
            {"order_id": order_id},
            {
                "$set": {
                    "status": status_value,
                    "updated_at": datetime.now(),
                    "razorpay_response": {
                        "order": order_data,
                        "payments": payments_list
                    }
                }
            }
        )
        
        # If successful, credit wallet
        if status_value == "SUCCESS" and payment.get("status") != "SUCCESS":
            logger.info(f"💰 Payment successful, crediting wallet for order {order_id}")
            await credit_user_wallet(payment)
        elif status_value == "SUCCESS" and payment.get("status") == "SUCCESS":
            logger.info(f"✅ Payment already processed for order {order_id}")
        else:
            logger.info(f"⏳ Payment not successful yet for order {order_id}, status: {status_value}")
        
        # Return detailed response for debugging
        final_status = SimplePaymentStatus(
            order_id=order_id,
            status=status_value,
            amount=payment.get("amount", 0),
            message=f"Payment {status_value.lower()}"
        )
        
        logger.info(f"📤 Returning payment status: order_id={order_id}, status={status_value}")
        return final_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment status: {str(e)}"
        )


async def credit_user_wallet(payment: dict):
    """Credit user's wallet when payment is successful"""
    try:
        database = get_database()
        user_id = payment["user_id"]
        amount = payment["amount"]
        
        logger.info(f"Starting wallet credit for user {user_id}, amount {amount}")
        
        # Get user
        user = await database.users.find_one({"_id": user_id})
        if not user:
            logger.error(f"User not found: {user_id}")
            return
        
        logger.info(f"User found: {user.get('email', 'no email')}")
        
        # Update wallet balance
        current_balance = user.get("walletBalance", 0.0)
        new_balance = float(current_balance) + float(amount)
        
        logger.info(f"Updating balance: {current_balance} -> {new_balance}")
        
        await database.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"walletBalance": new_balance}}
        )
        
        # Create wallet transaction
        wallet_transaction = {
            "userId": user["_id"],  # Use the resolved user's MongoDB _id
            "transactionId": f"SP_{payment['order_id']}",
            "transactionType": "credit",
            "amount": amount,
            "description": payment.get("description", "Wallet top-up via simple payment"),
            "category": "deposit",
            "balanceBefore": current_balance,
            "balanceAfter": new_balance,
            "status": "completed",
            "createdAt": datetime.now()
        }
        
        result = await database.wallet_transactions.insert_one(wallet_transaction)
        logger.info(f"📝 Wallet transaction created with ID: {result.inserted_id}")
        logger.info(f"✅ Successfully credited ₹{amount} to user {user_identifier} for order {payment['order_id']}")
        
    except Exception as e:
        logger.error(f"Error crediting wallet: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
