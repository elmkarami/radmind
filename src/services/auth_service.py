from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from src.db.dao import user_dao
from src.db.models.user import User
from src.utils.exceptions import AuthenticationError


class AuthService:
    SECRET_KEY = (
        "your-secret-key-change-in-production"  # TODO: Move to environment variable
    )
    ALGORITHM = "HS256"

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await user_dao.get_user_by_email(email)
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    async def login(email: str, password: str) -> dict:
        """Login user and return JWT token with user info"""
        user = await AuthService.authenticate_user(email, password)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Create access token
        access_token = AuthService.create_access_token(user.id)

        return {
            "token": access_token,
            "user": user,
            "must_change_password": user.password_must_change,
        }

    @staticmethod
    def create_access_token(user_id: int, expires_delta: timedelta = None) -> str:
        """Create JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"sub": str(user_id), "exp": expire}
        return jwt.encode(
            to_encode, AuthService.SECRET_KEY, algorithm=AuthService.ALGORITHM
        )

    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """Verify JWT token and return user ID"""
        try:
            payload = jwt.decode(
                token, AuthService.SECRET_KEY, algorithms=[AuthService.ALGORITHM]
            )
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except jwt.PyJWTError:
            return None

    @staticmethod
    async def get_current_user(token: str) -> Optional[User]:
        """Get current user from JWT token"""
        user_id = AuthService.verify_token(token)
        if user_id is None:
            return None
        return await user_dao.get_user_by_id(user_id)

    @staticmethod
    async def change_password(
        user_id: int, current_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        user = await user_dao.get_user_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        # Verify current password
        if not user.check_password(current_password):
            raise AuthenticationError("Current password is incorrect")

        # Set new password
        user.set_password(new_password)

        # Clear password change requirement and temp password
        await user_dao.update_user_password_fields(
            user_id, password_must_change=False, temp_password=None
        )

        return True
