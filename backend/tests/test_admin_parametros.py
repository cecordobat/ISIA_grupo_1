"""
Tests de administración de parámetros normativos.
Ref: RF-10, HU-11, RNF-03, INV-04
"""
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock

from src.api.dependencies import require_admin
from src.domain.enums import RolUsuario


@pytest.mark.asyncio
async def test_require_admin_permite_admin():
    usuario = MagicMock()
    usuario.rol = RolUsuario.ADMIN
    result = await require_admin(current_user=usuario)
    assert result is usuario


@pytest.mark.asyncio
async def test_require_admin_rechaza_contratista():
    usuario = MagicMock()
    usuario.rol = RolUsuario.CONTRATISTA
    with pytest.raises(HTTPException) as exc:
        await require_admin(current_user=usuario)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_admin_rechaza_contador():
    usuario = MagicMock()
    usuario.rol = RolUsuario.CONTADOR
    with pytest.raises(HTTPException) as exc:
        await require_admin(current_user=usuario)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_crear_snapshot_normativo():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))

    from src.infrastructure.repositories.parametros_repo import ParametrosRepository
    repo = ParametrosRepository(db)
    snapshot = await repo.crear_snapshot(
        smmlv=1300000.00,
        uvt=47065.00,
        pct_salud=0.125,
        pct_pension=0.16,
        tabla_arl_json='{"I":"0.00522","II":"0.01044","III":"0.02436","IV":"0.04350","V":"0.06960"}',
        vigencia_anio=2026,
    )

    db.add.assert_called_once()
    assert snapshot.vigencia_anio == 2026


@pytest.mark.asyncio
async def test_crear_ciiu():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    from datetime import date

    from src.infrastructure.repositories.parametros_repo import ParametrosRepository
    repo = ParametrosRepository(db)
    ciiu = await repo.crear_ciiu(
        codigo_ciiu="7010",
        descripcion="Actividades de consultoría de gestión",
        pct_costos_presuntos=0.27,
        vigente_desde=date(2026, 1, 1),
    )

    db.add.assert_called_once()
    assert ciiu.codigo_ciiu == "7010"


@pytest.mark.asyncio
async def test_crear_tramo_retencion():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    from datetime import date

    from src.infrastructure.repositories.parametros_repo import ParametrosRepository
    repo = ParametrosRepository(db)
    tramo = await repo.crear_tramo_retencion(
        uvt_desde=0,
        uvt_hasta=87,
        tarifa_marginal=0.0,
        uvt_deduccion=0.0,
        vigente_desde=date(2026, 1, 1),
    )

    db.add.assert_called_once()
    assert tramo.uvt_desde == 0
