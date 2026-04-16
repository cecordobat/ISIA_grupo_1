"""
Modelo ORM: Liquidación Período — APPEND-ONLY.

INVARIANTE CRÍTICA (INV-03): Esta tabla es solo de inserción.
No existen métodos update() ni delete() en el repositorio.
En PostgreSQL prod se refuerza con RULEs de BD.

Ref: context/data_model.md LiquidacionPeriodo, INV-03, RES-C03
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import NivelARL, OpcionPisoProteccion
from src.infrastructure.database import Base


class LiquidacionPeriodo(Base):
    __tablename__ = "liquidaciones_periodo"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    perfil_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("perfiles_contratista.id"), nullable=False, index=True
    )
    snapshot_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("snapshots_normativos.id"), nullable=False
    )
    # YYYY-MM
    periodo: Mapped[str] = mapped_column(String(7), nullable=False, index=True)

    # Valores calculados — DECIMAL(18,4) para intermedios, DECIMAL(18,2) para finales
    ingreso_bruto_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    costos_presuntos: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    ibc: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)

    aporte_salud: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    aporte_pension: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    aporte_arl: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    nivel_arl_aplicado: Mapped[NivelARL] = mapped_column(Enum(NivelARL), nullable=False)

    base_gravable_retencion: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    retencion_fuente: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)

    opcion_piso_proteccion: Mapped[OpcionPisoProteccion] = mapped_column(
        Enum(OpcionPisoProteccion), nullable=False
    )

    generado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    perfil: Mapped["PerfilContratista"] = relationship(  # type: ignore[name-defined]
        "PerfilContratista", back_populates="liquidaciones"
    )
    snapshot: Mapped["SnapshotNormativo"] = relationship("SnapshotNormativo")  # type: ignore[name-defined]
