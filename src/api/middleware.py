from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.db import db


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        await db.start_session()
        try:
            response = await call_next(request)
            return response
        except Exception:
            await db.session.rollback()
            raise
        finally:
            await db.close_session()
