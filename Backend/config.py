from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "bindass_grand"
    secret_key: str = "your-secret-key-change-this-in-production" 
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    # Cashfree settings
    cashfree_client_id: Optional[str] = "10778038a4f7f9a972c4db4739a3087701"
    cashfree_client_secret: Optional[str] = "cfsk_ma_prod_3c29e1f44d603a53240d7a4d3189defa_2dd27ccb"
    cashfree_environment: str = "production"  # sandbox or production
    
    class Config:
        env_file = ".env"

settings = Settings()
