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
        self.client_id = settings.cashfree_client_id
        self.client_secret = settings.cashfree_client_secret
        self.api_base = settings.cashfree_api_base
        self.orders_url = f"{self.api_base}/pg/orders"
        self.sessions_url = f"{self.api_base}/pg/orders/sessions"
        self.return_url = settings.cashfree_return_url
        self.notify_url = settings.cashfree_notify_url

    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-client-id": self.client_id,
            "x-client-secret": self.client_secret,
            "x-api-version": "2022-01-01",
            "Content-Type": "application/json"
        }

    async def create_payment_order(
        self, 
        user_id: str, 
        amount: float, 
        customer_email: str, 
        customer_phone: str,
        description: str = "Wallet top-up"
    ) -> Dict[str, Any]:
        """Create a payment order with Cashfree"""
        database = get_database()
        
        # Generate unique order ID
        order_id = f"WALLET_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # Prepare order data
        order_data = {
            "order_id": order_id,
            "order_amount": amount,
            "order_currency": "INR",
            "customer_details": {
                "customer_id": user_id,
                "customer_email": customer_email,
                "customer_phone": customer_phone
            },
            "order_meta": {
                "return_url": f"{self.return_url}?order_id={order_id}",
                "notify_url": self.notify_url
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Create order
                response = await client.post(
                    self.orders_url, 
                    headers=self._get_headers(), 
                    json=order_data
                )
                
                if response.status_code not in (200, 201):
                    raise Exception(f"Cashfree API error: {response.status_code} - {response.text}")
                
                response_data = response.json()
                
                # Create payment transaction record
                payment_transaction = {
                    "userId": user_id,
                    "orderId": order_id,
                    "amount": amount,
                    "currency": "INR",
                    "gateway": PaymentGateway.CASHFREE,
                    "gatewayOrderId": response_data.get("cf_order_id"),
                    "paymentLink": response_data.get("payment_link"),
                    "status": PaymentStatus.PENDING,
                    "gatewayResponse": response_data,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now()
                }
                
                # Try to create session for payment_session_id
                if response_data.get("order_token"):
                    try:
                        session_payload = {
                            "order_id": order_id,
                            "order_token": response_data.get("order_token")
                        }
                        session_resp = await client.post(
                            self.sessions_url, 
                            headers=self._get_headers(), 
                            json=session_payload
                        )
                        
                        if session_resp.status_code in (200, 201):
                            session_data = session_resp.json()
                            if session_data.get("payment_session_id"):
                                payment_transaction["paymentSessionId"] = session_data.get("payment_session_id")
                    except Exception as e:
                        logger.warning(f"Failed to create payment session: {e}")
                
                # Save payment transaction to database
                result = await database.payment_transactions.insert_one(payment_transaction)
                payment_transaction["id"] = str(result.inserted_id)
                
                return {
                    "orderId": order_id,
                    "amount": amount,
                    "paymentLink": payment_transaction.get("paymentLink"),
                    "paymentSessionId": payment_transaction.get("paymentSessionId"),
                    "status": PaymentStatus.PENDING,
                    "message": "Payment order created successfully"
                }
                
        except Exception as e:
            logger.error(f"Error creating payment order: {e}")
            raise Exception(f"Failed to create payment order: {str(e)}")

    async def verify_payment(self, order_id: str) -> Dict[str, Any]:
        """Verify payment status by polling Cashfree"""
        database = get_database()
        
        # Get payment transaction
        payment_transaction = await database.payment_transactions.find_one({"orderId": order_id})
        if not payment_transaction:
            raise Exception("Payment transaction not found")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get order status
                order_resp = await client.get(
                    f"{self.orders_url}/{order_id}",
                    headers=self._get_headers()
                )
                
                if order_resp.status_code not in (200, 201):
                    raise Exception(f"Failed to fetch order status: {order_resp.status_code}")
                
                order_data = order_resp.json()
                
                # Get payments
                payments_resp = await client.get(
                    f"{self.orders_url}/{order_id}/payments",
                    headers=self._get_headers()
                )
                
                payments_data = []
                if payments_resp.status_code in (200, 201):
                    payments_response = payments_resp.json()
                    if isinstance(payments_response, dict) and isinstance(payments_response.get("data"), list):
                        payments_data = payments_response.get("data", [])
                    elif isinstance(payments_response, list):
                        payments_data = payments_response
                
                # Determine payment status
                payment_status = PaymentStatus.PENDING
                gateway_payment_id = None
                
                # Check order status
                order_status = order_data.get("order_status")
                if order_status == "PAID":
                    payment_status = PaymentStatus.SUCCESS
                elif order_status in ["CANCELLED", "EXPIRED"]:
                    payment_status = PaymentStatus.CANCELLED if order_status == "CANCELLED" else PaymentStatus.EXPIRED
                
                # Check individual payments
                for payment in payments_data:
                    payment_status_value = payment.get("payment_status") or payment.get("status")
                    if payment_status_value == "SUCCESS":
                        payment_status = PaymentStatus.SUCCESS
                        gateway_payment_id = payment.get("cf_payment_id") or payment.get("payment_id")
                        break
                    elif payment_status_value == "FAILED":
                        payment_status = PaymentStatus.FAILED
                        break
                
                # Update payment transaction
                update_data = {
                    "status": payment_status,
                    "gatewayResponse": order_data,
                    "updatedAt": datetime.now()
                }
                
                if gateway_payment_id:
                    update_data["gatewayPaymentId"] = gateway_payment_id
                
                if payment_status in [PaymentStatus.SUCCESS, PaymentStatus.FAILED, PaymentStatus.CANCELLED, PaymentStatus.EXPIRED]:
                    update_data["completedAt"] = datetime.now()
                
                await database.payment_transactions.update_one(
                    {"orderId": order_id},
                    {"$set": update_data}
                )
                
                return {
                    "orderId": order_id,
                    "status": payment_status,
                    "orderStatus": order_status,
                    "payments": payments_data,
                    "gatewayPaymentId": gateway_payment_id
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

