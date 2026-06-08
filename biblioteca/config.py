import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    MONGODB_URI = os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017/biblioteca",
    )
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
