"""
Validaciones de Consistencia Transversal (CT-01 a CT-04).

Estas validaciones son PRE-CONDICIONES BLOQUEANTES.
Si alguna falla, la liquidación queda en estado ERROR y no puede confirmarse.

Ref: context/invariantes.md INV-06, context/functional_requirements.md CT-01..CT-04
"""
from decimal import Decimal

from src.domain.exceptions import (
    ErrorCT01_IBCFueraDeRango,
    ErrorCT02_SumaAportesInconsistente,
    ErrorCT03_BaseGravableIncorrecta,
)
from src.engine.dtos import (
    AportesResult,
    ContratoInput,
    IBCResult,
    ParametrosNormativosDTO,
    PeriodoLiquidacion,
    RetencionResult,
)

_TOLERANCIA_CT02 = Decimal("1.00")
_CERO = Decimal("0.00")


def validar_ct01_ibc_rango(
    ibc_result: IBCResult, parametros: ParametrosNormativosDTO
) -> None:
    """
    CT-01: El IBC debe estar en el rango [1 SMMLV, 25 SMMLV].

    Ref: RES-N01 — Art. 18 Ley 100/1993, Art. 244 Ley 1955/2019.
    Raises: ErrorCT01_IBCFueraDeRango si el IBC está fuera del rango.
    """
    tope_inferior = parametros.smmlv
    tope_superior = parametros.smmlv * 25

    if not (tope_inferior <= ibc_result.ibc <= tope_superior):
        raise ErrorCT01_IBCFueraDeRango(ibc=ibc_result.ibc, smmlv=parametros.smmlv)


def validar_ct02_suma_aportes(
    aportes_result: AportesResult,
    ibc_result: IBCResult,
    parametros: ParametrosNormativosDTO,
) -> None:
    """
    CT-02: |Σ(Salud + Pensión + ARL) - suma_directa| ≤ $1.00 COP.

    Verifica la consistencia aritmética de los aportes calculados
    contra el cálculo directo desde el IBC.
    Tolerancia máxima: $1.00 COP por redondeo ROUND_HALF_UP.

    Ref: context/functional_requirements.md CT-02.
    Raises: ErrorCT02_SumaAportesInconsistente si la diferencia supera $1 COP.
    """
    from decimal import ROUND_HALF_UP

    ibc = ibc_result.ibc
    nivel_arl = ibc_result.nivel_arl_maximo
    tarifa_arl = parametros.tarifas_arl[nivel_arl]

    suma_directa = (
        (ibc * parametros.pct_salud).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        + (ibc * parametros.pct_pension).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        + (ibc * tarifa_arl).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )

    diferencia = abs(aportes_result.total_aportes - suma_directa)

    if diferencia > _TOLERANCIA_CT02:
        raise ErrorCT02_SumaAportesInconsistente(diferencia=diferencia)


def validar_ct03_base_gravable(
    retencion_result: RetencionResult,
    ingreso_bruto_total: Decimal,
    aportes_result: AportesResult,
) -> None:
    """
    CT-03: Base gravable = Ingreso bruto − Salud − Pensión.

    Verifica que la depuración de la retención sea correcta.
    Ref: context/functional_requirements.md CT-03, Art. 383 + Art. 126-1 E.T.
    Raises: ErrorCT03_BaseGravableIncorrecta si la base no coincide.
    """
    from decimal import ROUND_HALF_UP

    esperada = (
        ingreso_bruto_total
        - aportes_result.aporte_salud
        - aportes_result.aporte_pension
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Tolerancia de $1 COP por redondeo acumulado
    diferencia = abs(retencion_result.base_gravable - esperada)
    if diferencia > _TOLERANCIA_CT02:
        raise ErrorCT03_BaseGravableIncorrecta(
            calculada=retencion_result.base_gravable,
            esperada=esperada,
        )


def filtrar_contratos_por_periodo(
    contratos: list[ContratoInput],
    periodo: PeriodoLiquidacion,
) -> tuple[list[ContratoInput], int]:
    """
    CT-04: Excluye contratos cuyas fechas no se superponen con el período.

    Un contrato participa si hay al menos 1 día de superposición entre
    [fecha_inicio, fecha_fin] del contrato y [inicio_mes, fin_mes] del período.

    Ref: context/functional_requirements.md CT-04.

    Returns:
        Tupla (contratos_activos, cantidad_excluidos).
    """
    activos = []
    for contrato in contratos:
        fin_efectivo = min(contrato.fecha_fin, periodo.fecha_fin_mes)
        inicio_efectivo = max(contrato.fecha_inicio, periodo.fecha_inicio_mes)
        if fin_efectivo >= inicio_efectivo:
            activos.append(contrato)

    excluidos = len(contratos) - len(activos)
    return activos, excluidos
