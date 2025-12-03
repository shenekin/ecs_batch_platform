from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.auth import verify_api_key , verify_jwt_token

router = APIRouter(tags=["Authentication"], prefix="/auth")

def create_access_token(data: dict) -> str:
    """Generate signed JWT token with expiry"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/token", summary="Get JWT Token (API Key Required)")
async def get_jwt_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    # _: dict = Depends(verify_api_key) , # Fix: Use _ for unused dependency
    _: dict = Depends(verify_jwt_token)
):
    """
    Retrieve JWT token for user authentication:
    - Requires valid API Key (X-API-Key header)
    - Requires username/password (replace with your user DB in prod)
    """
    # Replace with real user authentication (e.g., query PostgreSQL/MySQL)
    if form_data.username != "admin" or form_data.password != "1qaz@WSX":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_seconds": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/apikey", summary="Get API Token (API Key Required)")
async def get_api_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    _: dict = Depends(verify_api_key) , # Fix: Use _ for unused dependency
):
    """
    Retrieve JWT token for user authentication:
    - Requires valid API Key (X-API-Key header)
    - Requires username/password (replace with your user DB in prod)
    """
    # Replace with real user authentication (e.g., query PostgreSQL/MySQL)
    if form_data.username != "admin" or form_data.password != "1qaz@WSX":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_seconds": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
