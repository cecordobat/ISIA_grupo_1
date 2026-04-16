"""
Servicio de Liquidación — único punto de orquestación entre infraestructura y engine.

Responsabilidades:
  1. Carga parámetros normativos desde la BD
  2. Traduce contratos ORM → ContratoInput DTOs
  3. Llama al engine puro (función pura, sin efectos secundarios)
  4. Persiste el resultado inmutable en BD
  5. Retorna el LiquidacionResult para la capa API

Ref: context/invariantes.md INV-02 (engine puro), INV-05 (orden)
"""
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import NivelARL, OpcionPisoProteccion
from src.domain.exceptions import AccesoNoAutorizadoError, ContratistaNoEncontradoError
from src.engine.dtos import (
    ContratoInput,
    LiquidacionResult,
    ParametrosNormativosDTO,
    PeriodoLiquidacion,
)
from src.engine.liquidacion_engine import calcular
from src.infrastructure.models.liquidacion_periodo import LiquidacionPeriodo
from src.infrastructure.repositories.contrato_repo import ContratoRepository
from src.infrastructure.repositories.liquidacion_repo import LiquidacionRepository
from src.infrastructure.repositories.parametros_repo import ParametrosRepository
from src.infrastructure.repositories.perfil_repo import PerfilRepository


@dataclass(frozen=True)
class LiquidacionEjecutada:
    resultado: LiquidacionResult
    liquidacion: LiquidacionPeriodo
    parametros: ParametrosNormativosDTO
    contratos: list[ContratoInput]


class LiquidacionService:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._perfil_repo = PerfilRepository(db)
        self._contrato_repo = ContratoRepository(db)
        self._parametros_repo = ParametrosRepository(db)
        self._liquidacion_repo = LiquidacionRepository(db)

    async def ejecutar_liquidacion(
        self,
        perfil_id: str,
        usuario_id: str,
        anio: int,
        mes: int,
        opcion_piso: OpcionPisoProteccion | None = None,
    ) -> LiquidacionEjecutada:
        """
        Orquesta el flujo completo de liquidación para un período.

        Args:
            perfil_id: ID del perfil del contratista.
            usuario_id: ID del usuario autenticado (para verificar ownership).
            anio: Año del período de liquidación.
            mes: Mes del período de liquidación (1..12).
            opcion_piso: Decisión del usuario para el Piso de Protección Social.

        Returns:
            LiquidacionResult del engine puro.
        """
        # 1. Verificar que el perfil existe y pertenece al usuario
        perfil = await self._perfil_repo.get_por_id(perfil_id)
        if perfil is None:
            raise ContratistaNoEncontradoError(perfil_id)
        if perfil.usuario_id != usuario_id:
            raise AccesoNoAutorizadoError()

        # 2. Cargar parámetros normativos (snapshot + CIIU + tabla 383)
        periodo = PeriodoLiquidacion(anio=anio, mes=mes)
        parametros = await self._parametros_repo.construir_parametros_dto(
            anio=anio,
            ciiu_codigo=perfil.ciiu_codigo,
            fecha_referencia=date(anio, mes, 1),
        )

        # 3. Cargar contratos y traducir a DTOs del engine
        contratos_orm = await self._contrato_repo.listar_por_perfil(perfil_id)
        contratos_input = [
            ContratoInput(
                id=c.id,
                entidad_contratante=c.entidad_contratante,
                valor_bruto_mensual=Decimal(str(c.valor_bruto_mensual)),
                nivel_arl=NivelARL(c.nivel_arl.value if hasattr(c.nivel_arl, 'value') else c.nivel_arl),
                fecha_inicio=c.fecha_inicio,
                fecha_fin=c.fecha_fin if c.fecha_fin is not None else (
                    date(anio + (mes // 12), mes % 12 + 1, 1) - timedelta(days=1)
                ),
            )
            for c in contratos_orm
        ]

        # 4. Llamar al engine puro (función pura — INV-02)
        resultado = calcular(
            contratos=contratos_input,
            parametros=parametros,
            periodo=periodo,
            opcion_piso=opcion_piso,
        )

        # 5. Persistir resultado inmutable (APPEND-ONLY — INV-03)
        snapshot = await self._parametros_repo.get_snapshot_por_anio(anio)
        liquidacion = await self._liquidacion_repo.crear(
            resultado=resultado,
            perfil_id=perfil_id,
            snapshot_id=snapshot.id,  # type: ignore[union-attr]
        )
        await self._db.commit()

        return LiquidacionEjecutada(
            resultado=resultado,
            liquidacion=liquidacion,
            parametros=parametros,
            contratos=contratos_input,
        )

    async def obtener_historial(
        self, perfil_id: str, usuario_id: str
    ) -> list["LiquidacionPeriodo"]:
        """Retorna el historial de liquidaciones del contratista."""
        perfil = await self._perfil_repo.get_por_id(perfil_id)
        if perfil is None:
            raise ContratistaNoEncontradoError(perfil_id)
        if perfil.usuario_id != usuario_id:
            raise AccesoNoAutorizadoError()

        return await self._liquidacion_repo.listar_por_perfil(perfil_id)
