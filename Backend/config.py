from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "bindass_grand"
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 300
    
    # Razorpay Payment Gateway Configuration
    # razorpay_key_id: str = "rzp_live_RKwDSlcvXD4E14"
    # razorpay_key_secret: str = "vP14iBFn9tAik0GyMrl0sIyM"
    razorpay_key_id: str = "rzp_live_RKWsm0Yu35R03E"
    razorpay_key_secret: str = "vP14iBFn9tAik0GyMrl0sIyM"
    razorpay_api_base: str = "https://api.razorpay.com/v1"
    razorpay_return_url: str = "https://yourdomain.com/api/payment/return"
    
    # Email Configuration for forgot password
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "bindassgrand@gmail.com"  # Replace with your email
    smtp_password: str = "bjtbkadanltetlpa"     # Replace with your app password
    from_email: str = "bindassgrand@gmail.com"     # Replace with your email
    frontend_url: str = "https://server.bindassgrand.com"  # Replace with your frontend URL
    
    class Config:
        env_file = ".env"

settings = Settings()
