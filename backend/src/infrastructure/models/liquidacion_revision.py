import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base


class LiquidacionRevision(Base):
    __tablename__ = "liquidaciones_revision"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    liquidacion_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("liquidaciones_periodo.id"), nullable=False, unique=True, index=True
    )
    contador_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    nota: Mapped[str] = mapped_column(Text, nullable=False)
    aprobada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    revisado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    liquidacion: Mapped["LiquidacionPeriodo"] = relationship(  # type: ignore[name-defined]
        "LiquidacionPeriodo",
        back_populates="revision",
    )
    contador: Mapped["Usuario"] = relationship("Usuario")  # type: ignore[name-defined]
