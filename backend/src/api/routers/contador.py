from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.dependencies import get_current_user
from src.domain.enums import RolUsuario
from src.infrastructure.database import get_db
from src.infrastructure.models.liquidacion_periodo import LiquidacionPeriodo
from src.infrastructure.models.perfil_contratista import PerfilContratista
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.acceso_contador_repo import AccesoContadorRepository
from src.infrastructure.repositories.liquidacion_revision_repo import LiquidacionRevisionRepository
from src.infrastructure.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/contador", tags=["contador"])


class VincularContadorRequest(BaseModel):
    perfil_id: str
    contador_email: EmailStr


class ClienteContadorResponse(BaseModel):
    perfil_id: str
    nombre_contratista: str
    numero_documento: str
    ciiu_codigo: str
    contratista_email: str


class RevisionContadorRequest(BaseModel):
    liquidacion_id: str
    nota: str
    aprobada: bool = True


@router.post("/vinculos", status_code=status.HTTP_201_CREATED)
async def vincular_contador(
    body: VincularContadorRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    perfil = await db.scalar(
        select(PerfilContratista).where(
            PerfilContratista.id == body.perfil_id,
            PerfilContratista.usuario_id == current_user.id,
        )
    )
    if perfil is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado o no pertenece al usuario autenticado.",
        )

    usuario_repo = UsuarioRepository(db)
    contador = await usuario_repo.get_por_email(body.contador_email)
    if contador is None or contador.rol != RolUsuario.CONTADOR:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No existe un contador registrado con ese email.",
        )

    acceso_repo = AccesoContadorRepository(db)
    if not await acceso_repo.existe(contador.id, perfil.id):
        await acceso_repo.crear(contador.id, perfil.id)
        await db.commit()

    return {"message": "Contador vinculado correctamente."}


@router.get("/clientes", response_model=list[ClienteContadorResponse])
async def listar_clientes(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ClienteContadorResponse]:
    if current_user.rol != RolUsuario.CONTADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta vista esta disponible solo para usuarios contador.",
        )

    repo = AccesoContadorRepository(db)
    perfiles = await repo.listar_perfiles_por_contador(current_user.id)
    return [
        ClienteContadorResponse(
            perfil_id=perfil.id,
            nombre_contratista=perfil.nombre_completo,
            numero_documento=perfil.numero_documento,
            ciiu_codigo=perfil.ciiu_codigo,
            contratista_email=perfil.usuario.email,
        )
        for perfil in perfiles
    ]


@router.post("/revisiones", status_code=status.HTTP_201_CREATED)
async def revisar_liquidacion(
    body: RevisionContadorRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if current_user.rol != RolUsuario.CONTADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un contador puede registrar revisiones.",
        )

    liquidacion = await db.scalar(
        select(LiquidacionPeriodo).where(LiquidacionPeriodo.id == body.liquidacion_id)
    )
    if liquidacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Liquidacion no encontrada.",
        )

    acceso_repo = AccesoContadorRepository(db)
    if not await acceso_repo.contador_tiene_acceso(current_user.id, liquidacion.perfil_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a esta liquidacion.",
        )

    revision_repo = LiquidacionRevisionRepository(db)
    await revision_repo.upsert(
        liquidacion_id=body.liquidacion_id,
        contador_id=current_user.id,
        nota=body.nota,
        aprobada=body.aprobada,
    )
    await db.commit()
    return {"message": "Revision registrada correctamente."}
