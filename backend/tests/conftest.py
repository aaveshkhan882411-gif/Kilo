import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.middleware.rate_limit import _client

from app.database import get_db, Base

TEST_DATABASE_URL = "postgresql+asyncpg://growthai:password@localhost:5432/growthai_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestingSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db

# Disable Redis-backed rate limiting during tests to avoid cross-event-loop Redis clients.
for _middleware in list(app.user_middleware):
    if _middleware.cls.__name__ == "RateLimitMiddleware":
        app.user_middleware.remove(_middleware)
app.middleware_stack = app.build_middleware_stack()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    return TestClient(app)


@pytest_asyncio.fixture
async def db():
    async with TestingSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def test_org(db: AsyncSession):
    from app.models.organization import Organization

    org = Organization(
        name="Test Org",
        slug="test-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@pytest_asyncio.fixture
async def test_user(db: AsyncSession, test_org):
    from app.models.user import User
    from app.auth.utils import hash_password

    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
        role="admin",
        org_id=test_org.id,
        is_verified=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    from app.auth.utils import create_access_token

    token = create_access_token(
        data={
            "sub": test_user.id,
            "org_id": test_user.org_id,
        }
    )
    return {"Authorization": f"Bearer {token}"}
