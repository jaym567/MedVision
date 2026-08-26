"""
Pytest Configuration and Fixtures

Provides reusable test fixtures for database, client, etc.
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database.session import Base, get_db
from app.core.config import settings


# Test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    settings.DATABASE_URL.split("/")[-1],
    "medvision_test_db"
)


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def db_session(test_db) -> AsyncSession:
    """Alias for test_db fixture."""
    return test_db


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> dict:
    """Create a test user and return dictionary with user object and JWT token."""
    from app.models.user import User
    from app.core.security import hash_password, create_access_token

    user = User(
        email="test_user@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Test User",
        role="radiologist",
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    return {
        "user": user,
        "token": token,
        "email": user.email,
        "id": user.id,
    }


@pytest_asyncio.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()