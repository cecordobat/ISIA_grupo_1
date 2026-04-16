"""
DTOs del motor de cálculo.
Contrato de interfaz entre el engine puro y toda la infraestructura.

REGLA ABSOLUTA (INV-02): Este módulo solo importa stdlib Python.
Ningún DTO puede importar SQLAlchemy, FastAPI ni Pydantic.
Ref: context/invariantes.md INV-01, INV-02
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from src.domain.enums import NivelARL, OpcionPisoProteccion


@dataclass(frozen=True)
class ContratoInput:
    """
    Datos de un contrato para el período de liquidación.
    Ref: context/data_model.md Contrato, RN-04, RN-05, RN-08
    """
    id: str
    entidad_contratante: str
    valor_bruto_mensual: Decimal
    nivel_arl: NivelARL
    fecha_inicio: date
    fecha_fin: date


@dataclass(frozen=True)
class TramoRetencion:
    """Un tramo de la tabla Art. 383 E.T. en UVT. Ref: RN-07."""
    uvt_desde: Decimal
    uvt_hasta: Decimal | None   # None = último tramo (sin techo)
    tarifa_marginal: Decimal
    uvt_deduccion: Decimal


@dataclass(frozen=True)
class ParametrosNormativosDTO:
    """
    Snapshot normativo para un período de liquidación.
    Todos los valores vienen de la BD — nunca hardcodeados.
    Ref: context/invariantes.md INV-04, context/data_model.md SnapshotNormativo

    IMPORTANTE: Este DTO es frozen. El engine no puede mutar parámetros normativos.
    """
    smmlv: Decimal
    uvt: Decimal
    pct_salud: Decimal          # 0.1250
    pct_pension: Decimal        # 0.1600
    pct_costos_presuntos: Decimal  # según CIIU del contratista
    tarifas_arl: dict[NivelARL, Decimal]  # {I: 0.00522, II: 0.01044, ...}
    tramos_retencion_383: tuple[TramoRetencion, ...]
    vigencia_anio: int


@dataclass(frozen=True)
class PeriodoLiquidacion:
    """
    Período mensual de liquidación.
    El engine recibe el período como input explícito — nunca llama datetime.now().
    Ref: context/invariantes.md INV-02
    """
    anio: int
    mes: int   # 1..12

    @property
    def codigo(self) -> str:
        return f"{self.anio:04d}-{self.mes:02d}"

    @property
    def dias_en_mes(self) -> int:
        return calendar.monthrange(self.anio, self.mes)[1]

    @property
    def fecha_inicio_mes(self) -> date:
        return date(self.anio, self.mes, 1)

    @property
    def fecha_fin_mes(self) -> date:
        return date(self.anio, self.mes, self.dias_en_mes)


@dataclass(frozen=True)
class ContratoCalculado:
    """Resultado del cálculo de proporcionalidad de un contrato individual."""
    contrato_id: str
    dias_cotizados: int
    ingreso_bruto_proporcional: Decimal


@dataclass(frozen=True)
class IBCResult:
    """Resultado del cálculo del IBC consolidado. Ref: RN-01..RN-05."""
    ingreso_bruto_total: Decimal
    costos_presuntos: Decimal
    base_40_pct: Decimal            # (ingreso - costos) × 0.40, antes de topes
    ibc: Decimal                    # clamped a [1 SMMLV, 25 SMMLV]
    ajustado_por_tope: bool         # True si se aplicó tope inferior o superior
    nivel_arl_maximo: NivelARL
    contratos_calculados: tuple[ContratoCalculado, ...]


@dataclass(frozen=True)
class AportesResult:
    """Resultado de la liquidación de aportes SGSSI. Ref: RN-03, RN-08."""
    aporte_salud: Decimal
    aporte_pension: Decimal
    aporte_arl: Decimal
    nivel_arl_aplicado: NivelARL
    tarifa_arl_aplicada: Decimal

    @property
    def total_aportes(self) -> Decimal:
        return self.aporte_salud + self.aporte_pension + self.aporte_arl


@dataclass(frozen=True)
class RetencionResult:
    """Resultado del cálculo de retención en la fuente. Ref: RN-07, Art. 383 E.T."""
    base_gravable: Decimal          # ingreso_bruto − salud − pensión
    retencion_fuente: Decimal       # 0 si no supera el umbral mínimo
    aplica_retencion: bool


@dataclass(frozen=True)
class LiquidacionResult:
    """
    Resultado completo de una liquidación mensual.
    Este DTO es el output del engine y el input del servicio de persistencia.
    Ref: context/invariantes.md INV-05
    """
    periodo: PeriodoLiquidacion
    ibc_result: IBCResult
    opcion_piso_proteccion: OpcionPisoProteccion
    aportes_result: AportesResult
    retencion_result: RetencionResult

    # Campos derivados para conveniencia
    @property
    def ingreso_bruto_total(self) -> Decimal:
        return self.ibc_result.ingreso_bruto_total

    @property
    def ibc(self) -> Decimal:
        return self.ibc_result.ibc

    @property
    def aporte_salud(self) -> Decimal:
        return self.aportes_result.aporte_salud

    @property
    def aporte_pension(self) -> Decimal:
        return self.aportes_result.aporte_pension

    @property
    def aporte_arl(self) -> Decimal:
        return self.aportes_result.aporte_arl

    @property
    def total_aportes(self) -> Decimal:
        return self.aportes_result.total_aportes

    @property
    def retencion_fuente(self) -> Decimal:
        return self.retencion_result.retencion_fuente

    @property
    def neto_estimado(self) -> Decimal:
        return self.ingreso_bruto_total - self.total_aportes - self.retencion_fuente
