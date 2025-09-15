from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from database import connect_to_mongo, close_mongo_connection
from routers import auth, users, contests, seats, wallet, admin, notifications

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
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

@app.get("/")
async def root():
    return {"message": "BINDASS GRAND Lottery API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
