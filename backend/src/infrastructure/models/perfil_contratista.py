"""
Modelo ORM: Perfil del Contratista Independiente.
Ref: context/data_model.md PerfilContratista, RF-01
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import EstadoPerfil, TipoDocumento
from src.infrastructure.database import Base


class PerfilContratista(Base):
    __tablename__ = "perfiles_contratista"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    tipo_documento: Mapped[TipoDocumento] = mapped_column(
        Enum(TipoDocumento), nullable=False
    )
    numero_documento: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    eps: Mapped[str] = mapped_column(String(100), nullable=False)
    afp: Mapped[str] = mapped_column(String(100), nullable=False)
    ciiu_codigo: Mapped[str] = mapped_column(
        String(10), ForeignKey("tabla_ciiu.codigo_ciiu"), nullable=False
    )
    estado: Mapped[EstadoPerfil] = mapped_column(
        Enum(EstadoPerfil), nullable=False, default=EstadoPerfil.ACTIVO
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="perfiles"
    )
    contratos: Mapped[list["Contrato"]] = relationship(  # type: ignore[name-defined]
        "Contrato", back_populates="perfil", lazy="select"
    )
    liquidaciones: Mapped[list["LiquidacionPeriodo"]] = relationship(  # type: ignore[name-defined]
        "LiquidacionPeriodo", back_populates="perfil", lazy="select"
    )
