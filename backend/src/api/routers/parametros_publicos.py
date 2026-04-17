"""
Router público de parámetros de referencia: CIIU, EPS, AFP.
Accesible por cualquier usuario autenticado.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.infrastructure.database import get_db
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.parametros_repo import ParametrosRepository

router = APIRouter(prefix="/parametros", tags=["parámetros"])


class CIIUItem(BaseModel):
    codigo: str
    descripcion: str
    pct_costos_presuntos: str


@router.get("/ciiu", response_model=list[CIIUItem])
async def listar_ciiu(
    _: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CIIUItem]:
    items = await ParametrosRepository(db).listar_ciiu()
    return [
        CIIUItem(
            codigo=c.codigo_ciiu,
            descripcion=c.descripcion,
            pct_costos_presuntos=str(c.pct_costos_presuntos),
        )
        for c in items
    ]
