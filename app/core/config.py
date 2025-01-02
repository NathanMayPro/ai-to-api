from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "AI to API Platform"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-default")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "api_platform"
    MONGO_USERNAME: str | None = None
    MONGO_PASSWORD: str | None = None
    
    # Stripe settings
    STRIPE_SECRET_KEY: str = "your-stripe-secret-key"
    STRIPE_WEBHOOK_SECRET: str = "your-stripe-webhook-secret"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Test settings
    TEST_EMAIL: str = os.getenv("TEST_EMAIL")
    TEST_USERNAME: str = os.getenv("TEST_USERNAME")
    TEST_PASSWORD: str = os.getenv("TEST_PASSWORD")

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_prefix = ""

    @property
    def mongodb_url(self) -> str:
        if self.MONGO_USERNAME and self.MONGO_PASSWORD:
            return f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@cluster0.mongodb.net/{self.MONGODB_DB_NAME}?retryWrites=true&w=majority"
        return self.MONGODB_URL

settings = Settings() 