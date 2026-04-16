"""
Evaluación del Piso de Protección Social.

Implementa RN-06: cuando el ingreso neto mensual consolidado < 1 SMMLV,
el contratista tiene dos opciones:
  (a) BEPS: aporte del 15% a BEPS (NO acumula semanas de pensión)
  (b) SMMLV_COMPLETO: cotizar sobre 1 SMMLV en el sistema ordinario

Si el ingreso >= 1 SMMLV, retorna NO_APLICA y la cotización continúa normal.

Ref: context/business_rules.md RN-06, Decreto 1174/2020, Art. 193 Ley 1955/2019
"""
from decimal import Decimal

from src.domain.enums import OpcionPisoProteccion
from src.domain.exceptions import PisoProteccionRequeridoError


def evaluar_piso_proteccion(
    ingreso_bruto_total: Decimal,
    smmlv: Decimal,
    opcion_solicitada: OpcionPisoProteccion | None,
) -> OpcionPisoProteccion:
    """
    Determina la opción de Piso de Protección Social aplicable.

    Args:
        ingreso_bruto_total: Ingreso bruto consolidado del período.
        smmlv: Valor del SMMLV vigente (del SnapshotNormativo).
        opcion_solicitada: Opción elegida por el usuario (puede ser None si no aplica
                           o si el usuario aún no ha elegido).

    Returns:
        OpcionPisoProteccion: NO_APLICA si ingreso >= SMMLV,
                               BEPS o SMMLV_COMPLETO según la elección del usuario.

    Raises:
        PisoProteccionRequeridoError: Si el ingreso < SMMLV y el usuario no eligió.
    """
    if ingreso_bruto_total >= smmlv:
        return OpcionPisoProteccion.NO_APLICA

    # Ingreso < SMMLV: se requiere decisión del usuario
    if opcion_solicitada is None or opcion_solicitada == OpcionPisoProteccion.NO_APLICA:
        raise PisoProteccionRequeridoError()

    return opcion_solicitada


def aplica_piso_proteccion(ingreso_bruto_total: Decimal, smmlv: Decimal) -> bool:
    """Retorna True si el ingreso activa la evaluación del Piso de Protección Social."""
    return ingreso_bruto_total < smmlv
