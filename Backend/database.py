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
        # Helper to check if an index with the same key pattern already exists
        async def ensure_index(collection, keys, unique=False, name=None):
            try:
                info = await collection.index_information()
                # Normalize keys to list of tuples
                norm_keys = keys if isinstance(keys, list) else [(keys, 1)] if isinstance(keys, str) else keys
                for idx in info.values():
                    if idx.get('key') == norm_keys:
                        return  # Index with same keys exists; do not recreate with a different name
                await collection.create_index(keys, unique=unique, name=name)
            except Exception as _e:
                logger.warning(f"Ensuring index on {getattr(collection, 'name', 'unknown')} failed: {_e}")
        # Users Collection Indexes
        # Only ensure unique email index; leave existing userId/phoneNumber indexes untouched
        try:
            await ensure_index(db.database.users, "email", unique=True, name="email_1")
        except Exception as _email_idx_e:
            logger.warning(f"Ensuring unique email index failed (may exist): {_email_idx_e}")
        
        # Purchased Seats Collection Indexes
        # Drop legacy composite index if it exists with a different name
        try:
            ps_indexes = await db.database.purchased_seats.index_information()
            if "contestId_1_seatNumber_1" in ps_indexes:
                await db.database.purchased_seats.drop_index("contestId_1_seatNumber_1")
        except Exception as _ps_e:
            logger.warning(f"Inspect/drop legacy purchased_seats index issue: {_ps_e}")
        await ensure_index(db.database.purchased_seats, [("contestId", 1), ("seatNumber", 1)], unique=True, name="contest_seat_unique")
        await ensure_index(db.database.purchased_seats, "userId", name="purchased_userId_idx")
        await ensure_index(db.database.purchased_seats, [("contestId", 1), ("categoryId", 1)], name="contest_category_idx")
        
        # Contests Collection Indexes
        await ensure_index(db.database.contests, "status", name="contest_status_idx")
        await ensure_index(db.database.contests, "contestStartDate", name="contest_start_idx")
        
        # Wallet Transactions Collection Indexes
        await ensure_index(db.database.wallet_transactions, [("userId", 1), ("createdAt", -1)], name="wallet_user_date_idx")
        await ensure_index(db.database.wallet_transactions, "transactionId", unique=True, name="wallet_txn_unique")
        
        # Winners Collection Indexes
        await ensure_index(db.database.winners, "contestId", name="winners_contest_idx")
        await ensure_index(db.database.winners, "userId", name="winners_user_idx")
        
        # Bank Details Collection Indexes
        await ensure_index(db.database.bank_details, "userId", name="bank_user_idx")
        
        # Withdrawals Collection Indexes
        await ensure_index(db.database.withdrawals, [("userId", 1), ("status", 1)], name="withdraw_user_status_idx")
        
        # Notifications Collection Indexes
        await ensure_index(db.database.notifications, [("userId", 1), ("isRead", 1)], name="notif_user_read_idx")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    return db.database
