from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_async_session
from app.main import app
from app.models import Role, User
from app.utils.auth import generate_jwt_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)
AsyncTestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncTestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database() -> None:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncTestSessionLocal() as session:
        roles = [Role(id=1, name="admin"), Role(id=2, name="editor")]
        session.add_all(roles)
        await session.commit()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncTestSessionLocal() as session:
        roles = [Role(id=1, name="admin"), Role(id=2, name="editor"), Role(id=3, name="user")]
        session.add_all(roles)
        await session.commit()
    yield


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncTestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def editor_user(db_session: AsyncSession) -> User:
    user = User(username="editor1", password_hash="hashed", role_id=2)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(username="admin1", password_hash="hashed", role_id=1)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def authenticated_editor_client(editor_user: User) -> AsyncGenerator[AsyncClient, None]:
    token = generate_jwt_token({"sub": str(editor_user.id)})
    app.dependency_overrides[get_async_session] = override_get_async_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authenticated_admin_client(admin_user: User) -> AsyncGenerator[AsyncClient, None]:
    token = generate_jwt_token({"sub": str(admin_user.id)})
    app.dependency_overrides[get_async_session] = override_get_async_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_to_delete(db_session: AsyncSession) -> User:
    user = User(username="to_delete", password_hash="hash", role_id=2)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def form_data() -> AsyncMock:
    form = AsyncMock()
    form.username = "testuser"
    form.password = "secret"
    return form


@pytest.fixture
def mock_db_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_user() -> User:
    return User(id=1, username="testuser", password_hash="$2b$12$example", role_id=2)
