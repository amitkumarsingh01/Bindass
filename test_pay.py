import requests
import datetime

# Your Cashfree credentials
CLIENT_ID = "10778038a4f7f9a972c4db4739a3087701"
CLIENT_SECRET = "cfsk_ma_prod_3c29e1f44d603a53240d7a4d3189defa_2dd27ccb"
API_VERSION = "2025-01-01"  # or whichever version your account supports
ENV = "PRODUCTION"  # Or "SANDBOX". If sandbox, use sandbox URL.

def create_payment_link(amount, currency, customer_name, customer_phone, customer_email, return_url=None, expiry_days=7):
    if ENV == "SANDBOX":
        base_url = "https://sandbox.cashfree.com/pg/links"
    else:
        base_url = "https://api.cashfree.com/pg/links"
    
    expiry_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=expiry_days)).isoformat()
    
    payload = {
        "link_amount": amount,
        "link_currency": currency,
        "link_purpose": "Payment for something",  # customize
        "customer_details": {
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "customer_email": customer_email
        },
        # optional meta
        "link_meta": {}
    }
    
    if return_url:
        payload["link_meta"]["return_url"] = return_url
    
    payload["link_expiry_time"] = expiry_time
    
    headers = {
        "Content-Type": "application/json",
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-api-version": API_VERSION
    }
    
    resp = requests.post(base_url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # Assuming success; else you need to catch status codes/errors
    link_url = data.get("link_url")
    return data, link_url

# Example usage:
if __name__ == "__main__":
    data, url = create_payment_link(
        amount=100.0,
        currency="INR",
        customer_name="John Doe",
        customer_phone="9865478525",
        customer_email="john@doe.com",
        return_url="https://yourdomain.com/payment-return"
    )
    print("Payment Link created:", url)
    print("Full response:", data)
