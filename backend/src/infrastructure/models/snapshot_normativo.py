"""
Modelo ORM: Snapshot Normativo.
Foto de los parámetros legales en el momento de la liquidación.
Ref: context/data_model.md SnapshotNormativo, RES-C03, INV-04
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database import Base


class SnapshotNormativo(Base):
    __tablename__ = "snapshots_normativos"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    smmlv: Mapped[float] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    uvt: Mapped[float] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    pct_salud: Mapped[float] = mapped_column(Numeric(precision=6, scale=4), nullable=False)
    pct_pension: Mapped[float] = mapped_column(Numeric(precision=6, scale=4), nullable=False)
    # tabla_arl guardada como JSON string: {"I": "0.00522", "II": "0.01044", ...}
    tabla_arl_json: Mapped[str] = mapped_column(String(500), nullable=False)
    vigencia_anio: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
