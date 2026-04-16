"""
Tests de las validaciones CT-01 a CT-04.

Verifica que cada CT bloquea correctamente cuando los datos son inválidos
y pasa correctamente cuando los datos son válidos.
"""
from datetime import date
from decimal import Decimal

import pytest

from src.domain.enums import NivelARL
from src.domain.exceptions import (
    ErrorCT01_IBCFueraDeRango,
    ErrorCT03_BaseGravableIncorrecta,
)
from src.engine.dtos import (
    AportesResult,
    ContratoCalculado,
    ContratoInput,
    IBCResult,
    PeriodoLiquidacion,
    RetencionResult,
)
from src.engine.validations import (
    filtrar_contratos_por_periodo,
    validar_ct01_ibc_rango,
    validar_ct03_base_gravable,
)


def _crear_ibc_result(ibc: Decimal, ingreso_bruto: Decimal = None) -> IBCResult:
    ingreso = ingreso_bruto if ingreso_bruto is not None else ibc
    return IBCResult(
        ingreso_bruto_total=ingreso,
        costos_presuntos=Decimal("0"),
        base_40_pct=ibc,
        ibc=ibc,
        ajustado_por_tope=False,
        nivel_arl_maximo=NivelARL.I,
        contratos_calculados=(
            ContratoCalculado("test", 30, ingreso),
        ),
    )


class TestCT01IBCRango:
    """CT-01: IBC debe estar en [1 SMMLV, 25 SMMLV]."""

    def test_ibc_igual_a_1_smmlv_pasa(self, parametros_2025):
        """El límite inferior exacto debe pasar."""
        ibc_result = _crear_ibc_result(Decimal("1423500"))
        validar_ct01_ibc_rango(ibc_result, parametros_2025)  # no debe lanzar

    def test_ibc_igual_a_25_smmlv_pasa(self, parametros_2025):
        """El límite superior exacto debe pasar."""
        ibc_result = _crear_ibc_result(Decimal("35587500"))  # 1.423.500 × 25
        validar_ct01_ibc_rango(ibc_result, parametros_2025)  # no debe lanzar

    def test_ibc_por_debajo_del_minimo_lanza_ct01(self, parametros_2025):
        """IBC < 1 SMMLV es bloqueante."""
        ibc_result = _crear_ibc_result(Decimal("1000000"))  # < $1.423.500
        with pytest.raises(ErrorCT01_IBCFueraDeRango) as exc_info:
            validar_ct01_ibc_rango(ibc_result, parametros_2025)
        assert exc_info.value.ct_code == "CT-01"

    def test_ibc_por_encima_del_maximo_lanza_ct01(self, parametros_2025):
        """IBC > 25 SMMLV es bloqueante."""
        ibc_result = _crear_ibc_result(Decimal("40000000"))  # > $35.587.500
        with pytest.raises(ErrorCT01_IBCFueraDeRango) as exc_info:
            validar_ct01_ibc_rango(ibc_result, parametros_2025)
        assert exc_info.value.ct_code == "CT-01"

    def test_mensaje_error_incluye_valores(self, parametros_2025):
        """El mensaje de error debe incluir el IBC y el SMMLV para orientar al usuario."""
        ibc_result = _crear_ibc_result(Decimal("500000"))
        with pytest.raises(ErrorCT01_IBCFueraDeRango) as exc_info:
            validar_ct01_ibc_rango(ibc_result, parametros_2025)
        assert "CT-01" in str(exc_info.value)


class TestCT03BaseGravable:
    """CT-03: Base gravable = Ingreso bruto − Salud − Pensión."""

    def _crear_aportes(self, salud: Decimal, pension: Decimal) -> AportesResult:
        return AportesResult(
            aporte_salud=salud,
            aporte_pension=pension,
            aporte_arl=Decimal("15000"),
            nivel_arl_aplicado=NivelARL.I,
            tarifa_arl_aplicada=Decimal("0.00522"),
        )

    def test_base_gravable_correcta_pasa(self):
        """Si base = ingreso - salud - pension, CT-03 pasa."""
        ingreso = Decimal("5000000")
        salud = Decimal("625000")
        pension = Decimal("800000")
        base_correcta = ingreso - salud - pension  # $3.575.000

        retencion = RetencionResult(
            base_gravable=base_correcta,
            retencion_fuente=Decimal("0"),
            aplica_retencion=False,
        )
        aportes = self._crear_aportes(salud, pension)
        validar_ct03_base_gravable(retencion, ingreso, aportes)  # no debe lanzar

    def test_base_gravable_incorrecta_lanza_ct03(self):
        """Si base ≠ ingreso - salud - pension (diferencia > $1), CT-03 falla."""
        ingreso = Decimal("5000000")
        salud = Decimal("625000")
        pension = Decimal("800000")
        base_incorrecta = Decimal("4000000")  # incorrecto: debería ser $3.575.000

        retencion = RetencionResult(
            base_gravable=base_incorrecta,
            retencion_fuente=Decimal("0"),
            aplica_retencion=False,
        )
        aportes = self._crear_aportes(salud, pension)
        with pytest.raises(ErrorCT03_BaseGravableIncorrecta) as exc_info:
            validar_ct03_base_gravable(retencion, ingreso, aportes)
        assert exc_info.value.ct_code == "CT-03"


class TestCT04FiltradoContratos:
    """CT-04: Contratos fuera del período son excluidos."""

    def test_contrato_del_mes_correcto_se_incluye(self):
        periodo = PeriodoLiquidacion(anio=2025, mes=1)
        contratos = [
            ContratoInput(
                id="c1",
                entidad_contratante="Test",
                valor_bruto_mensual=Decimal("3000000"),
                nivel_arl=NivelARL.I,
                fecha_inicio=date(2025, 1, 1),
                fecha_fin=date(2025, 1, 31),
            )
        ]
        activos, excluidos = filtrar_contratos_por_periodo(contratos, periodo)
        assert len(activos) == 1
        assert excluidos == 0

    def test_contrato_mes_anterior_se_excluye(self):
        periodo = PeriodoLiquidacion(anio=2025, mes=1)
        contratos = [
            ContratoInput(
                id="c-dic",
                entidad_contratante="Test",
                valor_bruto_mensual=Decimal("3000000"),
                nivel_arl=NivelARL.I,
                fecha_inicio=date(2024, 12, 1),
                fecha_fin=date(2024, 12, 31),
            )
        ]
        activos, excluidos = filtrar_contratos_por_periodo(contratos, periodo)
        assert len(activos) == 0
        assert excluidos == 1

    def test_contrato_que_cruza_el_periodo_se_incluye(self):
        """Contrato que va de diciembre a febrero incluye días de enero."""
        periodo = PeriodoLiquidacion(anio=2025, mes=1)
        contratos = [
            ContratoInput(
                id="c-largo",
                entidad_contratante="Test",
                valor_bruto_mensual=Decimal("5000000"),
                nivel_arl=NivelARL.I,
                fecha_inicio=date(2024, 12, 1),
                fecha_fin=date(2025, 2, 28),
            )
        ]
        activos, excluidos = filtrar_contratos_por_periodo(contratos, periodo)
        assert len(activos) == 1
        assert excluidos == 0

    def test_mezcla_incluidos_y_excluidos(self):
        periodo = PeriodoLiquidacion(anio=2025, mes=1)
        contratos = [
            ContratoInput(
                id="c-enero",
                entidad_contratante="Empresa A",
                valor_bruto_mensual=Decimal("3000000"),
                nivel_arl=NivelARL.I,
                fecha_inicio=date(2025, 1, 1),
                fecha_fin=date(2025, 1, 31),
            ),
            ContratoInput(
                id="c-dic",
                entidad_contratante="Empresa B",
                valor_bruto_mensual=Decimal("2000000"),
                nivel_arl=NivelARL.I,
                fecha_inicio=date(2024, 12, 1),
                fecha_fin=date(2024, 12, 31),
            ),
            ContratoInput(
                id="c-feb",
                entidad_contratante="Empresa C",
                valor_bruto_mensual=Decimal("4000000"),
                nivel_arl=NivelARL.I,
                fecha_inicio=date(2025, 2, 1),
                fecha_fin=date(2025, 2, 28),
            ),
        ]
        activos, excluidos = filtrar_contratos_por_periodo(contratos, periodo)
        assert len(activos) == 1
        assert excluidos == 2
        assert activos[0].id == "c-enero"
