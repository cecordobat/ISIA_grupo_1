"""Repositorio del perfil del contratista."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.perfil_contratista import PerfilContratista


class PerfilRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_por_id(self, perfil_id: str) -> PerfilContratista | None:
        result = await self._db.execute(
            select(PerfilContratista).where(PerfilContratista.id == perfil_id)
        )
        return result.scalar_one_or_none()

    async def get_por_usuario(self, usuario_id: str) -> PerfilContratista | None:
        result = await self._db.execute(
            select(PerfilContratista).where(PerfilContratista.usuario_id == usuario_id)
        )
        return result.scalar_one_or_none()

    async def crear(self, usuario_id: str, **kwargs: object) -> PerfilContratista:
        perfil = PerfilContratista(usuario_id=usuario_id, **kwargs)
        self._db.add(perfil)
        await self._db.flush()
        return perfil
