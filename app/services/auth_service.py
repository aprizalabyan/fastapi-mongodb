from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import secrets
from passlib.context import CryptContext
from jose import JWTError, jwt, ExpiredSignatureError

from app.core.config import Settings
from app.schemas.auth import TokenData

settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthError(Exception):
    """Base authentication error."""

    pass


class TokenExpiredError(AuthError):
    """Token has expired."""

    pass


class TokenInvalidError(AuthError):
    """Token is invalid."""

    pass


class TokenGenerationError(AuthError):
    """Error occurred while generating token."""

    pass


class RefreshTokenNotFoundError(AuthError):
    """Refresh token not found in database."""

    pass


class RefreshTokenExpiredError(AuthError):
    """Refresh token has expired."""

    pass


class AuthService:
    """Authentication service for password hashing and JWT tokens."""

    collection_name = "refresh_tokens"

    def __init__(self, db):
        """Initialize service with database instance."""
        self.db = db

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password for storing."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.access_token_expire_minutes
                )
            to_encode.update({"exp": expire, "type": "access"})
            encoded_jwt = jwt.encode(
                to_encode, settings.secret_key, algorithm=settings.algorithm
            )
            return encoded_jwt
        except Exception as e:
            raise TokenGenerationError(f"Failed to generate access token: {str(e)}")

    async def create_refresh_token(
        self, user_id: str, expires_at: Optional[datetime] = None
    ) -> str:
        """Create random refresh token and store in DB."""
        try:
            token = secrets.token_urlsafe(32)
            if expires_at is None:
                expire = datetime.now(timezone.utc) + timedelta(
                    days=settings.refresh_token_expire_days
                )
            else:
                expire = expires_at

            now = datetime.now(timezone.utc)
            data = {
                "token": token,
                "user_id": user_id,
                "expires_at": expire,
                "created_at": now,
                "revoked_at": None,
            }

            result = await self.db[self.collection_name].insert_one(data)
            if not result.acknowledged:
                raise TokenGenerationError("Failed to save refresh token to database")
            return token
        except Exception as e:
            raise TokenGenerationError(f"Failed to generate refresh token: {str(e)}")

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> TokenData:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token, key=settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            token_type_in_payload: str = payload.get("type")
            if user_id is None or token_type_in_payload != token_type:
                raise TokenInvalidError("Token payload is invalid")
            return TokenData(id=user_id)
        except ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except JWTError as e:
            raise TokenInvalidError(f"Token is invalid: {str(e)}")
        except Exception as e:
            raise TokenInvalidError(
                f"Unexpected error during token verification: {str(e)}"
            )

    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """Create new access token and refresh token from refresh token."""
        try:
            # Find refresh token in DB
            doc = await self.db[self.collection_name].find_one(
                {"token": refresh_token, "revoked_at": None}
            )
            if not doc:
                raise RefreshTokenNotFoundError("Refresh token not found")

            now = datetime.now(timezone.utc)
            # Check if token has expired
            if doc["expires_at"] <= now.replace(tzinfo=None):
                # Revoke expired token
                await self.db[self.collection_name].update_one(
                    {"token": refresh_token}, {"$set": {"revoked_at": now}}
                )
                raise RefreshTokenExpiredError("Refresh token has expired")

            user_id = doc["user_id"]

            # Revoke old refresh token
            update_result = await self.db[self.collection_name].update_one(
                {"token": refresh_token}, {"$set": {"revoked_at": now}}
            )
            if update_result.modified_count == 0:
                raise TokenGenerationError("Failed to delete old refresh token")

            # Create new access token
            access_token = self.create_access_token(data={"sub": user_id})

            # Create new refresh token with same expiration as old one
            new_refresh_token = await self.create_refresh_token(
                user_id, doc["expires_at"]
            )

            return access_token, new_refresh_token

        except (
            RefreshTokenNotFoundError,
            RefreshTokenExpiredError,
            TokenGenerationError,
        ):
            # Re-raise specific auth errors
            raise
        except Exception as e:
            raise TokenGenerationError(
                f"Unexpected error during token refresh: {str(e)}"
            )

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a specific refresh token."""
        try:
            now = datetime.now(timezone.utc)
            result = await self.db[self.collection_name].update_one(
                {"token": refresh_token, "revoked_at": None},
                {"$set": {"revoked_at": now}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise TokenGenerationError(f"Failed to revoke refresh token: {str(e)}")

    async def revoke_all_user_refresh_tokens(self, user_id: str) -> int:
        """Revoke all active refresh tokens for a user."""
        try:
            now = datetime.now(timezone.utc)
            result = await self.db[self.collection_name].update_many(
                {"user_id": user_id, "revoked_at": None},
                {"$set": {"revoked_at": now}}
            )
            return result.modified_count
        except Exception as e:
            raise TokenGenerationError(f"Failed to revoke user refresh tokens: {str(e)}")
