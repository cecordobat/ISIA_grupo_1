"""
Schemas Pydantic para endpoints de administración de parámetros normativos.
Ref: RF-10, HU-11, INV-04
"""
from datetime import date

from pydantic import BaseModel, Field


class SnapshotNormativoCreate(BaseModel):
    smmlv: float = Field(..., gt=0, description="Salario Mínimo Mensual Legal Vigente")
    uvt: float = Field(..., gt=0, description="Unidad de Valor Tributario")
    pct_salud: float = Field(default=0.125, ge=0, le=1)
    pct_pension: float = Field(default=0.16, ge=0, le=1)
    tabla_arl_json: str = Field(
        ...,
        description='JSON con tasas ARL por nivel, ej: {"I":"0.00522","II":"0.01044",...}'
    )
    vigencia_anio: int = Field(..., ge=2020, le=2100)


class SnapshotNormativoResponse(BaseModel):
    id: str
    smmlv: float
    uvt: float
    pct_salud: float
    pct_pension: float
    tabla_arl_json: str
    vigencia_anio: int

    model_config = {"from_attributes": True}


class CIIUCreate(BaseModel):
    codigo_ciiu: str = Field(..., min_length=4, max_length=10)
    descripcion: str = Field(..., min_length=5, max_length=500)
    pct_costos_presuntos: float = Field(..., ge=0, le=1)
    vigente_desde: date


class CIIUResponse(BaseModel):
    codigo_ciiu: str
    descripcion: str
    pct_costos_presuntos: float
    vigente_desde: date

    model_config = {"from_attributes": True}


class TramoRetencionCreate(BaseModel):
    uvt_desde: float = Field(..., ge=0)
    uvt_hasta: float | None = None
    tarifa_marginal: float = Field(..., ge=0, le=1)
    uvt_deduccion: float = Field(..., ge=0)
    vigente_desde: date


class TramoRetencionResponse(BaseModel):
    id: int
    uvt_desde: float
    uvt_hasta: float | None
    tarifa_marginal: float
    uvt_deduccion: float
    vigente_desde: date

    model_config = {"from_attributes": True}
