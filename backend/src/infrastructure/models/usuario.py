"""
Modelo ORM: Usuario del sistema (contratista o contador).
Ref: context/data_model.md, context/non_functional_requirements.md RNF-06
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import RolUsuario
from src.infrastructure.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario), nullable=False, default=RolUsuario.CONTRATISTA
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    perfiles: Mapped[list["PerfilContratista"]] = relationship(  # type: ignore[name-defined]
        "PerfilContratista", back_populates="usuario", lazy="select"
    )
