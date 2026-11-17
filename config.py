import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "farm-linker-secret-key-change-in-production")
    MONGO_URI = os.environ.get(
        "MONGO_URI",
        "mongodb+srv://<username>:<password>@cluster0.mongodb.net/farm_linker?retryWrites=true&w=majority"
    )
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "farm_linker")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
