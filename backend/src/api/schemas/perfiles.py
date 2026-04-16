from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

from src.domain.enums import EstadoPerfil, TipoDocumento


class PerfilCreate(BaseModel):
    """Payload para crear un nuevo perfil de contratista."""

    tipo_documento: TipoDocumento
    numero_documento: str
    nombre_completo: str
    eps: str
    afp: str
    ciiu_codigo: str
    confirmar_ciiu_alto: bool = False


class PerfilUpdate(BaseModel):
    """Payload para actualizar un perfil existente de contratista."""

    tipo_documento: TipoDocumento
    numero_documento: str
    nombre_completo: str
    eps: str
    afp: str
    ciiu_codigo: str
    confirmar_ciiu_alto: bool = False


class PerfilResponse(BaseModel):
    """Respuesta con los datos del perfil."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    usuario_id: str
    tipo_documento: TipoDocumento
    numero_documento: str
    nombre_completo: str
    eps: str
    afp: str
    ciiu_codigo: str
    pct_costos_presuntos: Decimal | None = None
    estado: EstadoPerfil
    created_at: datetime

    @field_serializer("pct_costos_presuntos")
    def serialize_decimal(self, value: Decimal | None) -> str | None:
        return None if value is None else str(value)
