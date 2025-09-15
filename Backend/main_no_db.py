from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BINDASS GRAND Lottery API",
    description="Backend API for BINDASS GRAND lottery system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "BINDASS GRAND Lottery API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/setup")
async def setup_info():
    return {
        "message": "BINDASS GRAND Backend is ready!",
        "note": "MongoDB connection required for full functionality",
        "endpoints": {
            "docs": "http://localhost:8000/docs",
            "health": "http://localhost:8000/health"
        },
        "next_steps": [
            "1. Install MongoDB locally or use MongoDB Atlas",
            "2. Update MONGODB_URL in config.py",
            "3. Run: python main.py (instead of this file)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

