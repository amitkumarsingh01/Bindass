# test_payment_link.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import os
import uvicorn

app = FastAPI()

# Load from env or hard-code for testing
CLIENT_ID = os.getenv("CASHFREE_CLIENT_ID", "10778038a4f7f9a972c4db4739a3087701")
CLIENT_SECRET = os.getenv("CASHFREE_CLIENT_SECRET", "cfsk_ma_prod_3c29e1f44d603a53240d7a4d3189defa_2dd27ccb")
ENV = "production"  # or "production"

# According to docs: base URL for PG new APIs
BASE_URL = "https://sandbox.cashfree.com/pg" if ENV == "sandbox" else "https://api.cashfree.com/pg"

# API version you are using
X_API_VERSION = "2023-08-01"


class PaymentLinkRequest(BaseModel):
    customer_id: str
    customer_phone: str
    customer_email: str
    order_amount: float
    order_currency: str = "INR"
    link_validity_minutes: int = 60   # optional, how long link stays valid
    return_url: str = None            # optional, redirect after payment success/failure


@app.post("/create-payment-link")
def create_payment_link(req: PaymentLinkRequest):
    try:
        url = f"{BASE_URL}/payment-links"
        headers = {
            "Content-Type": "application/json",
            "x-api-version": X_API_VERSION,
            "x-client-id": CLIENT_ID,
            "x-client-secret": CLIENT_SECRET
        }
        body = {
            "customer_details": {
                "customer_id": req.customer_id,
                "customer_phone": req.customer_phone,
                "customer_email": req.customer_email,
            },
            "link_details": {
                "amount": req.order_amount,
                "currency": req.order_currency,
                "expiry_minutes": req.link_validity_minutes,
            }
        }
        if req.return_url:
            body["link_details"]["return_url"] = req.return_url

        resp = requests.post(url, json=body, headers=headers)
        resp.raise_for_status()

        data = resp.json()

        # The response has something like link_url
        return {
            "payment_link": data.get("link_url"),
            "link_id": data.get("link_id"),
            **data
        }
    except requests.HTTPError as http_err:
        return JSONResponse(status_code=resp.status_code, content={"error": resp.text})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/")
def root():
    return {"msg": "Cashfree Payment Link Test API Up"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)