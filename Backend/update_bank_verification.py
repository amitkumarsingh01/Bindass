#!/usr/bin/env python3
"""
Script to update all existing bank details to be auto-verified
Run this once to update existing data in the database
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URL

async def update_all_bank_details():
    """Update all existing bank details to be auto-verified"""
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client.bindass_grand
    
    print("🔄 Updating all bank details to be auto-verified...")
    
    # Update all bank details that are not verified
    result = await database.bank_details.update_many(
        {"isVerified": {"$ne": True}},
        {
            "$set": {
                "isVerified": True,
                "verifiedAt": datetime.now(),
                "updatedAt": datetime.now()
            }
        }
    )
    
    print(f"✅ Updated {result.modified_count} bank details to be auto-verified")
    
    # Count total verified bank details
    total_verified = await database.bank_details.count_documents({"isVerified": True})
    total_bank_details = await database.bank_details.count_documents({})
    
    print(f"📊 Total bank details: {total_bank_details}")
    print(f"✅ Verified bank details: {total_verified}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_all_bank_details())
