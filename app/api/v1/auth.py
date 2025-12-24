from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from app.schemas.auth import UserLogin, Token
from app.schemas.user import UserRead
from app.services.user_service import UserService
from app.services.auth_service import (
    AuthService,
    TokenExpiredError,
    TokenInvalidError,
    TokenGenerationError,
    RefreshTokenNotFoundError,
    RefreshTokenExpiredError,
)
from app.api.deps import get_db

router = APIRouter()
security_scheme = HTTPBearer()


async def get_user_service(db=Depends(get_db)):
    """Dependency to inject database into UserService."""
    return UserService(db)


async def get_auth_service(db=Depends(get_db)):
    """Dependency to inject database into AuthService."""
    return AuthService(db)


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login with email and password, return access and refresh tokens."""
    user = await user_service.authenticate_user(
        user_credentials.email, user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        access_token = auth_service.create_access_token(data={"sub": str(user.id)})
        refresh_token = await auth_service.create_refresh_token(str(user.id))
        return Token(access_token=access_token, refresh_token=refresh_token)
    except TokenGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authentication tokens: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during login: {str(e)}"
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh access token using refresh token."""
    try:
        result = await auth_service.refresh_access_token(refresh_token)
        access_token, new_refresh_token = result
        return Token(access_token=access_token, refresh_token=new_refresh_token)
    except RefreshTokenNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except RefreshTokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate new tokens: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during token refresh: {str(e)}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    user_service: UserService = Depends(get_user_service),
):
    """Dependency to get current authenticated user."""
    try:
        token = credentials.credentials
        token_data = AuthService.verify_token(token, "access")
        
        # Get user from database
        user = await user_service.get_user(token_data.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user  # Return UserRead instead of UserCurrent
        
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Access token is invalid: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserRead)
async def get_me(current_user: UserRead = Depends(get_current_user)):
    """Get current user details."""
    return current_user
