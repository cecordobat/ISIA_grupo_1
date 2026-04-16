"""
Schemas Pydantic para el recurso Contrato.
Ref: context/functional_requirements.md RF-02, INV-01
"""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer

from src.domain.enums import EstadoContrato, NivelARL


class ContratoCreate(BaseModel):
    """Payload para crear un nuevo contrato de prestación de servicios."""

    perfil_id: str
    entidad_contratante: str
    valor_bruto_mensual: Decimal
    nivel_arl: NivelARL
    fecha_inicio: date
    fecha_fin: date | None = None


class ContratoUpdate(BaseModel):
    """Payload para actualizar un contrato existente."""

    entidad_contratante: str
    valor_bruto_mensual: Decimal
    nivel_arl: NivelARL
    fecha_inicio: date
    fecha_fin: date | None = None


class ContratoResponse(BaseModel):
    """Respuesta con los datos del contrato. Decimales serializados como str (INV-01)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    perfil_id: str
    entidad_contratante: str
    valor_bruto_mensual: Decimal
    nivel_arl: NivelARL
    fecha_inicio: date
    fecha_fin: date | None
    estado: EstadoContrato
    created_at: datetime

    @field_serializer("valor_bruto_mensual")
    def serialize_decimal(self, value: Decimal) -> str:
        return str(value)
