"""
Router de contratos — gestión de contratos de prestación de servicios.
POST   /contratos/              → crear contrato
GET    /contratos/?perfil_id=   → listar contratos por perfil
DELETE /contratos/{id}          → eliminar contrato
Ref: context/functional_requirements.md RF-02, INV-01
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.api.schemas.contratos import ContratoCreate, ContratoResponse
from src.infrastructure.database import get_db
from src.infrastructure.models.contrato import Contrato
from src.infrastructure.models.perfil_contratista import PerfilContratista
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.contrato_repo import ContratoRepository
from src.infrastructure.repositories.perfil_repo import PerfilRepository

router = APIRouter(prefix="/contratos", tags=["contratos"])


async def _verificar_propiedad_perfil(
    perfil_id: str,
    usuario_id: str,
    db: AsyncSession,
) -> None:
    """Lanza HTTP 403 si el perfil no existe o no pertenece al usuario."""
    perfil_repo = PerfilRepository(db)
    perfil = await perfil_repo.get_por_id(perfil_id)
    if perfil is None or perfil.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: el perfil no pertenece al usuario autenticado.",
        )


@router.post("/", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED)
async def crear_contrato(
    body: ContratoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContratoResponse:
    """
    Crea un contrato de prestación de servicios.
    Verifica que el perfil pertenezca al usuario autenticado (HTTP 403 si no).
    """
    await _verificar_propiedad_perfil(body.perfil_id, current_user.id, db)

    repo = ContratoRepository(db)
    contrato = await repo.crear(
        perfil_id=body.perfil_id,
        entidad_contratante=body.entidad_contratante,
        valor_bruto_mensual=body.valor_bruto_mensual,
        nivel_arl=body.nivel_arl,
        fecha_inicio=body.fecha_inicio,
        fecha_fin=body.fecha_fin,
    )
    await db.commit()
    await db.refresh(contrato)
    return ContratoResponse.model_validate(contrato)


@router.get("/", response_model=list[ContratoResponse])
async def listar_contratos(
    perfil_id: str = Query(..., description="ID del perfil cuyo contratos se listan"),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ContratoResponse]:
    """
    Lista todos los contratos activos de un perfil.
    Verifica que el perfil pertenezca al usuario autenticado (HTTP 403 si no).
    """
    await _verificar_propiedad_perfil(perfil_id, current_user.id, db)

    repo = ContratoRepository(db)
    contratos = await repo.listar_por_perfil(perfil_id)
    return [ContratoResponse.model_validate(c) for c in contratos]


@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_contrato(
    contrato_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Elimina (hard delete) un contrato.
    Verifica que el contrato exista y pertenezca a un perfil del usuario (HTTP 403 si no).
    """
    result = await db.execute(
        select(Contrato)
        .join(PerfilContratista, Contrato.perfil_id == PerfilContratista.id)
        .where(
            Contrato.id == contrato_id,
            PerfilContratista.usuario_id == current_user.id,
        )
    )
    contrato = result.scalar_one_or_none()
    if contrato is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: el contrato no existe o no pertenece al usuario autenticado.",
        )

    await db.delete(contrato)
    await db.commit()
