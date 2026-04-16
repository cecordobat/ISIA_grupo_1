import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base


class LiquidacionConfirmacion(Base):
    __tablename__ = "liquidaciones_confirmacion"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    liquidacion_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("liquidaciones_periodo.id"), nullable=False, unique=True, index=True
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    confirmado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    liquidacion: Mapped["LiquidacionPeriodo"] = relationship(  # type: ignore[name-defined]
        "LiquidacionPeriodo",
        back_populates="confirmacion",
    )
    usuario: Mapped["Usuario"] = relationship("Usuario")  # type: ignore[name-defined]
