from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "bindass_grand"
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Cashfree Payment Gateway Configuration
    cashfree_client_id: str = "10778038a4f7f9a972c4db4739a3087701"
    cashfree_client_secret: str = "cfsk_ma_prod_3c29e1f44d603a53240d7a4d3189defa_2dd27ccb"
    cashfree_api_base: str = "https://api.cashfree.com"
    cashfree_webhook_secret: Optional[str] = None
    cashfree_return_url: str = "https://yourdomain.com/api/payment/return"
    cashfree_notify_url: str = "https://yourdomain.com/api/payment/notify"
    
    class Config:
        env_file = ".env"

settings = Settings()
