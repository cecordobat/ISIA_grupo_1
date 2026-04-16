"""
Fixtures de integración — cliente HTTP sobre SQLite en memoria.

Cada test recibe un AsyncClient fresco con su propia base de datos
en memoria (scope="function"), garantizando aislamiento total.
"""
from datetime import date

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.main import app
from src.infrastructure.database import Base, get_db
from src.infrastructure.models.tabla_ciiu import TablaParametroCIIU

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def async_client():
    """
    Levanta un AsyncClient con la app FastAPI apuntando a SQLite en memoria.
    Sobreescribe la dependencia get_db para usar la BD de test.
    """
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            insert(TablaParametroCIIU),
            [
                {
                    "codigo_ciiu": "6201",
                    "descripcion": "Actividades de desarrollo de sistemas informaticos",
                    "pct_costos_presuntos": 0.27,
                    "vigente_desde": date(2025, 1, 1),
                },
                {
                    "codigo_ciiu": "9001",
                    "descripcion": "Actividades artisticas con costo presunto alto",
                    "pct_costos_presuntos": 0.65,
                    "vigente_desde": date(2025, 1, 1),
                },
            ],
        )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
