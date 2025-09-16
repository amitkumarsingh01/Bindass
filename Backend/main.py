from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from database import connect_to_mongo, close_mongo_connection, get_database
from auth import get_password_hash
from routers import auth, users, contests, seats, wallet, admin, notifications
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
