"""
Cálculo de Aportes al Sistema de Seguridad Social Integral (SGSSI).

Implementa:
  RN-03: Salud = IBC × 12.5%, Pensión = IBC × 16%, ARL = IBC × tarifa según nivel
  RN-06: Piso de Protección Social (15% a BEPS si ingreso < 1 SMMLV)
  RN-08: Nivel ARL más alto entre contratos (ya determinado por ibc_calculator)

REGLA ABSOLUTA (INV-01): Solo Decimal con ROUND_HALF_UP.
REGLA ABSOLUTA (INV-04): Las tarifas vienen de ParametrosNormativosDTO, nunca hardcodeadas.
Ref: context/business_rules.md RN-03, RN-06, RN-08
"""
from decimal import ROUND_HALF_UP, Decimal

from src.domain.enums import NivelARL, OpcionPisoProteccion
from src.engine.dtos import AportesResult, IBCResult, ParametrosNormativosDTO

_DOS_DECIMALES = Decimal("0.01")
_QUINCE_PCT = Decimal("0.15")


def calcular_aportes(
    ibc_result: IBCResult,
    parametros: ParametrosNormativosDTO,
    opcion_piso: OpcionPisoProteccion,
) -> AportesResult:
    """
    Calcula los aportes a Salud, Pensión y ARL sobre el IBC.

    Si la opción es BEPS (Piso de Protección Social, RN-06):
      - Aporte único = ingreso_bruto × 15% destinado a BEPS
      - Salud y ARL son $0 (el contratista no cotiza al sistema ordinario)

    Si la opción es SMMLV_COMPLETO o NO_APLICA:
      - Salud = IBC × pct_salud (ej: 12.5%)
      - Pensión = IBC × pct_pension (ej: 16%)
      - ARL = IBC × tarifa_nivel_arl (ej: 0.522% para nivel I)

    Ref: RN-03 (Ley 100/1993 Art. 204), RN-06 (Decreto 1174/2020), RN-08 (Decreto 1295/1994)
    """
    ibc = ibc_result.ibc
    nivel_arl = ibc_result.nivel_arl_maximo

    if opcion_piso == OpcionPisoProteccion.BEPS:
        # Piso de Protección Social: 15% del ingreso bruto a BEPS
        # NO acumula semanas de pensión en Colpensiones
        aporte_beps = (ibc_result.ingreso_bruto_total * _QUINCE_PCT).quantize(
            _DOS_DECIMALES, rounding=ROUND_HALF_UP
        )
        return AportesResult(
            aporte_salud=Decimal("0.00"),
            aporte_pension=aporte_beps,   # modelado como pensión para el resumen
            aporte_arl=Decimal("0.00"),
            nivel_arl_aplicado=nivel_arl,
            tarifa_arl_aplicada=Decimal("0.00"),
        )

    # Régimen ordinario (RN-03)
    tarifa_arl = parametros.tarifas_arl[nivel_arl]

    aporte_salud = (ibc * parametros.pct_salud).quantize(
        _DOS_DECIMALES, rounding=ROUND_HALF_UP
    )
    aporte_pension = (ibc * parametros.pct_pension).quantize(
        _DOS_DECIMALES, rounding=ROUND_HALF_UP
    )
    aporte_arl = (ibc * tarifa_arl).quantize(
        _DOS_DECIMALES, rounding=ROUND_HALF_UP
    )

    return AportesResult(
        aporte_salud=aporte_salud,
        aporte_pension=aporte_pension,
        aporte_arl=aporte_arl,
        nivel_arl_aplicado=nivel_arl,
        tarifa_arl_aplicada=tarifa_arl,
    )
