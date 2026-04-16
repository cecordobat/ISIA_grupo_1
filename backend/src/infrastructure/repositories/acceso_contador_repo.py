from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.models.acceso_contador_perfil import AccesoContadorPerfil
from src.infrastructure.models.perfil_contratista import PerfilContratista


class AccesoContadorRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def existe(self, contador_id: str, perfil_id: str) -> bool:
        result = await self._db.execute(
            select(AccesoContadorPerfil).where(
                AccesoContadorPerfil.contador_id == contador_id,
                AccesoContadorPerfil.perfil_id == perfil_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def crear(self, contador_id: str, perfil_id: str) -> AccesoContadorPerfil:
        acceso = AccesoContadorPerfil(contador_id=contador_id, perfil_id=perfil_id)
        self._db.add(acceso)
        await self._db.flush()
        return acceso

    async def contador_tiene_acceso(self, contador_id: str, perfil_id: str) -> bool:
        return await self.existe(contador_id, perfil_id)

    async def listar_perfiles_por_contador(self, contador_id: str) -> list[PerfilContratista]:
        result = await self._db.execute(
            select(PerfilContratista)
            .join(AccesoContadorPerfil, AccesoContadorPerfil.perfil_id == PerfilContratista.id)
            .where(AccesoContadorPerfil.contador_id == contador_id)
            .options(selectinload(PerfilContratista.usuario))
            .order_by(PerfilContratista.nombre_completo)
        )
        return list(result.scalars().all())

    async def contar_por_perfil(self, perfil_id: str) -> int:
        result = await self._db.execute(
            select(AccesoContadorPerfil).where(AccesoContadorPerfil.perfil_id == perfil_id)
        )
        return len(list(result.scalars().all()))
