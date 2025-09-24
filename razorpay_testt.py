from fastapi import FastAPI
from pydantic import BaseModel
import razorpay
import os
import uvicorn

app = FastAPI()

# Configure Razorpay client
# Replace with your Razorpay Key & Secret
RAZORPAY_KEY_ID = "rzp_live_RKWsm0Yu35R03E"
RAZORPAY_KEY_SECRET = "vP14iBFn9tAik0GyMrl0sIyM"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


class PaymentRequest(BaseModel):
    user_id: str
    amount: int   # in INR


@app.post("/create_payment/")
def create_payment(data: PaymentRequest):
    try:
        # Razorpay expects amount in paise (₹1 = 100 paise)
        payment = client.payment_link.create({
            "amount": data.amount * 100,
            "currency": "INR",
            "description": f"Payment for user {data.user_id}",
            "customer": {
                "name": f"User-{data.user_id}",
                "email": "test@example.com",  # you can make this dynamic
            },
            "notify": {"sms": False, "email": False},
            "callback_url": "http://localhost:8062/payment_callback",
            "callback_method": "get"
        })

        return {
            "payment_id": payment["id"],
            "payment_url": payment["short_url"]
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/check_status/{payment_id}")
def check_status(payment_id: str):
    try:
        payment = client.payment_link.fetch(payment_id)
        return {
            "status": payment["status"],  # created / paid / cancelled
            "amount": payment["amount"] / 100,
            "id": payment["id"]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8062)