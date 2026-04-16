from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.liquidacion_confirmacion import LiquidacionConfirmacion


class LiquidacionConfirmacionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_por_liquidacion(self, liquidacion_id: str) -> LiquidacionConfirmacion | None:
        result = await self._db.execute(
            select(LiquidacionConfirmacion).where(
                LiquidacionConfirmacion.liquidacion_id == liquidacion_id
            )
        )
        return result.scalar_one_or_none()

    async def confirmar(self, liquidacion_id: str, usuario_id: str) -> LiquidacionConfirmacion:
        confirmacion = await self.get_por_liquidacion(liquidacion_id)
        if confirmacion is None:
            confirmacion = LiquidacionConfirmacion(
                liquidacion_id=liquidacion_id,
                usuario_id=usuario_id,
            )
            self._db.add(confirmacion)
            await self._db.flush()
        return confirmacion
