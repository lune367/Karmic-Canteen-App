import os

class Config:
    # Database
    DATABASE_PATH = "karmic_canteen.db"
    
    # JWT Secret Key
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
    
    # API Settings
    API_PREFIX = "/api/admin"
    HOST = "0.0.0.0"
    PORT = 8000
    
    # CORS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]