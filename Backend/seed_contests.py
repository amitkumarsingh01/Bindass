#!/usr/bin/env python3
"""
Seed three default contests with 10 categories each and 1..10000 seat mapping.

Contests:
- Rs 100  -> total prize 9.5 lakh
- Rs 200  -> total prize 19 lakh
- Rs 300  -> total prize 29 lakh

Run:
  python seed_contests.py
"""

import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings


def categories_1_to_10000():
    return [
        {"categoryId": 1, "categoryName": "Bike", "seatRangeStart": 1, "seatRangeEnd": 1000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 2, "categoryName": "Auto", "seatRangeStart": 1001, "seatRangeEnd": 2000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 3, "categoryName": "Car", "seatRangeStart": 2001, "seatRangeEnd": 3000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 4, "categoryName": "Jeep", "seatRangeStart": 3001, "seatRangeEnd": 4000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 5, "categoryName": "Van", "seatRangeStart": 4001, "seatRangeEnd": 5000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 6, "categoryName": "Bus", "seatRangeStart": 5001, "seatRangeEnd": 6000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 7, "categoryName": "Lorry", "seatRangeStart": 6001, "seatRangeEnd": 7000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 8, "categoryName": "Train", "seatRangeStart": 7001, "seatRangeEnd": 8000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 9, "categoryName": "Helicopter", "seatRangeStart": 8001, "seatRangeEnd": 9000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
        {"categoryId": 10, "categoryName": "Airplane", "seatRangeStart": 9001, "seatRangeEnd": 10000, "totalSeats": 1000, "availableSeats": 1000, "purchasedSeats": 0},
    ]


async def seed():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    async def upsert_contest(name: str, ticket_price: float, total_prize: float):
        existing = await db.contests.find_one({"contestName": name, "ticketPrice": ticket_price})
        if existing:
            print(f"✔ Contest already exists: {name} (ticket {ticket_price}) -> _id={existing['_id']}")
            return existing["_id"]

        now = datetime.now()
        doc = {
            "contestName": name,
            "totalPrizeMoney": total_prize,
            "ticketPrice": ticket_price,
            "totalSeats": 10000,
            "availableSeats": 10000,
            "purchasedSeats": 0,
            "totalWinners": 0,
            "status": "active",
            "contestStartDate": now,
            "contestEndDate": now + timedelta(days=7),
            "drawDate": now + timedelta(days=8),
            "isDrawCompleted": False,
            "categories": categories_1_to_10000(),
            "createdAt": now,
            "updatedAt": now,
        }
        res = await db.contests.insert_one(doc)
        print(f"➕ Inserted contest: {name} (ticket {ticket_price}) -> _id={res.inserted_id}")
        return res.inserted_id

    try:
        await upsert_contest("Rs 100 Contest", 100.0, 950000.0)
        await upsert_contest("Rs 200 Contest", 200.0, 1900000.0)
        await upsert_contest("Rs 300 Contest", 300.0, 2900000.0)
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed())


