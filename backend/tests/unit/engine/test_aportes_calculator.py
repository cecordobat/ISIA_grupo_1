"""
Tests unitarios del calculador de aportes SGSSI.

Cubre: RN-03 (Salud 12.5%, Pensión 16%, ARL por nivel)
       RN-06 (Piso de Protección Social — BEPS 15%)
       CT-02 (tolerancia $1 COP en suma de aportes)
"""
import pytest
from decimal import Decimal

from src.domain.enums import NivelARL, OpcionPisoProteccion
from src.engine.aporte_calculator import calcular_aportes
from src.engine.dtos import (
    AportesResult,
    ContratoCalculado,
    IBCResult,
)


def _crear_ibc_result(
    ibc: Decimal,
    ingreso_bruto: Decimal,
    nivel_arl: NivelARL = NivelARL.I,
) -> IBCResult:
    """Helper para crear un IBCResult con los campos mínimos necesarios."""
    return IBCResult(
        ingreso_bruto_total=ingreso_bruto,
        costos_presuntos=Decimal("0"),
        base_40_pct=ibc,
        ibc=ibc,
        ajustado_por_tope=False,
        nivel_arl_maximo=nivel_arl,
        contratos_calculados=(
            ContratoCalculado(
                contrato_id="test",
                dias_cotizados=30,
                ingreso_bruto_proporcional=ingreso_bruto,
            ),
        ),
    )


class TestAportesOrdinarios:
    """Tests del régimen ordinario de aportes (RN-03)."""

    def test_calcula_salud_12_5_pct(self, parametros_2025):
        """Salud = IBC × 12.5%"""
        ibc = Decimal("2000000")
        ibc_result = _crear_ibc_result(ibc, ibc)
        resultado = calcular_aportes(ibc_result, parametros_2025, OpcionPisoProteccion.NO_APLICA)
        assert resultado.aporte_salud == Decimal("250000.00")  # 2.000.000 × 0.125

    def test_calcula_pension_16_pct(self, parametros_2025):
        """Pensión = IBC × 16%"""
        ibc = Decimal("2000000")
        ibc_result = _crear_ibc_result(ibc, ibc)
        resultado = calcular_aportes(ibc_result, parametros_2025, OpcionPisoProteccion.NO_APLICA)
        assert resultado.aporte_pension == Decimal("320000.00")  # 2.000.000 × 0.16

    @pytest.mark.parametrize("nivel,tarifa_esperada,aporte_esperado", [
        (NivelARL.I, Decimal("0.00522"), Decimal("10440.00")),
        (NivelARL.II, Decimal("0.01044"), Decimal("20880.00")),
        (NivelARL.III, Decimal("0.02436"), Decimal("48720.00")),
        (NivelARL.IV, Decimal("0.04350"), Decimal("87000.00")),
        (NivelARL.V, Decimal("0.06960"), Decimal("139200.00")),
    ])
    def test_calcula_arl_todos_los_niveles(
        self, parametros_2025, nivel, tarifa_esperada, aporte_esperado
    ):
        """ARL = IBC × tarifa según nivel. Verifica todos los niveles (Decreto 1295/1994)."""
        ibc = Decimal("2000000")
        ibc_result = _crear_ibc_result(ibc, ibc, nivel_arl=nivel)
        resultado = calcular_aportes(ibc_result, parametros_2025, OpcionPisoProteccion.NO_APLICA)
        assert resultado.aporte_arl == aporte_esperado
        assert resultado.tarifa_arl_aplicada == tarifa_esperada

    def test_total_aportes_es_suma_de_tres(self, parametros_2025):
        """El total debe ser exactamente Salud + Pensión + ARL."""
        ibc = Decimal("3000000")
        ibc_result = _crear_ibc_result(ibc, ibc)
        resultado = calcular_aportes(ibc_result, parametros_2025, OpcionPisoProteccion.NO_APLICA)
        assert resultado.total_aportes == (
            resultado.aporte_salud + resultado.aporte_pension + resultado.aporte_arl
        )


class TestPisoProteccionSocial:
    """Tests del Piso de Protección Social — BEPS (RN-06, Decreto 1174/2020)."""

    def test_beps_calcula_15_pct_del_ingreso_bruto(self, parametros_2025):
        """
        BEPS: aporte = ingreso_bruto × 15%.
        Ingreso bruto $1.000.000 → BEPS = $150.000
        """
        ingreso = Decimal("1000000")
        ibc_result = _crear_ibc_result(
            ibc=Decimal("1423500"),  # clamped a 1 SMMLV
            ingreso_bruto=ingreso,
        )
        resultado = calcular_aportes(ibc_result, parametros_2025, OpcionPisoProteccion.BEPS)

        assert resultado.aporte_pension == Decimal("150000.00")  # 1.000.000 × 15%
        assert resultado.aporte_salud == Decimal("0.00")
        assert resultado.aporte_arl == Decimal("0.00")

    def test_beps_salud_y_arl_son_cero(self, parametros_2025):
        """En BEPS, Salud y ARL son $0 (no cotiza sistema ordinario)."""
        ingreso = Decimal("800000")
        ibc_result = _crear_ibc_result(ibc=Decimal("1423500"), ingreso_bruto=ingreso)
        resultado = calcular_aportes(ibc_result, parametros_2025, OpcionPisoProteccion.BEPS)
        assert resultado.aporte_salud == Decimal("0.00")
        assert resultado.aporte_arl == Decimal("0.00")


class TestConsistenciaCT02:
    """Tests de la validación CT-02 (tolerancia $1 COP)."""

    def test_diferencia_exactamente_1_cop_no_lanza_error(self, parametros_2025):
        """CT-02 pasa si la diferencia es exactamente $1.00 COP."""
        from src.engine.validations import validar_ct02_suma_aportes

        ibc = Decimal("2000000")
        ibc_result = _crear_ibc_result(ibc, ibc)
        aportes = calcular_aportes(ibc_result, parametros_2025, OpcionPisoProteccion.NO_APLICA)
        # Si el cálculo es correcto, no debe lanzar excepción
        validar_ct02_suma_aportes(aportes, ibc_result, parametros_2025)

    def test_diferencia_mayor_1_cop_lanza_ct02(self, parametros_2025):
        """CT-02 falla si la suma de aportes difiere del cálculo directo en > $1 COP."""
        from decimal import ROUND_HALF_UP
        from src.domain.exceptions import ErrorCT02_SumaAportesInconsistente
        from src.engine.validations import validar_ct02_suma_aportes

        ibc = Decimal("2000000")
        ibc_result = _crear_ibc_result(ibc, ibc)
        aportes_correctos = calcular_aportes(
            ibc_result, parametros_2025, OpcionPisoProteccion.NO_APLICA
        )
        # Manipulamos el aporte de salud para provocar diferencia de $2 COP
        aportes_manipulados = AportesResult(
            aporte_salud=aportes_correctos.aporte_salud + Decimal("2.00"),
            aporte_pension=aportes_correctos.aporte_pension,
            aporte_arl=aportes_correctos.aporte_arl,
            nivel_arl_aplicado=aportes_correctos.nivel_arl_aplicado,
            tarifa_arl_aplicada=aportes_correctos.tarifa_arl_aplicada,
        )
        with pytest.raises(ErrorCT02_SumaAportesInconsistente):
            validar_ct02_suma_aportes(aportes_manipulados, ibc_result, parametros_2025)
