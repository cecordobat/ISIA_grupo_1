"""
Modelo ORM: Tabla de costos presuntos por CIIU.
Resolución DIAN 209 de 2020 — actualizable sin redespliegue.
Ref: context/data_model.md TablaParametroCIIU, RN-02, RES-D01, INV-04
"""
from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database import Base


class TablaParametroCIIU(Base):
    __tablename__ = "tabla_ciiu"

    codigo_ciiu: Mapped[str] = mapped_column(String(10), primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    # pct_costos_presuntos en [0,1] — ej: 0.2700 = 27%
    pct_costos_presuntos: Mapped[float] = mapped_column(
        Numeric(precision=6, scale=4), nullable=False
    )
    vigente_desde: Mapped[object] = mapped_column(Date, nullable=False)
