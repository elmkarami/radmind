from contextvars import ContextVar
from typing import Optional

from src.db.models.user import User

# Context variable to store current authenticated user
current_user_context: ContextVar[Optional[User]] = ContextVar(
    "current_user", default=None
)


def get_current_user() -> Optional[User]:
    """Get current authenticated user from context"""
    return current_user_context.get()


def set_current_user(user: Optional[User]) -> None:
    """Set current authenticated user in context"""
    current_user_context.set(user)


class AuthenticationError(Exception):
    """Raised when authentication fails"""

    pass


class PasswordChangeRequiredError(Exception):
    """Raised when user must change password before accessing other operations"""

    pass
