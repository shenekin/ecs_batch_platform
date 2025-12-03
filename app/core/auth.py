from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from app.core.config import settings

# === FIXED SETTINGS MAPPINGS ===
API_PREFIX = "/api/v1"  # Set manually (or add to Settings)
API_KEY_HEADER = "X-API-Key"
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
VALID_API_KEYS = settings.API_KEY_WHITELIST
# ===============================

# JWT Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/token")

# API Key Setup
api_key_header = APIKeyHeader(
    name=API_KEY_HEADER,
    auto_error=False
)

def verify_jwt_token(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired JWT token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
        return {"user_id": user_id, "auth_type": "jwt"}
    except JWTError:
        raise credentials_exception


# === API Key Verification ===
def verify_api_key(api_key: str = Depends(api_key_header)) -> dict:
    """Validate API Key and return service context (for service-to-service auth)"""
    # auto_error=True ensures `api_key` is NOT None (no need for Optional[str])
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=403,  # Forbidden (invalid key) – not 401 (unauthorized)
            detail="Invalid API Key. Contact admin for a valid key.",
            headers={API_KEY_HEADER: "Invalid"}
        )
    return {"api_key": api_key, "auth_type": "api_key"}

def get_current_user(
    jwt_user: Optional[dict] = Depends(verify_jwt_token),
    api_key_user: Optional[dict] = Depends(verify_api_key)
) -> dict:
    if not jwt_user and not api_key_user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Provide JWT token or API Key",
            headers={API_KEY_HEADER: "Required"},
        )
    return jwt_user or api_key_user

auth_dependency = Depends(get_current_user)
