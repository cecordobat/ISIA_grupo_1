"""
Router de perfiles — gestión del perfil del contratista independiente.
POST /perfiles/        → crear perfil
GET  /perfiles/        → listar perfiles del usuario autenticado
GET  /perfiles/{id}    → obtener un perfil por ID
Ref: context/functional_requirements.md RF-01
"""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.api.schemas.perfiles import PerfilCreate, PerfilResponse, PerfilUpdate
from src.infrastructure.database import get_db
from src.infrastructure.models.perfil_contratista import PerfilContratista
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.parametros_repo import ParametrosRepository
from src.infrastructure.repositories.perfil_repo import PerfilRepository

router = APIRouter(prefix="/perfiles", tags=["perfiles"])


async def _perfil_response(
    perfil: PerfilContratista,
    db: AsyncSession,
) -> PerfilResponse:
    parametros_repo = ParametrosRepository(db)
    ciiu = await parametros_repo.get_ciiu(perfil.ciiu_codigo)
    return PerfilResponse(
        id=perfil.id,
        usuario_id=perfil.usuario_id,
        tipo_documento=perfil.tipo_documento,
        numero_documento=perfil.numero_documento,
        nombre_completo=perfil.nombre_completo,
        eps=perfil.eps,
        afp=perfil.afp,
        ciiu_codigo=perfil.ciiu_codigo,
        pct_costos_presuntos=ciiu.pct_costos_presuntos if ciiu is not None else None,
        estado=perfil.estado,
        created_at=perfil.created_at,
    )


@router.post("/", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
async def crear_perfil(
    body: PerfilCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerfilResponse:
    """Crea un nuevo perfil de contratista vinculado al usuario autenticado."""
    parametros_repo = ParametrosRepository(db)
    ciiu = await parametros_repo.get_ciiu(body.ciiu_codigo)
    if ciiu is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Codigo CIIU no encontrado.", "ct_code": "RF-01-CIIU"},
        )

    if Decimal(str(ciiu.pct_costos_presuntos)) > Decimal("0.60") and not body.confirmar_ciiu_alto:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "El CIIU seleccionado tiene costos presuntos superiores al 60%. Debe confirmar expresamente que corresponde a su actividad.",
                "requires_ciiu_confirmation": True,
                "pct_costos_presuntos": str(ciiu.pct_costos_presuntos),
            },
        )

    repo = PerfilRepository(db)
    perfil = await repo.crear(
        usuario_id=current_user.id,
        tipo_documento=body.tipo_documento,
        numero_documento=body.numero_documento,
        nombre_completo=body.nombre_completo,
        eps=body.eps,
        afp=body.afp,
        ciiu_codigo=body.ciiu_codigo,
    )
    await db.commit()
    await db.refresh(perfil)
    return await _perfil_response(perfil, db)


@router.put("/{perfil_id}", response_model=PerfilResponse)
async def actualizar_perfil(
    perfil_id: str,
    body: PerfilUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerfilResponse:
    parametros_repo = ParametrosRepository(db)
    ciiu = await parametros_repo.get_ciiu(body.ciiu_codigo)
    if ciiu is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Codigo CIIU no encontrado.", "ct_code": "RF-01-CIIU"},
        )

    if Decimal(str(ciiu.pct_costos_presuntos)) > Decimal("0.60") and not body.confirmar_ciiu_alto:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "El CIIU seleccionado tiene costos presuntos superiores al 60%. Debe confirmar expresamente que corresponde a su actividad.",
                "requires_ciiu_confirmation": True,
                "pct_costos_presuntos": str(ciiu.pct_costos_presuntos),
            },
        )

    repo = PerfilRepository(db)
    perfil = await repo.get_por_id(perfil_id)
    if perfil is None or perfil.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado.",
        )

    await repo.actualizar(
        perfil,
        tipo_documento=body.tipo_documento,
        numero_documento=body.numero_documento,
        nombre_completo=body.nombre_completo,
        eps=body.eps,
        afp=body.afp,
        ciiu_codigo=body.ciiu_codigo,
    )
    await db.commit()
    await db.refresh(perfil)
    return await _perfil_response(perfil, db)


@router.get("/", response_model=list[PerfilResponse])
async def listar_perfiles(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PerfilResponse]:
    """Lista todos los perfiles que pertenecen al usuario autenticado."""
    result = await db.execute(
        select(PerfilContratista).where(
            PerfilContratista.usuario_id == current_user.id
        )
    )
    perfiles = list(result.scalars().all())
    return [await _perfil_response(p, db) for p in perfiles]


@router.get("/{perfil_id}", response_model=PerfilResponse)
async def obtener_perfil(
    perfil_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerfilResponse:
    """Retorna un perfil por ID. HTTP 404 si no existe o no pertenece al usuario."""
    repo = PerfilRepository(db)
    perfil = await repo.get_por_id(perfil_id)
    if perfil is None or perfil.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado.",
        )
    return await _perfil_response(perfil, db)
