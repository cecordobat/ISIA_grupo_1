"""
FastAPI app factory — Motor de Cumplimiento Colombia.
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import auth, contratos, liquidaciones, perfiles
from src.config import get_settings
from src.infrastructure.database import Base, engine

# Importar todos los modelos ORM para que Base.metadata registre cada tabla
# antes de que lifespan llame a create_all. Sin estos imports las tablas
# no se crean aunque el engine esté configurado.
from src.infrastructure.models import (  # noqa: F401
    contrato,
    liquidacion_periodo,
    perfil_contratista,
    snapshot_normativo,
    tabla_ciiu,
    tabla_retencion_383,
    usuario,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Crea las tablas al iniciar (dev). En prod usar Alembic."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Motor de Cumplimiento Tributario y Seguridad Social "
            "para Contratistas Independientes — Colombia. "
            "⚠️ Herramienta de asistencia. No reemplaza asesoría contable certificada."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(liquidaciones.router)
    app.include_router(perfiles.router)
    app.include_router(contratos.router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.app_version}

    return app


app = create_app()
