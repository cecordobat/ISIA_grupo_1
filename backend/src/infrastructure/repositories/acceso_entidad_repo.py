"""
Repositorio: accesos de entidades contratantes a perfiles de contratistas.
Ref: RF-11, HU-12
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.acceso_entidad_contratante import AccesoEntidadContratante


class AccesoEntidadRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def autorizar(self, entidad_usuario_id: str, perfil_id: str) -> AccesoEntidadContratante:
        """Crea un acceso activo para una entidad contratante a un perfil."""
        acceso = AccesoEntidadContratante(
            entidad_usuario_id=entidad_usuario_id,
            perfil_id=perfil_id,
            activo=True,
        )
        self._db.add(acceso)
        await self._db.flush()
        return acceso

    async def revocar(self, entidad_usuario_id: str, perfil_id: str) -> None:
        """Desactiva el acceso. Solo el contratista dueño del perfil puede revocar."""
        result = await self._db.execute(
            select(AccesoEntidadContratante).where(
                AccesoEntidadContratante.entidad_usuario_id == entidad_usuario_id,
                AccesoEntidadContratante.perfil_id == perfil_id,
                AccesoEntidadContratante.activo.is_(True),
            )
        )
        acceso = result.scalar_one_or_none()
        if acceso is not None:
            acceso.activo = False
            await self._db.flush()

    async def tiene_acceso(self, entidad_usuario_id: str, perfil_id: str) -> bool:
        result = await self._db.execute(
            select(AccesoEntidadContratante).where(
                AccesoEntidadContratante.entidad_usuario_id == entidad_usuario_id,
                AccesoEntidadContratante.perfil_id == perfil_id,
                AccesoEntidadContratante.activo.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None
