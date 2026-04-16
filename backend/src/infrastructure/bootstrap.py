import json
import uuid
from datetime import date

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncEngine

from src.infrastructure.models.snapshot_normativo import SnapshotNormativo
from src.infrastructure.models.tabla_ciiu import TablaParametroCIIU
from src.infrastructure.models.tabla_retencion_383 import TablaRetencion383

SNAPSHOTS_BASE = [
    {
        "id": str(uuid.uuid4()),
        "smmlv": 1423500,
        "uvt": 49799,
        "pct_salud": 0.1250,
        "pct_pension": 0.1600,
        "tabla_arl_json": json.dumps(
            {
                "I": "0.00522",
                "II": "0.01044",
                "III": "0.02436",
                "IV": "0.04350",
                "V": "0.06960",
            }
        ),
        "vigencia_anio": 2025,
    }
]

TABLA_CIIU_BASE = [
    {
        "codigo_ciiu": "0125",
        "descripcion": "Cultivo de flor de corte",
        "pct_costos_presuntos": 0.65,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "codigo_ciiu": "6201",
        "descripcion": "Actividades de desarrollo de sistemas informaticos",
        "pct_costos_presuntos": 0.27,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "codigo_ciiu": "6910",
        "descripcion": "Actividades juridicas",
        "pct_costos_presuntos": 0.27,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "codigo_ciiu": "6920",
        "descripcion": "Actividades de contabilidad y auditoria",
        "pct_costos_presuntos": 0.27,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "codigo_ciiu": "7020",
        "descripcion": "Actividades de consultoria de gestion",
        "pct_costos_presuntos": 0.27,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "codigo_ciiu": "9001",
        "descripcion": "Actividades artisticas con costo presunto alto",
        "pct_costos_presuntos": 0.65,
        "vigente_desde": date(2025, 1, 1),
    },
]

TRAMOS_RETENCION_BASE = [
    {
        "uvt_desde": 0,
        "uvt_hasta": 95,
        "tarifa_marginal": 0,
        "uvt_deduccion": 0,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "uvt_desde": 95,
        "uvt_hasta": 150,
        "tarifa_marginal": 0.19,
        "uvt_deduccion": 95,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "uvt_desde": 150,
        "uvt_hasta": 360,
        "tarifa_marginal": 0.28,
        "uvt_deduccion": 18,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "uvt_desde": 360,
        "uvt_hasta": 640,
        "tarifa_marginal": 0.33,
        "uvt_deduccion": 36,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "uvt_desde": 640,
        "uvt_hasta": 945,
        "tarifa_marginal": 0.35,
        "uvt_deduccion": 48.8,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "uvt_desde": 945,
        "uvt_hasta": 2300,
        "tarifa_marginal": 0.37,
        "uvt_deduccion": 67.7,
        "vigente_desde": date(2025, 1, 1),
    },
    {
        "uvt_desde": 2300,
        "uvt_hasta": None,
        "tarifa_marginal": 0.39,
        "uvt_deduccion": 113.7,
        "vigente_desde": date(2025, 1, 1),
    },
]


async def seed_reference_data(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        snapshots_count = await conn.scalar(select(func.count()).select_from(SnapshotNormativo))
        if not snapshots_count:
            await conn.execute(insert(SnapshotNormativo), SNAPSHOTS_BASE)

        ciiu_count = await conn.scalar(select(func.count()).select_from(TablaParametroCIIU))
        if not ciiu_count:
            await conn.execute(insert(TablaParametroCIIU), TABLA_CIIU_BASE)

        retencion_count = await conn.scalar(select(func.count()).select_from(TablaRetencion383))
        if not retencion_count:
            await conn.execute(insert(TablaRetencion383), TRAMOS_RETENCION_BASE)
