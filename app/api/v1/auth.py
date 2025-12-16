from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from app.schemas.auth import UserLogin, Token
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.api.deps import get_db

router = APIRouter()
security_scheme = HTTPBearer()


async def get_user_service(db=Depends(get_db)):
    """Dependency to inject database into UserService."""
    return UserService(db)


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    service: UserService = Depends(get_user_service),
):
    """Login with email and password, return access and refresh tokens."""
    user = await service.authenticate_user(
        user_credentials.email, user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(data={"sub": user.email})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.email})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh-token", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    access_token = AuthService.refresh_access_token(refresh_token)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Generate new refresh token as well for security
    # Extract email from old refresh token
    from app.services.auth_service import AuthService

    token_data = AuthService.verify_token(refresh_token, "refresh")
    if not token_data or not token_data.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    new_refresh_token = AuthService.create_refresh_token(data={"sub": token_data.email})

    return Token(access_token=access_token, refresh_token=new_refresh_token)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    service: UserService = Depends(get_user_service),
):
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials

    token_data = AuthService.verify_token(token, "access")
    if token_data is None:
        raise credentials_exception

    user = await service.get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception

    return user
