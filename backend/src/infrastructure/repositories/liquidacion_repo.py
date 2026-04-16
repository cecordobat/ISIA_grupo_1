"""
Repositorio de liquidaciones — APPEND-ONLY.

INVARIANTE (INV-03): No existe update() ni delete(). Solo create() y lecturas.
Ref: context/invariantes.md INV-03, RES-C03
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import LiquidacionDuplicadaError, LiquidacionInmutableError
from src.engine.dtos import LiquidacionResult
from src.infrastructure.models.liquidacion_periodo import LiquidacionPeriodo


class LiquidacionRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def existe_para_periodo(self, perfil_id: str, periodo: str) -> bool:
        """Verifica si ya existe una liquidación para el mismo período."""
        result = await self._db.execute(
            select(LiquidacionPeriodo).where(
                LiquidacionPeriodo.perfil_id == perfil_id,
                LiquidacionPeriodo.periodo == periodo,
            )
        )
        return result.scalar_one_or_none() is not None

    async def crear(
        self,
        resultado: LiquidacionResult,
        perfil_id: str,
        snapshot_id: str,
    ) -> LiquidacionPeriodo:
        """
        Inserta una nueva liquidación. APPEND-ONLY.
        Lanza LiquidacionDuplicadaError si ya existe para ese período.
        """
        periodo_codigo = resultado.periodo.codigo
        if await self.existe_para_periodo(perfil_id, periodo_codigo):
            raise LiquidacionDuplicadaError(perfil_id, periodo_codigo)

        liquidacion = LiquidacionPeriodo(
            perfil_id=perfil_id,
            snapshot_id=snapshot_id,
            periodo=periodo_codigo,
            ingreso_bruto_total=float(resultado.ingreso_bruto_total),
            costos_presuntos=float(resultado.ibc_result.costos_presuntos),
            ibc=float(resultado.ibc),
            aporte_salud=float(resultado.aporte_salud),
            aporte_pension=float(resultado.aporte_pension),
            aporte_arl=float(resultado.aporte_arl),
            nivel_arl_aplicado=resultado.aportes_result.nivel_arl_aplicado,
            base_gravable_retencion=float(resultado.retencion_result.base_gravable),
            retencion_fuente=float(resultado.retencion_fuente),
            opcion_piso_proteccion=resultado.opcion_piso_proteccion,
        )
        self._db.add(liquidacion)
        await self._db.flush()
        return liquidacion

    async def get_por_id(self, liquidacion_id: str) -> LiquidacionPeriodo | None:
        result = await self._db.execute(
            select(LiquidacionPeriodo).where(LiquidacionPeriodo.id == liquidacion_id)
        )
        return result.scalar_one_or_none()

    async def listar_por_perfil(self, perfil_id: str) -> list[LiquidacionPeriodo]:
        result = await self._db.execute(
            select(LiquidacionPeriodo)
            .where(LiquidacionPeriodo.perfil_id == perfil_id)
            .order_by(LiquidacionPeriodo.periodo.desc())
        )
        return list(result.scalars().all())

    # ── NUNCA agregar update() ni delete() aquí (INV-03) ──────────────────────
