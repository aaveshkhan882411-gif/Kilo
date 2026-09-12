import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import asyncio

from app.main import app
from app.database import get_db, Base
from app.models.organization import Organization
from app.models.user import User
from app.auth.utils import hash_password

TEST_DATABASE_URL = "postgresql+asyncpg://growthai:password@localhost:5432/growthai_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


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


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def test_org(db: AsyncSession = Depends(override_get_db)):
    org = Organization(name="Test Org", slug="test-org", plan="standard")
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@pytest.fixture
async def test_user(db: AsyncSession = Depends(override_get_db), test_org: Organization = Depends()):
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
def auth_headers(test_user: User):
    from app.auth.utils import create_access_token
    token = create_access_token(data={"sub": test_user.id, "org_id": test_user.org_id})
    return {"Authorization": f"Bearer {token}"}
