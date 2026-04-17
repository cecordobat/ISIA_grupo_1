"""
Schemas para comparación histórica entre períodos.
Ref: RF-12, HU-13
"""
from pydantic import BaseModel


class LiquidacionResumen(BaseModel):
    periodo: str
    ingreso_bruto_total: float
    ibc: float
    aporte_salud: float
    aporte_pension: float
    aporte_arl: float
    retencion_fuente: float
    base_gravable_retencion: float

    model_config = {"from_attributes": True}


class DiferenciasComparacion(BaseModel):
    ingreso_bruto_total: float
    ibc: float
    aporte_salud: float
    aporte_pension: float
    aporte_arl: float
    retencion_fuente: float
    base_gravable_retencion: float


class ComparacionResponse(BaseModel):
    periodo_a: LiquidacionResumen
    periodo_b: LiquidacionResumen
    diferencias: DiferenciasComparacion
