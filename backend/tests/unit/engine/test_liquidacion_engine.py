"""
Tests del motor de liquidación completo (flujo INV-05).

Estos son los tests más importantes del sistema. Verifican el pipeline completo
con escenarios realistas basados en los casos de la UGPP.
"""
from datetime import date
from decimal import Decimal

import pytest

from src.domain.enums import NivelARL, OpcionPisoProteccion
from src.domain.exceptions import (
    PisoProteccionRequeridoError,
)
from src.engine.dtos import ContratoInput
from src.engine.liquidacion_engine import calcular


class TestEscenariosUGPP:
    """Escenarios reales de la UGPP para validar el motor completo."""

    def test_escenario_base_un_contrato_mes_completo(
        self, parametros_2025, periodo_enero_2025, contrato_mes_completo
    ):
        """
        Escenario canónico: 1 contrato $5.000.000, CIIU 6201, enero 2025.

        Resultado esperado:
          IBC = $1.460.000
          Salud = $1.460.000 × 12.5% = $182.500
          Pensión = $1.460.000 × 16% = $233.600
          ARL (I) = $1.460.000 × 0.522% = $7.621.20 → $7.621.00 aprox
          Base retención = $5.000.000 − $182.500 − $233.600 = $4.583.900
        """
        resultado = calcular(
            contratos=[contrato_mes_completo],
            parametros=parametros_2025,
            periodo=periodo_enero_2025,
        )

        assert resultado.ibc == Decimal("1460000.0000")
        assert resultado.aporte_salud == Decimal("182500.00")
        assert resultado.aporte_pension == Decimal("233600.00")
        assert resultado.opcion_piso_proteccion == OpcionPisoProteccion.NO_APLICA
        # La base gravable debe ser ingreso - salud - pensión
        assert resultado.retencion_result.base_gravable == (
            Decimal("5000000.0000") - Decimal("182500.00") - Decimal("233600.00")
        )

    def test_escenario_piso_proteccion_beps(self, parametros_2025, periodo_enero_2025):
        """
        Contratista con ingreso $800.000 (< 1 SMMLV $1.423.500).
        Elige BEPS → aporte = $800.000 × 15% = $120.000
        """
        contrato_bajo = ContratoInput(
            id="c-bajo",
            entidad_contratante="Microempresa",
            valor_bruto_mensual=Decimal("800000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 31),
        )
        resultado = calcular(
            contratos=[contrato_bajo],
            parametros=parametros_2025,
            periodo=periodo_enero_2025,
            opcion_piso=OpcionPisoProteccion.BEPS,
        )
        assert resultado.opcion_piso_proteccion == OpcionPisoProteccion.BEPS
        assert resultado.aporte_pension == Decimal("120000.00")  # 800.000 × 15%
        assert resultado.aporte_salud == Decimal("0.00")
        assert resultado.aporte_arl == Decimal("0.00")

    def test_escenario_piso_proteccion_sin_opcion_lanza_error(
        self, parametros_2025, periodo_enero_2025
    ):
        """Si ingreso < SMMLV y no se elige opción, el motor debe bloquearse."""
        contrato_bajo = ContratoInput(
            id="c-bajo",
            entidad_contratante="Microempresa",
            valor_bruto_mensual=Decimal("800000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 31),
        )
        with pytest.raises(PisoProteccionRequeridoError):
            calcular(
                contratos=[contrato_bajo],
                parametros=parametros_2025,
                periodo=periodo_enero_2025,
                opcion_piso=None,  # usuario no eligió
            )

    def test_escenario_dos_contratos_consolidacion_rn04(
        self, parametros_2025, periodo_enero_2025, contrato_mes_completo
    ):
        """
        RN-04: El IBC se calcula sobre la suma de ambos contratos.
        Contrato 1: $5.000.000 (mes completo)
        Contrato 2: $3.000.000 × 16/30 (medio mes)
        Total: $5.000.000 + $1.600.000 = $6.600.000
        Costos 27%: $1.782.000
        Base neta: $4.818.000
        40%: $1.927.200 (dentro del rango)
        """
        contrato2 = ContratoInput(
            id="c2",
            entidad_contratante="Segunda empresa",
            valor_bruto_mensual=Decimal("3000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 16),
            fecha_fin=date(2025, 1, 31),
        )
        resultado = calcular(
            contratos=[contrato_mes_completo, contrato2],
            parametros=parametros_2025,
            periodo=periodo_enero_2025,
        )
        # IBC consolidado, no por separado
        assert resultado.ibc == Decimal("1927200.0000")

    def test_escenario_ingreso_alto_tope_25_smmlv(
        self, parametros_2025, periodo_enero_2025
    ):
        """
        Ingreso muy alto: IBC se topa a 25 SMMLV = $35.587.500.
        """
        contrato_alto = ContratoInput(
            id="c-alto",
            entidad_contratante="Empresa Multinacional",
            valor_bruto_mensual=Decimal("150000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 31),
        )
        resultado = calcular(
            contratos=[contrato_alto],
            parametros=parametros_2025,
            periodo=periodo_enero_2025,
        )
        assert resultado.ibc == Decimal("35587500")
        assert resultado.ibc_result.ajustado_por_tope is True

    def test_contrato_fuera_del_periodo_se_excluye_ct04(
        self, parametros_2025, periodo_enero_2025, contrato_mes_completo
    ):
        """CT-04: El contrato de diciembre no debe participar en enero."""
        contrato_dic = ContratoInput(
            id="c-dic",
            entidad_contratante="Empresa Dec",
            valor_bruto_mensual=Decimal("10000000"),
            nivel_arl=NivelARL.I,
            fecha_inicio=date(2024, 12, 1),
            fecha_fin=date(2024, 12, 31),
        )
        # Solo contrato_mes_completo ($5M) debe participar, no el de diciembre ($10M)
        resultado = calcular(
            contratos=[contrato_mes_completo, contrato_dic],
            parametros=parametros_2025,
            periodo=periodo_enero_2025,
        )
        assert resultado.ingreso_bruto_total == Decimal("5000000.0000")

    def test_neto_estimado_es_correcto(
        self, parametros_2025, periodo_enero_2025, contrato_mes_completo
    ):
        """neto_estimado = ingreso − total_aportes − retención."""
        resultado = calcular(
            contratos=[contrato_mes_completo],
            parametros=parametros_2025,
            periodo=periodo_enero_2025,
        )
        neto_calculado = (
            resultado.ingreso_bruto_total
            - resultado.total_aportes
            - resultado.retencion_fuente
        )
        assert resultado.neto_estimado == neto_calculado

    def test_motor_es_idempotente_inv03(
        self, parametros_2025, periodo_enero_2025, contrato_mes_completo
    ):
        """
        INV-03: Ejecutar el motor dos veces con los mismos inputs produce el mismo resultado.
        """
        resultado1 = calcular(
            contratos=[contrato_mes_completo],
            parametros=parametros_2025,
            periodo=periodo_enero_2025,
        )
        resultado2 = calcular(
            contratos=[contrato_mes_completo],
            parametros=parametros_2025,
            periodo=periodo_enero_2025,
        )
        assert resultado1.ibc == resultado2.ibc
        assert resultado1.aporte_salud == resultado2.aporte_salud
        assert resultado1.aporte_pension == resultado2.aporte_pension
        assert resultado1.retencion_fuente == resultado2.retencion_fuente
