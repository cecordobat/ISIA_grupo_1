"""
Cálculo del IBC Consolidado.

Implementa:
  RN-01: Regla del 40% con topes [1 SMMLV, 25 SMMLV]
  RN-02: Costos presuntos por CIIU (Resolución DIAN 209/2020)
  RN-04: Acumulación de múltiples contratos
  RN-05: Proporcionalidad por días cotizados
  RN-08: Nivel ARL máximo entre contratos

REGLA ABSOLUTA (INV-01): Solo Decimal con ROUND_HALF_UP.
REGLA ABSOLUTA (INV-02): Sin efectos secundarios, sin BD, sin APIs.
Ref: context/business_rules.md RN-01..RN-05, RN-08
"""
from decimal import ROUND_HALF_UP, Decimal

from src.engine.dtos import (
    ContratoCalculado,
    ContratoInput,
    IBCResult,
    ParametrosNormativosDTO,
    PeriodoLiquidacion,
)
from src.domain.enums import NivelARL

_CERO = Decimal("0")
_CUARENTA_PCT = Decimal("0.40")
_DOS_DECIMALES = Decimal("0.01")
_CUATRO_DECIMALES = Decimal("0.0001")


def calcular_dias_cotizados(contrato: ContratoInput, periodo: PeriodoLiquidacion) -> int:
    """
    Calcula los días que el contrato estuvo activo dentro del período.
    Ref: RN-05 — proporcionalidad por días.

    El mes se normaliza a 30 días para efectos del cálculo (práctica UGPP).
    Si el contrato cubre todo el mes, retorna 30.
    """
    inicio_efectivo = max(contrato.fecha_inicio, periodo.fecha_inicio_mes)
    fin_efectivo = min(contrato.fecha_fin, periodo.fecha_fin_mes)

    if fin_efectivo < inicio_efectivo:
        return 0

    dias = (fin_efectivo - inicio_efectivo).days + 1
    # Normalizar: si cubre todo el mes calendario, son 30 días UGPP
    if (contrato.fecha_inicio <= periodo.fecha_inicio_mes
            and contrato.fecha_fin >= periodo.fecha_fin_mes):
        return 30

    return min(dias, 30)


def _proporcionar_ingreso(
    valor_bruto_mensual: Decimal, dias_cotizados: int
) -> Decimal:
    """
    Aplica proporcionalidad: IBC_proporcional = IBC_mensual × (días / 30)
    Ref: RN-05, Art. 5 Decreto 1990/2016.
    Precisión intermedia: 4 decimales.
    """
    if dias_cotizados == 30:
        return valor_bruto_mensual.quantize(_CUATRO_DECIMALES, rounding=ROUND_HALF_UP)

    factor = Decimal(str(dias_cotizados)) / Decimal("30")
    return (valor_bruto_mensual * factor).quantize(_CUATRO_DECIMALES, rounding=ROUND_HALF_UP)


def _nivel_arl_maximo(contratos: list[ContratoInput]) -> NivelARL:
    """
    Determina el nivel ARL más alto entre todos los contratos activos.
    Ref: RN-08, Decreto 1295/1994 Art. 26.
    """
    orden = {NivelARL.I: 1, NivelARL.II: 2, NivelARL.III: 3, NivelARL.IV: 4, NivelARL.V: 5}
    return max(contratos, key=lambda c: orden[c.nivel_arl]).nivel_arl


def calcular_ibc_consolidado(
    contratos: list[ContratoInput],
    parametros: ParametrosNormativosDTO,
    periodo: PeriodoLiquidacion,
) -> IBCResult:
    """
    Calcula el IBC consolidado para el período.

    Flujo:
      1. Calcular ingreso proporcional por contrato (RN-05)
      2. Sumar todos los ingresos (RN-04)
      3. Aplicar costos presuntos CIIU (RN-02)
      4. Aplicar regla del 40% (RN-01)
      5. Topar a [1 SMMLV, 25 SMMLV] (RN-01, RES-N01)
      6. Determinar nivel ARL máximo (RN-08)

    Args:
        contratos: Lista de contratos con fechas activas en el período.
                   CT-04 ya debe haber filtrado los que no aplican.
        parametros: SnapshotNormativo del período (incluye pct_costos_presuntos CIIU).
        periodo: Período mensual de liquidación.

    Returns:
        IBCResult con el IBC final y el detalle del cálculo.
    """
    if not contratos:
        raise ValueError("No hay contratos activos para el período.")

    # Paso 1 y 2: proporcionalidad y acumulación (RN-04, RN-05)
    contratos_calculados: list[ContratoCalculado] = []
    ingreso_bruto_total = _CERO

    for contrato in contratos:
        dias = calcular_dias_cotizados(contrato, periodo)
        ingreso_proporcional = _proporcionar_ingreso(contrato.valor_bruto_mensual, dias)
        contratos_calculados.append(
            ContratoCalculado(
                contrato_id=contrato.id,
                dias_cotizados=dias,
                ingreso_bruto_proporcional=ingreso_proporcional,
            )
        )
        ingreso_bruto_total += ingreso_proporcional

    ingreso_bruto_total = ingreso_bruto_total.quantize(
        _CUATRO_DECIMALES, rounding=ROUND_HALF_UP
    )

    # Paso 3: costos presuntos por CIIU (RN-02)
    costos_presuntos = (ingreso_bruto_total * parametros.pct_costos_presuntos).quantize(
        _CUATRO_DECIMALES, rounding=ROUND_HALF_UP
    )

    # Paso 4: base del 40% (RN-01)
    base_neta = ingreso_bruto_total - costos_presuntos
    base_40_pct = (base_neta * _CUARENTA_PCT).quantize(
        _CUATRO_DECIMALES, rounding=ROUND_HALF_UP
    )

    # Paso 5: topes [1 SMMLV, 25 SMMLV] (RN-01, RES-N01)
    tope_inferior = parametros.smmlv
    tope_superior = (parametros.smmlv * 25).quantize(_CUATRO_DECIMALES, rounding=ROUND_HALF_UP)

    ibc_raw = base_40_pct
    ibc_clamped = max(tope_inferior, min(tope_superior, ibc_raw))
    ibc_final = ibc_clamped.quantize(_CUATRO_DECIMALES, rounding=ROUND_HALF_UP)
    ajustado = ibc_raw != ibc_final

    # Paso 6: nivel ARL máximo (RN-08)
    nivel_arl_max = _nivel_arl_maximo(contratos)

    return IBCResult(
        ingreso_bruto_total=ingreso_bruto_total,
        costos_presuntos=costos_presuntos,
        base_40_pct=base_40_pct,
        ibc=ibc_final,
        ajustado_por_tope=ajustado,
        nivel_arl_maximo=nivel_arl_max,
        contratos_calculados=tuple(contratos_calculados),
    )
