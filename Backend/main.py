from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
from database import connect_to_mongo, close_mongo_connection, get_database
from auth import get_password_hash
from routers import auth, users, contests, seats, wallet, admin, notifications, payments, simple_payments
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    # Ensure static upload directories exist
    try:
        os.makedirs(os.path.join("static", "uploads"), exist_ok=True)
    except Exception as _e:
        logger.error(f"Failed to ensure static/uploads directory: {_e}")
    # Ensure DB indexes: only email is unique; userId/phoneNumber non-unique
    try:
        db = get_database()
        # Drop potentially existing unique indexes on phoneNumber or userId
        try:
            indexes = await db.users.index_information()
            # Drop legacy phoneNumber index name if exists
            if "phoneNumber_1" in indexes:
                await db.users.drop_index("phoneNumber_1")
            # Drop legacy userId index name if exists
            if "userId_1" in indexes:
                await db.users.drop_index("userId_1")
            # Also try dropping our new names if they exist with wrong options
            for legacy_name in ["userId_idx", "phoneNumber_idx"]:
                try:
                    if legacy_name in indexes:
                        await db.users.drop_index(legacy_name)
                except Exception as _drop_e:
                    logger.warning(f"Dropping index {legacy_name} failed (may not exist): {_drop_e}")
        except Exception as _idxe:
            logger.warning(f"Issue inspecting/dropping user indexes: {_idxe}")

        # Create desired indexes
        try:
            await db.users.create_index("email", unique=True, name="email_1")
        except Exception as _cie:
            logger.warning(f"Creating unique index on email failed (may already exist): {_cie}")
        # userId/phoneNumber indexes are managed in database.create_indexes()
    except Exception as se_idx:
        logger.error(f"Error ensuring user indexes: {se_idx}")
    # Seed default users if they don't exist
    try:
        db = get_database()
        # Admin user
        admin = await db.users.find_one({"userId": "admin"})
        if not admin:
            await db.users.insert_one({
                "userName": "Administrator",
                "userId": "admin",
                "email": "admin@example.com",
                "phoneNumber": "9000000000",
                "password": get_password_hash("admin123#"),
                "profilePicture": None,
                "city": "",
                "state": "",
                "walletBalance": 0.0,
                "isActive": True,
                "extraParameter1": None,
                "createdAt": __import__('datetime').datetime.now(),
                "updatedAt": __import__('datetime').datetime.now(),
            })
            logger.info("Seeded default admin user: admin / admin123#")

        # Test user
        test_user = await db.users.find_one({"userId": "test"})
        if not test_user:
            await db.users.insert_one({
                "userName": "Test User",
                "userId": "test",
                "email": "test@example.com",
                "phoneNumber": "9000000001",
                "password": get_password_hash("test123#"),
                "profilePicture": None,
                "city": "",
                "state": "",
                "walletBalance": 0.0,
                "isActive": True,
                "extraParameter1": None,
                "createdAt": __import__('datetime').datetime.now(),
                "updatedAt": __import__('datetime').datetime.now(),
            })
            logger.info("Seeded default test user: test / test123#")
    except Exception as se:
        logger.error(f"Error seeding initial users: {se}")
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="BINDASS GRAND Lottery API",
    description="Backend API for BINDASS GRAND lottery system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(contests.router, prefix="/api/contests", tags=["Contests"])
app.include_router(seats.router, prefix="/api/seats", tags=["Seats"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(payments.router, prefix="/api/payment", tags=["Payments"])
app.include_router(simple_payments.router, prefix="/api/new/payment", tags=["new-payment"])

# Ensure static directory exists before mounting
try:
    os.makedirs(os.path.join("static", "uploads"), exist_ok=True)
except Exception as _e:
    logger.error(f"Failed to create static/uploads directory at import time: {_e}")

# Mount static files to serve uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "BINDASS GRAND Lottery API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/reset-password")
async def serve_reset_password_page():
    """Serve the password reset page"""
    return FileResponse("static/pages/reset-password.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
