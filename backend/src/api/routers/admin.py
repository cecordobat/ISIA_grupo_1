"""
Router de administración de parámetros normativos.
Solo accesible para rol ADMIN.
Ref: RF-10, HU-11, INV-04, RNF-03
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import require_admin
from src.api.schemas.admin import (
    CIIUCreate,
    CIIUResponse,
    SnapshotNormativoCreate,
    SnapshotNormativoResponse,
    TramoRetencionCreate,
    TramoRetencionResponse,
)
from src.infrastructure.database import get_db
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.parametros_repo import ParametrosRepository

router = APIRouter(prefix="/admin/parametros", tags=["administración"])


@router.get("/snapshots", response_model=list[SnapshotNormativoResponse])
async def listar_snapshots(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[SnapshotNormativoResponse]:
    repo = ParametrosRepository(db)
    snapshots = await repo.listar_snapshots()
    return [SnapshotNormativoResponse.model_validate(s) for s in snapshots]


@router.post("/snapshots", response_model=SnapshotNormativoResponse, status_code=status.HTTP_201_CREATED)
async def crear_snapshot(
    body: SnapshotNormativoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> SnapshotNormativoResponse:
    repo = ParametrosRepository(db)
    try:
        snapshot = await repo.crear_snapshot(
            smmlv=body.smmlv,
            uvt=body.uvt,
            pct_salud=body.pct_salud,
            pct_pension=body.pct_pension,
            tabla_arl_json=body.tabla_arl_json,
            vigencia_anio=body.vigencia_anio,
        )
        await db.commit()
        return SnapshotNormativoResponse.model_validate(snapshot)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/ciiu", response_model=list[CIIUResponse])
async def listar_ciiu(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[CIIUResponse]:
    repo = ParametrosRepository(db)
    return [CIIUResponse.model_validate(c) for c in await repo.listar_ciiu()]


@router.post("/ciiu", response_model=CIIUResponse, status_code=status.HTTP_201_CREATED)
async def crear_ciiu(
    body: CIIUCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> CIIUResponse:
    repo = ParametrosRepository(db)
    ciiu = await repo.crear_ciiu(
        codigo_ciiu=body.codigo_ciiu,
        descripcion=body.descripcion,
        pct_costos_presuntos=body.pct_costos_presuntos,
        vigente_desde=body.vigente_desde,
    )
    await db.commit()
    return CIIUResponse.model_validate(ciiu)


@router.get("/retencion", response_model=list[TramoRetencionResponse])
async def listar_tramos_retencion(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[TramoRetencionResponse]:
    repo = ParametrosRepository(db)
    return [TramoRetencionResponse.model_validate(t) for t in await repo.listar_tramos_retencion_todos()]


@router.post("/retencion", response_model=TramoRetencionResponse, status_code=status.HTTP_201_CREATED)
async def crear_tramo_retencion(
    body: TramoRetencionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> TramoRetencionResponse:
    repo = ParametrosRepository(db)
    tramo = await repo.crear_tramo_retencion(
        uvt_desde=body.uvt_desde,
        uvt_hasta=body.uvt_hasta,
        tarifa_marginal=body.tarifa_marginal,
        uvt_deduccion=body.uvt_deduccion,
        vigente_desde=body.vigente_desde,
    )
    await db.commit()
    return TramoRetencionResponse.model_validate(tramo)
