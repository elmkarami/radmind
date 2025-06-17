from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

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

session = scoped_session(async_session_factory)


_session_context: ContextVar[AsyncSession] = ContextVar("session")


class DatabaseSession:
    @property
    def session(self) -> AsyncSession:
        return _session_context.get()

    async def start_session(self):
        session = async_session_factory()
        _session_context.set(session)
        return session

    async def close_session(self):
        session = _session_context.get(None)
        if session:
            await session.close()


db = DatabaseSession()
