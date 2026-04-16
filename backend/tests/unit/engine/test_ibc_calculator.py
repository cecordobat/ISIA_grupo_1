"""
Tests unitarios del calculador de IBC.

Cubre: RN-01 (regla 40%), RN-02 (costos presuntos CIIU),
       RN-04 (acumulación), RN-05 (proporcionalidad días), RN-08 (ARL máximo)

IMPORTANTE: Todos los valores monetarios son Decimal con string literal.
            Se verifica el resultado exacto, no aproximado.
"""
from datetime import date
from decimal import Decimal

import pytest

from src.domain.enums import NivelARL
from src.engine.dtos import ContratoInput
from src.engine.ibc_calculator import (
    calcular_dias_cotizados,
    calcular_ibc_consolidado,
)


class TestDiasCotizados:
    """Tests para el cálculo de proporcionalidad por días (RN-05)."""

    def test_mes_completo_retorna_30(self, periodo_enero_2025, contrato_mes_completo):
        """Contrato que cubre todo el mes retorna exactamente 30 días UGPP."""
        dias = calcular_dias_cotizados(contrato_mes_completo, periodo_enero_2025)
        assert dias == 30

    def test_media_quincena_desde_dia_16(self, periodo_enero_2025):
        """Contrato del 16 al 31 de enero = 16 días calendario."""
        contrato = ContratoInput(
            id="c1",
            entidad_contratante="Test",
            valor_bruto_mensual=Decimal("3000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 16),
            fecha_fin=date(2025, 1, 31),
        )
        dias = calcular_dias_cotizados(contrato, periodo_enero_2025)
        assert dias == 16

    def test_contrato_fuera_del_periodo_retorna_cero(self, periodo_enero_2025):
        """Contrato que termina antes del inicio del período retorna 0."""
        contrato = ContratoInput(
            id="c2",
            entidad_contratante="Test",
            valor_bruto_mensual=Decimal("2000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2024, 12, 1),
            fecha_fin=date(2024, 12, 31),
        )
        dias = calcular_dias_cotizados(contrato, periodo_enero_2025)
        assert dias == 0

    def test_contrato_primer_dia_retorna_1(self, periodo_enero_2025):
        contrato = ContratoInput(
            id="c3",
            entidad_contratante="Test",
            valor_bruto_mensual=Decimal("2000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 1),
        )
        dias = calcular_dias_cotizados(contrato, periodo_enero_2025)
        assert dias == 1


class TestIBCConsolidado:
    """Tests del IBC consolidado — el cálculo más crítico del sistema."""

    def test_caso_base_un_contrato_mes_completo(
        self, parametros_2025, periodo_enero_2025, contrato_mes_completo
    ):
        """
        Caso canónico: 1 contrato, $5.000.000, CIIU 6201 (costos 27%), mes completo.

        Cálculo manual:
          Ingreso bruto = $5.000.000
          Costos presuntos = $5.000.000 × 27% = $1.350.000
          Base neta = $5.000.000 − $1.350.000 = $3.650.000
          Base 40% = $3.650.000 × 40% = $1.460.000
          Tope inferior = $1.423.500 (1 SMMLV)
          Tope superior = $35.587.500 (25 SMMLV)
          IBC = $1.460.000 (dentro del rango, sin ajuste)
        """
        resultado = calcular_ibc_consolidado(
            [contrato_mes_completo], parametros_2025, periodo_enero_2025
        )
        assert resultado.ingreso_bruto_total == Decimal("5000000.0000")
        assert resultado.costos_presuntos == Decimal("1350000.0000")
        assert resultado.base_40_pct == Decimal("1460000.0000")
        assert resultado.ibc == Decimal("1460000.0000")
        assert not resultado.ajustado_por_tope

    def test_ibc_tope_inferior_1_smmlv(self, parametros_2025, periodo_enero_2025):
        """
        Ingreso muy bajo: el 40% queda por debajo de 1 SMMLV → se topa al mínimo.

        SMMLV 2025 = $1.423.500
        Ingreso bruto = $1.500.000
        Costos presuntos = $1.500.000 × 27% = $405.000
        Base neta = $1.095.000
        Base 40% = $438.000 < $1.423.500 → IBC = $1.423.500
        """
        contrato = ContratoInput(
            id="c-bajo",
            entidad_contratante="Test",
            valor_bruto_mensual=Decimal("1500000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 31),
        )
        resultado = calcular_ibc_consolidado([contrato], parametros_2025, periodo_enero_2025)
        assert resultado.ibc == Decimal("1423500")
        assert resultado.ajustado_por_tope is True

    def test_ibc_tope_superior_25_smmlv(self, parametros_2025, periodo_enero_2025):
        """
        Ingreso muy alto: el 40% supera 25 SMMLV → se topa al máximo.

        25 SMMLV = 25 × $1.423.500 = $35.587.500
        Ingreso bruto = $100.000.000
        Costos presuntos = $100.000.000 × 27% = $27.000.000
        Base neta = $73.000.000
        Base 40% = $29.200.000 < $35.587.500 → IBC = $29.200.000 (sin tope)

        Para activar tope superior usamos ingreso muy alto:
        Base 40% > $35.587.500 → necesitamos ingreso tal que
        (ingreso × 0.73) × 0.40 > $35.587.500
        ingreso > $122.026.027 aprox.
        """
        contrato = ContratoInput(
            id="c-alto",
            entidad_contratante="Empresa Grande S.A.",
            valor_bruto_mensual=Decimal("130000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 31),
        )
        resultado = calcular_ibc_consolidado([contrato], parametros_2025, periodo_enero_2025)
        assert resultado.ibc == Decimal("35587500")
        assert resultado.ajustado_por_tope is True

    def test_acumulacion_dos_contratos_rn04(
        self, parametros_2025, periodo_enero_2025,
        contrato_mes_completo, contrato_medio_mes
    ):
        """
        RN-04: Dos contratos se ACUMULAN antes de aplicar el 40%.
        NO se calcula el IBC por separado para cada contrato.

        Contrato 1: $5.000.000 × 30/30 = $5.000.000
        Contrato 2: $3.000.000 × 16/30 = $1.600.000
        Total = $6.600.000
        Costos presuntos = $6.600.000 × 27% = $1.782.000
        Base neta = $4.818.000
        Base 40% = $1.927.200
        IBC = $1.927.200 (dentro del rango)
        """
        # Hacer contrato_medio_mes nivel ARL I para aislar el cálculo de ARL
        contrato_2 = ContratoInput(
            id="contrato-002",
            entidad_contratante="Consultora ABC",
            valor_bruto_mensual=Decimal("3000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 16),
            fecha_fin=date(2025, 1, 31),
        )
        resultado = calcular_ibc_consolidado(
            [contrato_mes_completo, contrato_2], parametros_2025, periodo_enero_2025
        )
        ingreso_esperado = Decimal("5000000.0000") + Decimal("3000000") * Decimal("16") / Decimal("30")
        assert resultado.ingreso_bruto_total == ingreso_esperado.quantize(Decimal("0.0001"))
        assert not resultado.ajustado_por_tope

    def test_proporcionalidad_exacta_15_dias_rn05(self, parametros_2025, periodo_enero_2025):
        """
        RN-05: Contrato de 15 días paga proporcionalmente.
        $6.000.000 × 15/30 = $3.000.000
        """
        contrato = ContratoInput(
            id="c-15dias",
            entidad_contratante="Test",
            valor_bruto_mensual=Decimal("6000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 15),
        )
        resultado = calcular_ibc_consolidado([contrato], parametros_2025, periodo_enero_2025)
        assert resultado.ingreso_bruto_total == Decimal("3000000.0000")

    def test_nivel_arl_maximo_entre_contratos_rn08(
        self, parametros_2025, periodo_enero_2025, contrato_mes_completo
    ):
        """
        RN-08: Si hay contratos con nivel ARL I y ARL IV, aplica el nivel IV.
        """
        contrato_alto_riesgo = ContratoInput(
            id="c-arl-iv",
            entidad_contratante="Constructora Peligrosa",
            valor_bruto_mensual=Decimal("2000000"),
            nivel_arl=NivelARL.IV,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 31),
        )
        resultado = calcular_ibc_consolidado(
            [contrato_mes_completo, contrato_alto_riesgo],
            parametros_2025,
            periodo_enero_2025,
        )
        assert resultado.nivel_arl_maximo == NivelARL.IV

    def test_sin_contratos_lanza_error(self, parametros_2025, periodo_enero_2025):
        with pytest.raises(ValueError, match="No hay contratos activos"):
            calcular_ibc_consolidado([], parametros_2025, periodo_enero_2025)
