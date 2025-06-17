from datetime import datetime, timedelta, timezone

import jwt

from src.services.user_service import UserService
from src.utils.auth import hash_password, verify_password


class AuthService:
    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"

    @staticmethod
    def authenticate_user(email: str, password: str):
        user = UserService.get_user_by_email(email)
        if user and verify_password(password, user.password):
            return user
        return None

    @staticmethod
    def create_access_token(user_id: int, expires_delta: timedelta = None):
        if expires_delta is None:
            expires_delta = timedelta(hours=24)

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"sub": str(user_id), "exp": expire}
        return jwt.encode(
            to_encode, AuthService.SECRET_KEY, algorithm=AuthService.ALGORITHM
        )

    @staticmethod
    def verify_token(token: str):
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
