"""
Schemas Pydantic para el recurso PerfilContratista.
Ref: context/functional_requirements.md RF-01
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.domain.enums import EstadoPerfil, TipoDocumento


class PerfilCreate(BaseModel):
    """Payload para crear un nuevo perfil de contratista."""

    tipo_documento: TipoDocumento
    numero_documento: str
    nombre_completo: str
    eps: str
    afp: str
    ciiu_codigo: str


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
    estado: EstadoPerfil
    created_at: datetime
