"""
Cálculo de Retención en la Fuente por Honorarios.

Implementa:
  RN-07: Base gravable = Ingreso bruto − Salud − Pensión (Art. 126-1 E.T.)
          Retención = tabla Art. 383 E.T. sobre base depurada

La dependencia circular se resuelve por orden de cálculo (INV-05):
  Los aportes (P5) se calculan ANTES que la retención (P6/P7).
  La retención recibe los aportes ya calculados como input.

REGLA ABSOLUTA (INV-01): Solo Decimal con ROUND_HALF_UP.
REGLA ABSOLUTA (INV-02): Sin efectos secundarios.
Ref: context/business_rules.md RN-07, context/invariantes.md INV-05
     Art. 383 y Art. 126-1 Estatuto Tributario
"""
from decimal import ROUND_HALF_UP, Decimal

from src.engine.dtos import AportesResult, ParametrosNormativosDTO, RetencionResult, TramoRetencion

_DOS_DECIMALES = Decimal("0.01")
_CERO = Decimal("0.00")


def _convertir_uvt_a_cop(uvt_cantidad: Decimal, valor_uvt: Decimal) -> Decimal:
    """Convierte UVT a pesos colombianos usando el UVT del snapshot normativo."""
    return (uvt_cantidad * valor_uvt).quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)


def _aplicar_tabla_383(
    base_gravable_cop: Decimal,
    tramos: tuple[TramoRetencion, ...],
    uvt: Decimal,
) -> Decimal:
    """
    Aplica la tabla del Art. 383 E.T. a la base gravable en pesos.

    La tabla está en UVT; se convierte la base a UVT para encontrar el tramo,
    luego se calcula la retención en UVT y se convierte a COP.

    Ref: Art. 383 Estatuto Tributario — tabla de retención por honorarios.
    """
    if uvt <= _CERO or base_gravable_cop <= _CERO:
        return _CERO

    base_en_uvt = (base_gravable_cop / uvt).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )

    for tramo in tramos:
        cumple_inferior = base_en_uvt >= tramo.uvt_desde
        cumple_superior = (tramo.uvt_hasta is None) or (base_en_uvt < tramo.uvt_hasta)

        if cumple_inferior and cumple_superior:
            # Fórmula: (Base_UVT - deducción_UVT) × tarifa_marginal × UVT_COP
            retencion_uvt = (base_en_uvt - tramo.uvt_deduccion) * tramo.tarifa_marginal
            retencion_cop = _convertir_uvt_a_cop(retencion_uvt, uvt)
            return max(_CERO, retencion_cop)

    return _CERO


def calcular_retencion(
    ingreso_bruto_total: Decimal,
    aportes_result: AportesResult,
    parametros: ParametrosNormativosDTO,
) -> RetencionResult:
    """
    Calcula la retención en la fuente sobre honorarios.

    Orden de depuración (Art. 383 + Art. 126-1 E.T.):
      1. Base gravable = Ingreso bruto − Salud − Pensión
         (los aportes son ingreso no constitutivo de renta, Art. 126-1 E.T.)
      2. Aplicar tabla Art. 383 E.T. sobre la base depurada

    Args:
        ingreso_bruto_total: Total de ingresos del período (ya consolidados y proporcionados).
        aportes_result: Aportes calculados en P5 (obligatorio que P5 preceda a P6).
        parametros: Snapshot normativo con tabla Art. 383 y valor UVT.

    Returns:
        RetencionResult con base gravable y retención calculada.
    """
    # Paso 1: depuración de la base gravable (Art. 126-1 E.T.)
    base_gravable = (
        ingreso_bruto_total
        - aportes_result.aporte_salud
        - aportes_result.aporte_pension
    ).quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)

    if base_gravable <= _CERO:
        return RetencionResult(
            base_gravable=_CERO,
            retencion_fuente=_CERO,
            aplica_retencion=False,
        )

    # Paso 2: tabla Art. 383 E.T.
    retencion = _aplicar_tabla_383(
        base_gravable,
        parametros.tramos_retencion_383,
        parametros.uvt,
    )

    return RetencionResult(
        base_gravable=base_gravable,
        retencion_fuente=retencion,
        aplica_retencion=retencion > _CERO,
    )
