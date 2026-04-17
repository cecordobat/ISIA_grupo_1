"""
Tests unitarios: comparación histórica entre períodos.
Ref: RF-12, HU-13, INV-03
"""
from src.api.schemas.comparacion import ComparacionResponse, DiferenciasComparacion, LiquidacionResumen


def test_comparacion_response_schema():
    resumen_a = LiquidacionResumen(
        periodo="2025-01",
        ingreso_bruto_total=5000000.0,
        ibc=2000000.0,
        aporte_salud=250000.0,
        aporte_pension=320000.0,
        aporte_arl=10440.0,
        retencion_fuente=0.0,
        base_gravable_retencion=1500000.0,
    )
    resumen_b = LiquidacionResumen(
        periodo="2025-02",
        ingreso_bruto_total=6000000.0,
        ibc=2400000.0,
        aporte_salud=300000.0,
        aporte_pension=384000.0,
        aporte_arl=12528.0,
        retencion_fuente=0.0,
        base_gravable_retencion=1800000.0,
    )
    diferencias = DiferenciasComparacion(
        ingreso_bruto_total=resumen_b.ingreso_bruto_total - resumen_a.ingreso_bruto_total,
        ibc=resumen_b.ibc - resumen_a.ibc,
        aporte_salud=resumen_b.aporte_salud - resumen_a.aporte_salud,
        aporte_pension=resumen_b.aporte_pension - resumen_a.aporte_pension,
        aporte_arl=resumen_b.aporte_arl - resumen_a.aporte_arl,
        retencion_fuente=0.0,
        base_gravable_retencion=resumen_b.base_gravable_retencion - resumen_a.base_gravable_retencion,
    )
    response = ComparacionResponse(periodo_a=resumen_a, periodo_b=resumen_b, diferencias=diferencias)

    assert response.diferencias.ingreso_bruto_total == 1000000.0
    assert response.diferencias.ibc == 400000.0
    assert response.periodo_a.periodo == "2025-01"
    assert response.periodo_b.periodo == "2025-02"
