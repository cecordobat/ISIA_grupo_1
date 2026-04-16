"""
Modelo ORM: Contrato de prestación de servicios.
Ref: context/data_model.md Contrato, RF-02
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import EstadoContrato, NivelARL
from src.infrastructure.database import Base


class Contrato(Base):
    __tablename__ = "contratos"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    perfil_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("perfiles_contratista.id"), nullable=False, index=True
    )
    entidad_contratante: Mapped[str] = mapped_column(String(200), nullable=False)
    # DECIMAL(18,4) para ingresos — INV-01: nunca float
    valor_bruto_mensual: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=4), nullable=False
    )
    nivel_arl: Mapped[NivelARL] = mapped_column(Enum(NivelARL), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[EstadoContrato] = mapped_column(
        Enum(EstadoContrato), nullable=False, default=EstadoContrato.ACTIVO
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    perfil: Mapped["PerfilContratista"] = relationship(  # type: ignore[name-defined]
        "PerfilContratista", back_populates="contratos"
    )
