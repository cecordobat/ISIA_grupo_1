"""Repositorio de contratos del contratista."""
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import EstadoContrato
from src.infrastructure.models.contrato import Contrato


class ContratoRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def listar_por_perfil(self, perfil_id: str) -> list[Contrato]:
        result = await self._db.execute(
            select(Contrato)
            .where(Contrato.perfil_id == perfil_id, Contrato.estado == EstadoContrato.ACTIVO)
            .order_by(Contrato.fecha_inicio.desc())
        )
        return list(result.scalars().all())

    async def crear(self, perfil_id: str, **kwargs: object) -> Contrato:
        contrato = Contrato(perfil_id=perfil_id, **kwargs)
        self._db.add(contrato)
        await self._db.flush()
        return contrato

    async def get_por_id(self, contrato_id: str, perfil_id: str) -> Contrato | None:
        result = await self._db.execute(
            select(Contrato).where(
                Contrato.id == contrato_id,
                Contrato.perfil_id == perfil_id,
            )
        )
        return result.scalar_one_or_none()
