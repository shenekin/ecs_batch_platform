from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, List
from datetime import timedelta

class Settings(BaseSettings):
    # App Configuration
    APP_TITLE: str = "Batch ECS Creation API Gateway"
    APP_VERSION: str = "v1"
    APP_DESCRIPTION: str = "API Inbound Layer - Batch Job Creation Entry"
    
    # Security Configuration
    JWT_SECRET_KEY: str = "your-strong-secret-key-32bytes-long-123456"  # Inject via env in production
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY_WHITELIST: List[str] = ["api-key-test-123"]  # Test only; use env in production
    
    # Rate Limiting Configuration
    RATE_LIMIT: str = "1000/minute"  # 100 requests per user per minute
    MAX_REQUEST_SIZE: int = 20 * 1024 * 1024  # 20MB (max request body size)
    
    # Quota Configuration
    MAX_DAILY_JOBS_PER_USER: int = 1000  # Max daily jobs per user
    MAX_BATCH_SIZE: int = 10000  # Max records per request (after CSV/Excel parsing)
    
    # Kafka Configuration (Event-Driven)
    KAFKA_BOOTSTRAP_SERVERS: Optional[str] = "localhost:9092"
    KAFKA_TOPIC: str = "batch-job-requests"
    
    # Storage Configuration (Temporary JobID storage; use Redis/MongoDB in production)
    JOB_STORAGE: Dict[str, dict] = {}  # In-memory storage (test only)
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
print(settings,"Configuration loaded successfully.")
    # Additional configurations can be added here as needed
    # e.g., Database settings, Logging settings, etc.   
    # Additional configurations can be added here as needed
    # e.g., Database settings, Logging settings, etc.

