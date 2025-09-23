import httpx
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from config import settings
from models import PaymentTransaction, PaymentStatus, PaymentGateway
from database import get_database
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        # Razorpay
        self.key_id = settings.razorpay_key_id
        self.key_secret = settings.razorpay_key_secret
        self.api_base = settings.razorpay_api_base
        self.orders_url = f"{self.api_base}/orders"
        self.payments_url = f"{self.api_base}/payments"
        self.return_url = settings.razorpay_return_url

    def _get_auth(self) -> tuple[str, str]:
        # Basic auth with key_id:key_secret
        return (self.key_id, self.key_secret)

    async def create_payment_order(
        self,
        user_id: str,
        amount: float,
        customer_email: str,
        customer_phone: str,
        description: str = "Wallet top-up",
    ) -> Dict[str, Any]:
        """Create a payment order with Razorpay"""
        database = get_database()

        # Razorpay expects amount in paise (int)
        amount_paise = int(round(amount * 100))

        # Generate receipt/order id
        order_id = f"WALLET_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"

        order_payload = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": order_id,
            "payment_capture": 1,
            "notes": {
                "user_id": user_id,
                "description": description,
                "email": customer_email,
                "phone": customer_phone,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self._get_auth()) as client:
                resp = await client.post(self.orders_url, json=order_payload)
                if resp.status_code not in (200, 201):
                    raise Exception(f"Razorpay API error: {resp.status_code} - {resp.text}")

                rzp_order = resp.json()

                payment_transaction = {
                    "userId": user_id,
                    "orderId": order_id,
                    "amount": amount,
                    "currency": "INR",
                    "gateway": PaymentGateway.RAZORPAY,
                    "gatewayOrderId": rzp_order.get("id"),
                    "status": PaymentStatus.PENDING,
                    "gatewayResponse": rzp_order,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now(),
                }

                result = await database.payment_transactions.insert_one(payment_transaction)
                payment_transaction["id"] = str(result.inserted_id)

                return {
                    "orderId": order_id,
                    "amount": amount,
                    "status": PaymentStatus.PENDING,
                    "message": "Payment order created successfully",
                    "razorpayKeyId": self.key_id,
                    "gatewayOrderId": rzp_order.get("id"),
                }
                
        except Exception as e:
            logger.error(f"Error creating payment order: {e}")
            raise Exception(f"Failed to create payment order: {str(e)}")

    async def verify_payment(self, order_id: str) -> Dict[str, Any]:
        """Verify payment status by querying Razorpay order and payments"""
        database = get_database()

        payment_transaction = await database.payment_transactions.find_one({"orderId": order_id})
        if not payment_transaction:
            raise Exception("Payment transaction not found")

        gateway_order_id = payment_transaction.get("gatewayOrderId")
        if not gateway_order_id:
            raise Exception("Gateway order id missing")

        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self._get_auth()) as client:
                order_resp = await client.get(f"{self.orders_url}/{gateway_order_id}")
                if order_resp.status_code not in (200, 201):
                    raise Exception(f"Failed to fetch Razorpay order: {order_resp.status_code}")
                order_data = order_resp.json()

                payments_resp = await client.get(f"{self.orders_url}/{gateway_order_id}/payments")
                payments_list = payments_resp.json().get("items", []) if payments_resp.status_code in (200, 201) else []

                payment_status = PaymentStatus.PENDING
                gateway_payment_id = None
                order_status = order_data.get("status")  # created, paid, attempted

                if order_status == "paid":
                    payment_status = PaymentStatus.SUCCESS
                elif order_status == "cancelled":
                    payment_status = PaymentStatus.CANCELLED

                for p in payments_list:
                    if p.get("status") == "captured":
                        payment_status = PaymentStatus.SUCCESS
                        gateway_payment_id = p.get("id")
                        break
                    if p.get("status") == "failed":
                        payment_status = PaymentStatus.FAILED
                        gateway_payment_id = p.get("id")
                        break

                update_data = {
                    "status": payment_status,
                    "gatewayResponse": {"order": order_data, "payments": payments_list},
                    "updatedAt": datetime.now(),
                }
                if gateway_payment_id:
                    update_data["gatewayPaymentId"] = gateway_payment_id
                if payment_status in [PaymentStatus.SUCCESS, PaymentStatus.FAILED, PaymentStatus.CANCELLED, PaymentStatus.EXPIRED]:
                    update_data["completedAt"] = datetime.now()

                await database.payment_transactions.update_one({"orderId": order_id}, {"$set": update_data})

                return {
                    "orderId": order_id,
                    "status": payment_status,
                    "orderStatus": order_status,
                    "payments": payments_list,
                    "gatewayPaymentId": gateway_payment_id,
                }

        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            raise Exception(f"Failed to verify payment: {str(e)}")

    async def process_successful_payment(self, order_id: str) -> bool:
        """Process successful payment by adding money to user's wallet"""
        database = get_database()
        
        # Get payment transaction
        payment_transaction = await database.payment_transactions.find_one({"orderId": order_id})
        if not payment_transaction:
            return False
        
        if payment_transaction["status"] != PaymentStatus.SUCCESS:
            return False
        
        user_id = payment_transaction["userId"]
        amount = payment_transaction["amount"]
        
        try:
            # Get user
            user = await database.users.find_one({"_id": user_id})
            if not user:
                return False
            
            # Update wallet balance
            new_balance = (user.get("walletBalance", 0) + amount)
            await database.users.update_one(
                {"_id": user_id},
                {"$set": {"walletBalance": new_balance}}
            )
            
            # Create wallet transaction
            wallet_transaction = {
                "userId": user_id,
                "transactionId": f"PAY_{order_id}",
                "transactionType": "credit",
                "amount": amount,
                "description": "Wallet top-up via payment gateway",
                "category": "deposit",
                "balanceBefore": user.get("walletBalance", 0),
                "balanceAfter": new_balance,
                "status": "completed",
                "createdAt": datetime.now()
            }
            
            await database.wallet_transactions.insert_one(wallet_transaction)
            
            logger.info(f"Successfully processed payment for order {order_id}, added {amount} to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
            return False

    async def get_payment_history(self, user_id: str, limit: int = 20, skip: int = 0) -> Dict[str, Any]:
        """Get user's payment history"""
        database = get_database()
        
        payments = []
        cursor = database.payment_transactions.find({"userId": user_id}).sort("createdAt", -1).skip(skip).limit(limit)
        
        async for payment in cursor:
            payment["id"] = str(payment["_id"])
            del payment["_id"]
            payments.append(payment)
        
        return {
            "payments": payments,
            "total": len(payments),
            "limit": limit,
            "skip": skip
        }

# Global instance
payment_service = PaymentService()

