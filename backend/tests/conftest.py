from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from incidentops_lab_api.core.base import Base
from incidentops_lab_api.core.config import get_settings
from incidentops_lab_api.core.database import get_db
from incidentops_lab_api.core.security import create_access_token, hash_password
from incidentops_lab_api.main import app
from incidentops_lab_api.models import Cart, CartItem, Incident, Product, User
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    settings = get_settings()

    engine = create_async_engine(
        settings.test_database_url,
        pool_pre_ping=True,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session_factory(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_test_database(test_engine):
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clean_database(test_session_factory):
    async with test_session_factory() as session:
        await session.execute(delete(CartItem))
        await session.execute(delete(Cart))
        await session.execute(delete(Product))
        await session.execute(delete(Incident))
        await session.execute(delete(User))
        await session.commit()


@pytest.fixture
def client(test_session_factory):
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            yield session

    original_overrides = app.dependency_overrides.copy()
    original_factory = getattr(app.state, "test_session_factory", None)

    app.dependency_overrides[get_db] = override_get_db
    app.state.test_session_factory = test_session_factory

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides = original_overrides

        if original_factory is None:
            delattr(app.state, "test_session_factory")
        else:
            app.state.test_session_factory = original_factory


@pytest.fixture
def admin_token(client):
    async def create_admin():
        async with app.state.test_session_factory() as session:
            admin = User(
                email="admin@example.com",
                full_name="Test Admin",
                password_hash=hash_password("AdminPassword123!"),
                role="admin",
            )

            session.add(admin)
            await session.commit()
            await session.refresh(admin)

            return create_access_token(admin.id)

    return lambda: client.portal.call(create_admin)
