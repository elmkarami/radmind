from unittest.mock import Mock, patch
from urllib.parse import urlparse

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.api.app import app
from src.api.middleware import SessionMiddleware
from src.config.settings import settings
from src.db import db
from src.db.models.base import Base
from tests.factories.base import BaseFactory


def run_test_migrations(test_db_uri):
    alembic_cfg = Config("src/db/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_uri)
    alembic_cfg.set_main_option("script_location", "src/db/alembic")

    command.upgrade(alembic_cfg, "head")


def create_test_database():
    """Create test database and return its URI"""
    parsed_uri = urlparse(settings.SQLALCHEMY_DATABASE_URI)
    test_db_name = "test_db"

    # Server URI for creating/dropping database
    server_uri = f"{parsed_uri.scheme.replace('+asyncpg', '')}://{parsed_uri.username}:{parsed_uri.password}@{parsed_uri.hostname}:{parsed_uri.port}/postgres"
    admin_engine = create_engine(server_uri, isolation_level="AUTOCOMMIT")

    # Drop and create test database
    with admin_engine.connect() as conn:
        # Terminate existing connections to test database
        conn.execute(
            text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{test_db_name}'
              AND pid <> pg_backend_pid();
        """)
        )

        # Drop if exists and create new
        conn.execute(text(f'DROP DATABASE IF EXISTS "{test_db_name}"'))
        conn.execute(text(f'CREATE DATABASE "{test_db_name}"'))

    admin_engine.dispose()

    # Test database URI
    test_db_uri = f"{parsed_uri.scheme}://{parsed_uri.username}:{parsed_uri.password}@{parsed_uri.hostname}:{parsed_uri.port}/{test_db_name}"

    # Create tables in test database
    sync_test_uri = test_db_uri.replace("postgresql+asyncpg://", "postgresql://")
    test_engine = create_engine(sync_test_uri)
    Base.metadata.create_all(test_engine)
    test_engine.dispose()

    return test_db_uri


def drop_test_database():
    """Drop the test database"""
    parsed_uri = urlparse(settings.SQLALCHEMY_DATABASE_URI)
    test_db_name = "test_db"

    # Server URI for dropping database
    server_uri = f"{parsed_uri.scheme.replace('+asyncpg', '')}://{parsed_uri.username}:{parsed_uri.password}@{parsed_uri.hostname}:{parsed_uri.port}/postgres"
    admin_engine = create_engine(server_uri, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as conn:
        # Terminate existing connections to test database
        conn.execute(
            text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{test_db_name}'
              AND pid <> pg_backend_pid();
        """)
        )

        # Drop test database
        conn.execute(text(f'DROP DATABASE IF EXISTS "{test_db_name}"'))

    admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database before all tests and cleanup after"""
    test_db_uri = create_test_database()

    yield test_db_uri

    # Cleanup: drop test database after all tests
    drop_test_database()


@pytest.fixture(scope="session")
def test_app():
    middleware = [m for m in app.user_middleware if m.cls is not SessionMiddleware]
    app.user_middleware = middleware
    return app


@pytest_asyncio.fixture(autouse=True, scope="function")
async def db_session(setup_test_database):
    test_db_uri = setup_test_database

    engine = create_async_engine(test_db_uri)

    # Use connection-level transaction management
    connection = await engine.connect()
    transaction = await connection.begin()

    session_factory = sessionmaker(
        bind=connection, class_=AsyncSession, expire_on_commit=False
    )

    session = session_factory()
    BaseFactory.patch_session(session)

    # Set the session in context variable for the test
    await db.start_session(session)

    patcher = patch("src.db.sessionmaker", Mock(return_value=session))
    patcher.start()

    try:
        yield session
    finally:
        # Always rollback the connection-level transaction
        await transaction.rollback()
        await connection.close()
        await engine.dispose()
        patcher.stop()


@pytest.fixture
def patch_session():
    # The session is already set in the context variable by db_session fixture
    yield


@pytest_asyncio.fixture
async def test_client(test_app):
    """Create an async HTTP client for testing"""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        yield client
