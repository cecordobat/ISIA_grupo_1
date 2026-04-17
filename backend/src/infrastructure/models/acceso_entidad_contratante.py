"""
Modelo ORM: Acceso autorizado de entidad contratante a un perfil de contratista.
Solo el contratista puede autorizar y revocar accesos.
Ref: RF-11, HU-12, RNF-06
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database import Base


class AccesoEntidadContratante(Base):
    __tablename__ = "acceso_entidad_contratante"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    entidad_usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    perfil_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("perfiles_contratista.id"), nullable=False, index=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    autorizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
