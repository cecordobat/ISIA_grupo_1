"""
Repositorio de parámetros normativos.
Obtiene SnapshotNormativo, CIIU y tabla Art. 383 con vigencia temporal.
Ref: context/invariantes.md INV-04, RES-D01, RES-D02, RES-D03
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import NivelARL
from src.engine.dtos import ParametrosNormativosDTO, TramoRetencion
from src.infrastructure.models.snapshot_normativo import SnapshotNormativo
from src.infrastructure.models.tabla_ciiu import TablaParametroCIIU
from src.infrastructure.models.tabla_retencion_383 import TablaRetencion383
import json


class ParametrosRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_snapshot_por_anio(self, anio: int) -> SnapshotNormativo | None:
        """Retorna el snapshot normativo vigente para el año indicado."""
        result = await self._db.execute(
            select(SnapshotNormativo).where(SnapshotNormativo.vigencia_anio == anio)
        )
        return result.scalar_one_or_none()

    async def get_ciiu(self, codigo: str) -> TablaParametroCIIU | None:
        """Retorna los datos CIIU para el código indicado."""
        result = await self._db.execute(
            select(TablaParametroCIIU).where(TablaParametroCIIU.codigo_ciiu == codigo)
        )
        return result.scalar_one_or_none()

    async def get_tramos_retencion(self, fecha_referencia: date) -> list[TablaRetencion383]:
        """Retorna los tramos Art. 383 vigentes a la fecha de referencia."""
        result = await self._db.execute(
            select(TablaRetencion383)
            .where(TablaRetencion383.vigente_desde <= fecha_referencia)
            .order_by(TablaRetencion383.vigente_desde.desc(), TablaRetencion383.uvt_desde)
        )
        return list(result.scalars().all())

    async def construir_parametros_dto(
        self, anio: int, ciiu_codigo: str, fecha_referencia: date
    ) -> ParametrosNormativosDTO:
        """
        Ensambla el ParametrosNormativosDTO completo para el período.
        Este es el único punto donde la infraestructura alimenta al engine.
        """
        snapshot = await self.get_snapshot_por_anio(anio)
        if snapshot is None:
            raise ValueError(f"No existe snapshot normativo para el año {anio}.")

        ciiu = await self.get_ciiu(ciiu_codigo)
        if ciiu is None:
            raise ValueError(f"Código CIIU {ciiu_codigo} no encontrado en la tabla DIAN 209/2020.")

        tramos_orm = await self.get_tramos_retencion(fecha_referencia)
        if not tramos_orm:
            raise ValueError("No hay tramos de retención Art. 383 vigentes.")

        # Convertir tabla ARL del JSON guardado como string
        tabla_arl_raw: dict[str, str] = json.loads(snapshot.tabla_arl_json)
        tarifas_arl = {NivelARL(k): Decimal(v) for k, v in tabla_arl_raw.items()}

        # Convertir tramos ORM a DTOs del engine
        tramos_dto = tuple(
            TramoRetencion(
                uvt_desde=Decimal(str(t.uvt_desde)),
                uvt_hasta=Decimal(str(t.uvt_hasta)) if t.uvt_hasta is not None else None,
                tarifa_marginal=Decimal(str(t.tarifa_marginal)),
                uvt_deduccion=Decimal(str(t.uvt_deduccion)),
            )
            for t in tramos_orm
        )

        return ParametrosNormativosDTO(
            smmlv=Decimal(str(snapshot.smmlv)),
            uvt=Decimal(str(snapshot.uvt)),
            pct_salud=Decimal(str(snapshot.pct_salud)),
            pct_pension=Decimal(str(snapshot.pct_pension)),
            pct_costos_presuntos=Decimal(str(ciiu.pct_costos_presuntos)),
            tarifas_arl=tarifas_arl,
            tramos_retencion_383=tramos_dto,
            vigencia_anio=snapshot.vigencia_anio,
        )
