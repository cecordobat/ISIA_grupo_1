"""
Schemas para endpoints de verificación de cumplimiento por entidad contratante.
Principio de mínimo privilegio: solo datos de cumplimiento, sin detalle de cálculo.
Ref: RF-11, HU-12, RNF-06
"""
from pydantic import BaseModel


class AutorizarAccesoRequest(BaseModel):
    entidad_email: str


class EstadoCumplimientoResponse(BaseModel):
    nombre_contratista: str
    documento: str
    periodo_reciente: str | None
    tiene_liquidacion_confirmada: bool
    estado: str

    model_config = {"from_attributes": True}
