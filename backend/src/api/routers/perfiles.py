"""
Router de perfiles — gestión del perfil del contratista independiente.
POST /perfiles/        → crear perfil
GET  /perfiles/        → listar perfiles del usuario autenticado
GET  /perfiles/{id}    → obtener un perfil por ID
Ref: context/functional_requirements.md RF-01
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.api.schemas.perfiles import PerfilCreate, PerfilResponse
from src.infrastructure.database import get_db
from src.infrastructure.models.perfil_contratista import PerfilContratista
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.perfil_repo import PerfilRepository

router = APIRouter(prefix="/perfiles", tags=["perfiles"])


@router.post("/", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
async def crear_perfil(
    body: PerfilCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerfilResponse:
    """Crea un nuevo perfil de contratista vinculado al usuario autenticado."""
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
    return PerfilResponse.model_validate(perfil)


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
    return [PerfilResponse.model_validate(p) for p in perfiles]


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
    return PerfilResponse.model_validate(perfil)
