"""
Fixtures compartidas para todos los tests.

Los parámetros normativos de 2025 se cargan aquí una sola vez.
SMMLV 2025: $1.423.500 — UVT 2025: $49.799
Ref: context/invariantes.md INV-04 — los tests usan estos valores explícitos,
     nunca hardcodeados en el código de producción.
"""
from datetime import date
from decimal import Decimal

import pytest

from src.domain.enums import NivelARL
from src.engine.dtos import (
    ContratoInput,
    ParametrosNormativosDTO,
    PeriodoLiquidacion,
    TramoRetencion,
)

# ─── Constantes del snapshot normativo 2025 ────────────────────────────────────
SMMLV_2025 = Decimal("1423500")
UVT_2025 = Decimal("49799")
PCT_SALUD = Decimal("0.1250")
PCT_PENSION = Decimal("0.1600")

TARIFAS_ARL_2025 = {
    NivelARL.I: Decimal("0.00522"),
    NivelARL.II: Decimal("0.01044"),
    NivelARL.III: Decimal("0.02436"),
    NivelARL.IV: Decimal("0.04350"),
    NivelARL.V: Decimal("0.06960"),
}

# Tabla Art. 383 E.T. — Tramos en UVT (simplificada para tests, valores reales 2025)
TRAMOS_RETENCION_2025 = (
    TramoRetencion(
        uvt_desde=Decimal("0"),
        uvt_hasta=Decimal("95"),
        tarifa_marginal=Decimal("0"),
        uvt_deduccion=Decimal("0"),
    ),
    TramoRetencion(
        uvt_desde=Decimal("95"),
        uvt_hasta=Decimal("150"),
        tarifa_marginal=Decimal("0.19"),
        uvt_deduccion=Decimal("95"),
    ),
    TramoRetencion(
        uvt_desde=Decimal("150"),
        uvt_hasta=Decimal("360"),
        tarifa_marginal=Decimal("0.28"),
        uvt_deduccion=Decimal("18.0"),
    ),
    TramoRetencion(
        uvt_desde=Decimal("360"),
        uvt_hasta=Decimal("640"),
        tarifa_marginal=Decimal("0.33"),
        uvt_deduccion=Decimal("36.0"),
    ),
    TramoRetencion(
        uvt_desde=Decimal("640"),
        uvt_hasta=Decimal("945"),
        tarifa_marginal=Decimal("0.35"),
        uvt_deduccion=Decimal("48.8"),
    ),
    TramoRetencion(
        uvt_desde=Decimal("945"),
        uvt_hasta=Decimal("2300"),
        tarifa_marginal=Decimal("0.37"),
        uvt_deduccion=Decimal("67.7"),
    ),
    TramoRetencion(
        uvt_desde=Decimal("2300"),
        uvt_hasta=None,
        tarifa_marginal=Decimal("0.39"),
        uvt_deduccion=Decimal("113.7"),
    ),
)

# CIIU 6201 — Actividades de programación informática: costos presuntos 27%
CIIU_6201_PCT = Decimal("0.27")


@pytest.fixture
def parametros_2025() -> ParametrosNormativosDTO:
    """Snapshot normativo completo para el año 2025."""
    return ParametrosNormativosDTO(
        smmlv=SMMLV_2025,
        uvt=UVT_2025,
        pct_salud=PCT_SALUD,
        pct_pension=PCT_PENSION,
        pct_costos_presuntos=CIIU_6201_PCT,
        tarifas_arl=TARIFAS_ARL_2025,
        tramos_retencion_383=TRAMOS_RETENCION_2025,
        vigencia_anio=2025,
    )


@pytest.fixture
def periodo_enero_2025() -> PeriodoLiquidacion:
    return PeriodoLiquidacion(anio=2025, mes=1)


@pytest.fixture
def contrato_mes_completo() -> ContratoInput:
    """Un contrato activo todo el mes de enero 2025."""
    return ContratoInput(
        id="contrato-001",
        entidad_contratante="Empresa XYZ S.A.S.",
        valor_bruto_mensual=Decimal("5000000"),
        nivel_arl=NivelARL.I,
        fecha_inicio=date(2025, 1, 1),
        fecha_fin=date(2025, 1, 31),
    )


@pytest.fixture
def contrato_medio_mes() -> ContratoInput:
    """Un contrato activo solo la segunda mitad de enero (16 días)."""
    return ContratoInput(
        id="contrato-002",
        entidad_contratante="Consultora ABC Ltda.",
        valor_bruto_mensual=Decimal("3000000"),
        nivel_arl=NivelARL.II,
        fecha_inicio=date(2025, 1, 16),
        fecha_fin=date(2025, 1, 31),
    )
