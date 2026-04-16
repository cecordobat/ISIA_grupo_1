from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.liquidacion_revision import LiquidacionRevision


class LiquidacionRevisionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_por_liquidacion(self, liquidacion_id: str) -> LiquidacionRevision | None:
        result = await self._db.execute(
            select(LiquidacionRevision).where(LiquidacionRevision.liquidacion_id == liquidacion_id)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        liquidacion_id: str,
        contador_id: str,
        nota: str,
        aprobada: bool,
    ) -> LiquidacionRevision:
        revision = await self.get_por_liquidacion(liquidacion_id)
        if revision is None:
            revision = LiquidacionRevision(
                liquidacion_id=liquidacion_id,
                contador_id=contador_id,
                nota=nota,
                aprobada=aprobada,
            )
            self._db.add(revision)
        else:
            revision.contador_id = contador_id
            revision.nota = nota
            revision.aprobada = aprobada
        await self._db.flush()
        return revision
