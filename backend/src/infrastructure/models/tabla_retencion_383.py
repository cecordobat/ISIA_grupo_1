"""
Modelo ORM: Tabla Art. 383 E.T. — Retención en la fuente por honorarios.
Actualizable sin redespliegue (RES-T02, INV-04).
Ref: context/data_model.md TablaRetencion383, RN-07
"""
from sqlalchemy import Date, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database import Base


class TablaRetencion383(Base):
    __tablename__ = "tabla_retencion_383"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uvt_desde: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    # uvt_hasta NULL = último tramo (sin techo)
    uvt_hasta: Mapped[float | None] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    tarifa_marginal: Mapped[float] = mapped_column(Numeric(precision=6, scale=4), nullable=False)
    uvt_deduccion: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    vigente_desde: Mapped[object] = mapped_column(Date, nullable=False, index=True)
