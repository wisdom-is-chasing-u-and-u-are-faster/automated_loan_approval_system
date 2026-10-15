import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Enterprise Automatic Loan Approval System (ALAS)"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./alas.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "alas-dev-secret-key-3815-super-secure-token-signing")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

settings = Settings()
