"""
FastAPI app factory — Motor de Cumplimiento Colombia.
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar todos los modelos ORM para que Base.metadata registre cada tabla
# antes de que lifespan llame a create_all. Sin estos imports las tablas
# no se crean aunque el engine esté configurado.
import src.infrastructure.models.acceso_contador_perfil  # noqa: F401
import src.infrastructure.models.acceso_entidad_contratante  # noqa: F401
import src.infrastructure.models.contrato  # noqa: F401
import src.infrastructure.models.liquidacion_confirmacion  # noqa: F401
import src.infrastructure.models.liquidacion_periodo  # noqa: F401
import src.infrastructure.models.liquidacion_revision  # noqa: F401
import src.infrastructure.models.perfil_contratista  # noqa: F401
import src.infrastructure.models.snapshot_normativo  # noqa: F401
import src.infrastructure.models.tabla_ciiu  # noqa: F401
import src.infrastructure.models.tabla_retencion_383  # noqa: F401
import src.infrastructure.models.usuario  # noqa: F401
import src.infrastructure.models.usuario_mfa  # noqa: F401
from src.api.routers import auth, contador, contratos, liquidaciones, perfiles
from src.config import get_settings
from src.infrastructure.bootstrap import seed_reference_data
from src.infrastructure.database import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Crea las tablas al iniciar (dev). En prod usar Alembic."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_reference_data(engine)
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
    app.include_router(contador.router)
    app.include_router(liquidaciones.router)
    app.include_router(perfiles.router)
    app.include_router(contratos.router)
    from src.api.routers import admin
    app.include_router(admin.router)
    from src.api.routers import entidad_contratante
    app.include_router(entidad_contratante.router)
    from src.api.routers import parametros_publicos
    app.include_router(parametros_publicos.router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.app_version}

    return app


app = create_app()
