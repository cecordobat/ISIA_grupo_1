"""
Tests unitarios: verificación de cumplimiento por entidad contratante.
Ref: RF-11, HU-12, RNF-06
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.domain.enums import RolUsuario


def test_rol_entidad_contratante_existe():
    assert RolUsuario.ENTIDAD_CONTRATANTE == "ENTIDAD_CONTRATANTE"


def test_acceso_entidad_contratante_tiene_campos():
    from src.infrastructure.models.acceso_entidad_contratante import AccesoEntidadContratante
    columnas = {c.name for c in AccesoEntidadContratante.__table__.columns}
    assert "id" in columnas
    assert "entidad_usuario_id" in columnas
    assert "perfil_id" in columnas
    assert "autorizado_en" in columnas
    assert "activo" in columnas


@pytest.mark.asyncio
async def test_crear_acceso():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    from src.infrastructure.repositories.acceso_entidad_repo import AccesoEntidadRepository
    repo = AccesoEntidadRepository(db)
    acceso = await repo.autorizar(entidad_usuario_id="ent-1", perfil_id="perf-1")

    db.add.assert_called_once()
    assert acceso.entidad_usuario_id == "ent-1"
    assert acceso.perfil_id == "perf-1"
    assert acceso.activo is True


@pytest.mark.asyncio
async def test_tiene_acceso_retorna_false_si_no_existe():
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))

    from src.infrastructure.repositories.acceso_entidad_repo import AccesoEntidadRepository
    repo = AccesoEntidadRepository(db)
    result = await repo.tiene_acceso(entidad_usuario_id="ent-99", perfil_id="perf-99")
    assert result is False
