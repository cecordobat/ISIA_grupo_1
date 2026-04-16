import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base


class AccesoContadorPerfil(Base):
    __tablename__ = "accesos_contador_perfil"
    __table_args__ = (
        UniqueConstraint("contador_id", "perfil_id", name="uq_contador_perfil"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    contador_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    perfil_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("perfiles_contratista.id"), nullable=False, index=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    contador: Mapped["Usuario"] = relationship(  # type: ignore[name-defined]
        "Usuario",
        foreign_keys=[contador_id],
        back_populates="accesos_contador",
    )
    perfil: Mapped["PerfilContratista"] = relationship("PerfilContratista")  # type: ignore[name-defined]
