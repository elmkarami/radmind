from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.auth_context import set_current_user
from src.services.auth_service import AuthService


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to extract JWT token and set current user context"""

    async def dispatch(self, request: Request, call_next):
        # Reset user context for each request
        set_current_user(None)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            try:
                # Get user from token
                user = await AuthService.get_current_user(token)
                if user:
                    set_current_user(user)
            except Exception:
                # Invalid token - user remains None
                pass

        # Process the request
        response = await call_next(request)
        return response
