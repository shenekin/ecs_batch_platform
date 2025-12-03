from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from limits.storage import MemoryStorage, RedisStorage
from limits.strategies import FixedWindowRateLimiter
from app.core.config import settings
import time

# Initialize storage (Redis for prod, in-memory for dev)
storage = RedisStorage(settings.REDIS_URL) if settings.REDIS_URL else MemoryStorage()

# Rate limiter: Key = IP + UserID/API Key (prevents shared limits)
limiter = Limiter(
    key_func=lambda request: f"{get_remote_address(request)}:{request.state.user['user_id']}"
    if request.state.user["auth_type"] == "jwt"
    else f"{get_remote_address(request)}:{request.state.user['api_key']}",
    storage_uri=settings.REDIS_URL,
    strategy=FixedWindowRateLimiter(storage)
)

async def request_size_limit_middleware(request: Request, call_next):
    """Reject requests exceeding MAX_REQUEST_SIZE (10MB)"""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.MAX_REQUEST_SIZE:
            raise HTTPException(
                status_code=413,  # Payload Too Large
                detail=f"Request size exceeds {settings.MAX_REQUEST_SIZE / 1024 / 1024}MB limit"
            )
    response = await call_next(request)
    return response

async def daily_quota_middleware(request: Request, call_next):
    """Reject requests exceeding DAILY_QUOTA"""
    user_identifier = request.state.user["user_id"] if request.state.user["auth_type"] == "jwt" else request.state.user["api_key"]
    quota_key = f"quota:{user_identifier}:{time.strftime('%Y%m%d')}"  # Daily unique key

    # Get current quota usage (initialize to 0 if not exists)
    current_usage = int(storage.get(quota_key) or 0)
    if current_usage >= settings.DAILY_QUOTA:
        raise HTTPException(
            status_code=429,  # Too Many Requests
            detail=f"Daily quota exceeded ({settings.DAILY_QUOTA} requests/day). Reset tomorrow."
        )

    # Increment quota (expire after 24 hours)
    storage.set(quota_key, current_usage + 1, expiry=86400)
    response = await call_next(request)
    return response
