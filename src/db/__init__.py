import os
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI")

# Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


_session_context: ContextVar[AsyncSession] = ContextVar("session")


class DatabaseSession:
    @property
    def session(self) -> AsyncSession:
        return _session_context.get()

    async def start_session(self, session: AsyncSession | None = None):
        session = session or async_session_factory()
        _session_context.set(session)
        return session

    def remove_session(self):
        _session_context.set(None)

    async def close_session(self):
        session = _session_context.get(None)
        if session:
            await session.close()


db = DatabaseSession()
