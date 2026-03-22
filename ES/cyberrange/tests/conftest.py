# Extraído de: LibroCyberrange/interludio-testing-cyber-range.md
# tests/conftest.py — Fixtures compartidas para todo el proyecto de tests

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


@pytest.fixture(scope="session")
def event_loop():
    """Bucle de eventos compartido para toda la sesión de tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Motor de base de datos para tests — MySQL dedicado."""
    engine = create_async_engine(
        "mysql+asyncmy://test:test@localhost:3307/cyberrange_test",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """Sesión de base de datos aislada por test."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Cliente HTTP asíncrono con dependencia de BD inyectada."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def proxmox_config():
    """Configuración de Proxmox para tests de integración."""
    return {
        "host": "proxmox-test.internal",
        "port": 8006,
        "user": "test@pam",
        "password": "test_password",
        "verify_ssl": False,
        "test_node": "pve-test",
        "test_storage": "local-lvm",
    }
