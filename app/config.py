import os

SECRET_KEY = os.getenv("SECRET_KEY", "ssms-enterprise-jwt-super-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ssms.db")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_ssms_stripe_secret_key_12345")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_ssms_webhook_secret_67890")
