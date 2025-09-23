from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "bindass_grand"
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Razorpay Payment Gateway Configuration
    razorpay_key_id: str = "rzp_test_1234567890abcdef"
    razorpay_key_secret: str = "test_key_secret_change_me"
    razorpay_api_base: str = "https://api.razorpay.com/v1"
    razorpay_return_url: str = "https://yourdomain.com/api/payment/return"
    
    class Config:
        env_file = ".env"

settings = Settings()
