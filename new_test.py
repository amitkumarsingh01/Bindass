from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import httpx
import hashlib
import base64
import json
from pydantic import BaseModel
import uvicorn
import os
import asyncio
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime

app = FastAPI()

# Cashfree credentials
CLIENT_ID = "10778038a4f7f9a972c4db4739a3087701"
CLIENT_SECRET = "cfsk_ma_prod_3c29e1f44d603a53240d7a4d3189defa_2dd27ccb"
# Prefer environment variable to allow switching between sandbox and production
# Example sandbox base: https://sandbox.cashfree.com
API_BASE = os.getenv("CASHFREE_API_BASE", "https://api.cashfree.com")
API_URL = f"{API_BASE}/pg/orders"
SESSIONS_URL = f"{API_BASE}/pg/orders/sessions"

# Pydantic model for payment details
class PaymentDetails(BaseModel):
    order_id: str
    order_amount: float
    customer_email: str
    customer_phone: str

# -------------------------
# Persistence (SQLite)
# -------------------------
DB_PATH = os.getenv("PAYMENTS_DB_PATH", "payments.db")

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT,
                customer_email TEXT,
                customer_phone TEXT,
                order_amount REAL,
                order_currency TEXT,
                status TEXT,
                payment_link TEXT,
                raw_json TEXT,
                created_at TEXT
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                order_id TEXT,
                payment_status TEXT,
                payment_amount REAL,
                raw_json TEXT,
                created_at TEXT
            );
            """
        )
        conn.commit()
    finally:
        conn.close()

def save_order_record(order: Dict[str, Any], details: PaymentDetails):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO orders (order_id, customer_id, customer_email, customer_phone, order_amount, order_currency, status, payment_link, raw_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                customer_id=excluded.customer_id,
                customer_email=excluded.customer_email,
                customer_phone=excluded.customer_phone,
                order_amount=excluded.order_amount,
                order_currency=excluded.order_currency,
                status=excluded.status,
                payment_link=excluded.payment_link,
                raw_json=excluded.raw_json
            ;
            """,
            (
                order.get("order_id"),
                (order.get("customer_details") or {}).get("customer_id") or details.customer_email,
                details.customer_email,
                details.customer_phone,
                float(order.get("order_amount") or details.order_amount),
                order.get("order_currency") or "INR",
                order.get("order_status") or "ACTIVE",
                order.get("payment_link"),
                json.dumps(order),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()

def upsert_payment_records(order_id: str, payments: List[Dict[str, Any]]):
    if not payments:
        return
    conn = _get_conn()
    try:
        cur = conn.cursor()
        for p in payments:
            payment_id = p.get("cf_payment_id") or p.get("payment_id") or p.get("id") or f"{order_id}:{p.get('payment_time') or p.get('created_at') or datetime.utcnow().isoformat()}"
            cur.execute(
                """
                INSERT INTO payments (payment_id, order_id, payment_status, payment_amount, raw_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(payment_id) DO UPDATE SET
                    order_id=excluded.order_id,
                    payment_status=excluded.payment_status,
                    payment_amount=excluded.payment_amount,
                    raw_json=excluded.raw_json
                ;
                """,
                (
                    str(payment_id),
                    order_id,
                    p.get("payment_status") or p.get("status"),
                    float(p.get("payment_amount") or p.get("amount") or 0),
                    json.dumps(p),
                    datetime.utcnow().isoformat(),
                ),
            )
        conn.commit()
    finally:
        conn.close()

def list_orders(customer_email: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        if customer_email:
            cur.execute("SELECT * FROM orders WHERE customer_email = ? ORDER BY created_at DESC", (customer_email,))
        else:
            cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()

def list_payments(customer_email: Optional[str] = None, order_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        if order_id:
            cur.execute("SELECT p.* FROM payments p WHERE p.order_id = ? ORDER BY created_at DESC", (order_id,))
        elif customer_email:
            # Join orders to filter by customer_email
            cur.execute(
                """
                SELECT p.* FROM payments p
                JOIN orders o ON o.order_id = p.order_id
                WHERE o.customer_email = ?
                ORDER BY p.created_at DESC
                """,
                (customer_email,),
            )
        else:
            cur.execute("SELECT * FROM payments ORDER BY created_at DESC")
        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()

# Function to create order on Cashfree
async def create_order(payment_details: PaymentDetails):
    headers = {
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-api-version": "2022-01-01",
        "Content-Type": "application/json"
    }
    data = {
        "order_id": payment_details.order_id,
        "order_amount": payment_details.order_amount,
        "order_currency": "INR",
        "customer_details": {
            # Cashfree expects a customer_id; use email as a stable identifier if not separate
            "customer_id": payment_details.customer_email,
            "customer_email": payment_details.customer_email,
            "customer_phone": payment_details.customer_phone
        },
        "order_meta": {
            "return_url": f"https://yourdomain.com/payment/return?order_id={payment_details.order_id}",
            "notify_url": "https://yourdomain.com/payment/notify"
        }
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(API_URL, headers=headers, json=data)
        # Cashfree may return 201 Created on success
        try:
            response_data = response.json()
        except Exception:
            response_data = {"raw": response.text}

        # If payment_session_id is present (rare in some flows), return directly
        if response.status_code in (200, 201) and response_data.get("payment_session_id"):
            # Persist order record
            try:
                save_order_record(response_data, payment_details)
            except Exception:
                pass
            return response_data

        # If order_token is present, create a session to get payment_session_id
        if response.status_code in (200, 201) and response_data.get("order_token"):
            session_payload = {
                "order_id": response_data.get("order_id"),
                "order_token": response_data.get("order_token"),
            }
            session_resp = await client.post(SESSIONS_URL, headers=headers, json=session_payload)
            try:
                session_data = session_resp.json()
            except Exception:
                session_data = {"raw": session_resp.text}

            if session_resp.status_code in (200, 201) and session_data.get("payment_session_id"):
                # Merge useful fields for the client
                merged = {
                    **response_data,
                    "payment_session_id": session_data.get("payment_session_id"),
                }
                # Persist order record
                try:
                    save_order_record(merged, payment_details)
                except Exception:
                    pass
                return merged
            else:
                # Even if session creation fails, return the order with payment_link
                # This allows users to pay via the payment_link
                try:
                    save_order_record(response_data, payment_details)
                except Exception:
                    pass
                return response_data

        # Surface Cashfree error for easier debugging
        error_detail = response_data if isinstance(response_data, dict) else {"message": str(response_data)}
        raise HTTPException(status_code=400, detail={
            "message": "Failed to create order",
            "status_code": response.status_code,
            "cashfree_response": error_detail,
        })

# Route to initiate payment
@app.post("/pay")
async def initiate_payment(payment_details: PaymentDetails):
    order_response = await create_order(payment_details)
    payment_session_id = order_response.get("payment_session_id")
    payment_link = order_response.get("payment_link")
    return {
        "payment_session_id": payment_session_id,
        "payment_link": payment_link,
        "order": order_response,
    }

# Optional: check order status from Cashfree (useful for server-side verification)
@app.get("/payment/status")
async def payment_status(order_id: str):
    headers = {
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-api-version": "2022-01-01",
        "Content-Type": "application/json"
    }
    url = f"{API_URL}/{order_id}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
        if resp.status_code in (200, 201):
            # Update local order status if present
            try:
                conn = _get_conn()
                try:
                    conn.execute(
                        "UPDATE orders SET status = ?, raw_json = ? WHERE order_id = ?",
                        (
                            (data or {}).get("order_status"),
                            json.dumps(data),
                            order_id,
                        ),
                    )
                    conn.commit()
                finally:
                    conn.close()
            except Exception:
                pass
            return data
        raise HTTPException(status_code=resp.status_code, detail=data)

# Helper: fetch order and payments
async def _fetch_order(client: httpx.AsyncClient, headers: dict, order_id: str):
    resp = await client.get(f"{API_URL}/{order_id}", headers=headers)
    return resp

async def _fetch_payments(client: httpx.AsyncClient, headers: dict, order_id: str):
    resp = await client.get(f"{API_URL}/{order_id}/payments", headers=headers)
    return resp

# Polling endpoint: check status until terminal or timeout
@app.get("/payment/poll")
async def poll_payment(order_id: str, timeout_seconds: int = 45, interval_ms: int = 1500):
    headers = {
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-api-version": "2022-01-01",
        "Content-Type": "application/json"
    }
    terminal_order_statuses = {"PAID", "CANCELLED", "EXPIRED"}
    terminal_payment_statuses = {"SUCCESS", "FAILED"}

    started = asyncio.get_event_loop().time()
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            # Fetch order
            order_resp = await _fetch_order(client, headers, order_id)
            try:
                order_data = order_resp.json()
            except Exception:
                order_data = {"raw": order_resp.text}

            # If we got order details, check order_status
            if order_resp.status_code in (200, 201):
                order_status = (order_data or {}).get("order_status")
                if order_status in terminal_order_statuses:
                    return {
                        "order_id": order_id,
                        "state": "terminal",
                        "order_status": order_status,
                        "order": order_data,
                    }

            # Fetch payments list
            pay_resp = await _fetch_payments(client, headers, order_id)
            try:
                payments_data = pay_resp.json()
            except Exception:
                payments_data = {"raw": pay_resp.text}

            # Cashfree returns list under "payments" or array directly depending on API
            payments_list = []
            if isinstance(payments_data, dict) and isinstance(payments_data.get("data"), list):
                payments_list = payments_data.get("data", [])
            elif isinstance(payments_data, list):
                payments_list = payments_data

            # Find terminal payment, if any
            for p in payments_list:
                status = p.get("payment_status") or p.get("status")
                if status in terminal_payment_statuses:
                    # Upsert payment records locally
                    try:
                        upsert_payment_records(order_id, [p])
                    except Exception:
                        pass
                    return {
                        "order_id": order_id,
                        "state": "terminal",
                        "payment_status": status,
                        "payment": p,
                        "payments": payments_list,
                        "order": order_data,
                    }

            # Timeout check
            elapsed = asyncio.get_event_loop().time() - started
            if elapsed >= timeout_seconds:
                return {
                    "order_id": order_id,
                    "state": "timeout",
                    "elapsed_seconds": int(elapsed),
                    "order": order_data,
                    "payments": payments_list,
                }

            # Wait and retry
            await asyncio.sleep(max(0.1, interval_ms / 1000))

# Sync/refresh payments for an order from Cashfree and store locally
@app.post("/payments/refresh")
async def refresh_payments(order_id: str):
    headers = {
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-api-version": "2022-01-01",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        pay_resp = await client.get(f"{API_URL}/{order_id}/payments", headers=headers)
        try:
            payments_data = pay_resp.json()
        except Exception:
            payments_data = {"raw": pay_resp.text}

        if pay_resp.status_code not in (200, 201):
            raise HTTPException(status_code=pay_resp.status_code, detail=payments_data)

        payments_list: List[Dict[str, Any]] = []
        if isinstance(payments_data, dict) and isinstance(payments_data.get("data"), list):
            payments_list = payments_data.get("data", [])
        elif isinstance(payments_data, list):
            payments_list = payments_data

        try:
            upsert_payment_records(order_id, payments_list)
        except Exception:
            pass
        return {"order_id": order_id, "count": len(payments_list), "payments": payments_list}

# Public listing endpoints
@app.get("/orders")
async def get_orders(customer_email: Optional[str] = None):
    return {"orders": list_orders(customer_email)}

@app.get("/payments")
async def get_payments(customer_email: Optional[str] = None, order_id: Optional[str] = None):
    return {"payments": list_payments(customer_email, order_id)}

# Function to generate payment token
def generate_payment_token(payment_session_id: str) -> str:
    token_data = f"appId={CLIENT_ID}&paymentSessionId={payment_session_id}"
    token = hashlib.sha256(token_data.encode()).digest()
    return base64.b64encode(token).decode()

# Route to handle return from Cashfree
@app.get("/payment/return")
async def payment_return(order_id: str, cf_status: str = None, cf_message: str = None):
    # Verify payment status here
    return {"order_id": order_id, "status": cf_status, "message": cf_message}

# Route to handle payment notifications (webhooks)
@app.post("/payment/notify")
async def payment_notify(payload: dict):
    # Process the notification payload
    return {"status": "received", "data": payload}

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8007)