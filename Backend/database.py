from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for performance optimization"""
    try:
        # Users Collection Indexes
        await db.database.users.create_index("userId", unique=True)
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("phoneNumber", unique=True)
        
        # Purchased Seats Collection Indexes
        await db.database.purchased_seats.create_index([("contestId", 1), ("seatNumber", 1)], unique=True)
        await db.database.purchased_seats.create_index("userId")
        await db.database.purchased_seats.create_index([("contestId", 1), ("categoryId", 1)])
        
        # Contests Collection Indexes
        await db.database.contests.create_index("status")
        await db.database.contests.create_index("contestStartDate")
        
        # Wallet Transactions Collection Indexes
        await db.database.wallet_transactions.create_index([("userId", 1), ("createdAt", -1)])
        await db.database.wallet_transactions.create_index("transactionId", unique=True)
        
        # Winners Collection Indexes
        await db.database.winners.create_index("contestId")
        await db.database.winners.create_index("userId")
        
        # Bank Details Collection Indexes
        await db.database.bank_details.create_index("userId")
        
        # Withdrawals Collection Indexes
        await db.database.withdrawals.create_index([("userId", 1), ("status", 1)])
        
        # Notifications Collection Indexes
        await db.database.notifications.create_index([("userId", 1), ("isRead", 1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    return db.database
