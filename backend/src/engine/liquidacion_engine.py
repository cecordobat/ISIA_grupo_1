"""
Orquestador del Motor de Liquidación.

Implementa el flujo OBLIGATORIO E IRROMPIBLE de 10 pasos (INV-05).
Esta función es la única interfaz pública del engine.

CONTRATO DE INTERFAZ (INV-02):
    resultado = calcular(contratos, parametros, periodo, opcion_piso)

GARANTÍAS:
    - Función pura: mismos inputs → mismo resultado (INV-03, RES-C04)
    - Sin efectos secundarios: no toca BD, APIs ni estado global (INV-02)
    - Orden de cálculo irrompible (INV-05)
    - Solo Decimal con ROUND_HALF_UP (INV-01)

Ref: context/invariantes.md INV-02, INV-05
     context/functional_requirements.md RF-03..RF-09
"""
from src.domain.enums import OpcionPisoProteccion
from src.domain.exceptions import ErrorCT04_ContratosInvalidosEnPeriodo
from src.engine.aporte_calculator import calcular_aportes
from src.engine.dtos import (
    ContratoInput,
    LiquidacionResult,
    ParametrosNormativosDTO,
    PeriodoLiquidacion,
)
from src.engine.ibc_calculator import calcular_ibc_consolidado
from src.engine.piso_proteccion import evaluar_piso_proteccion
from src.engine.retencion_calculator import calcular_retencion
from src.engine.validations import (
    filtrar_contratos_por_periodo,
    validar_ct01_ibc_rango,
    validar_ct02_suma_aportes,
    validar_ct03_base_gravable,
)


def calcular(
    contratos: list[ContratoInput],
    parametros: ParametrosNormativosDTO,
    periodo: PeriodoLiquidacion,
    opcion_piso: OpcionPisoProteccion | None = None,
) -> LiquidacionResult:
    """
    Ejecuta el flujo completo de liquidación en el orden obligatorio.

    Orden de ejecución (INV-05):
      Paso 1:  CT-04 — Filtrar contratos por período
      Paso 2:  RF-03 — Consolidar ingresos brutos con proporcionalidad (RN-04, RN-05)
      Paso 3:  RF-04 — Costos presuntos CIIU + Regla del 40% = IBC (RN-01, RN-02)
      Paso 4:  CT-01 — Validar IBC en rango [1 SMMLV, 25 SMMLV]
      Paso 5:  RF-05 — Evaluación Piso de Protección Social (RN-06)
      Paso 6:  RF-06 — Aportes: Salud + Pensión + ARL (RN-03, RN-08)
      Paso 7:  CT-02 — Verificar Σ(Aportes) ≈ IBC × tasas (tol. ≤ $1 COP)
      Paso 8:  RF-07 — Depuración base gravable (RN-07, Art. 383 E.T.)
      Paso 9:  CT-03 — Verificar base = Ingreso − Salud − Pensión
      Paso 10: Ensamblar y retornar LiquidacionResult

    Args:
        contratos: Todos los contratos del contratista (incluye los de otros períodos;
                   el paso 1 filtra los que no aplican).
        parametros: SnapshotNormativo vigente para el período.
        periodo: Período mensual de liquidación.
        opcion_piso: Decisión del usuario sobre Piso de Protección Social.
                     Obligatoria si ingreso < 1 SMMLV.

    Returns:
        LiquidacionResult completo e inmutable.

    Raises:
        ErrorCT01_IBCFueraDeRango: IBC fuera del rango legal (bloqueante).
        ErrorCT02_SumaAportesInconsistente: Inconsistencia aritmética (bloqueante).
        ErrorCT03_BaseGravableIncorrecta: Base gravable incorrecta (bloqueante).
        PisoProteccionRequeridoError: Ingreso < SMMLV sin opción elegida.
        ValueError: No hay contratos activos en el período.
    """
    # ── Paso 1: CT-04 — Filtrar contratos por período ──────────────────────────
    contratos_activos, excluidos = filtrar_contratos_por_periodo(contratos, periodo)

    if excluidos > 0:
        # CT-04 es advertencia, no bloqueante, pero se registra en el resultado
        # El servicio decidirá si notificar al usuario
        pass  # los contratos ya fueron filtrados

    if not contratos_activos:
        raise ValueError(
            f"No hay contratos activos en el período {periodo.codigo}. "
            f"Se excluyeron {excluidos} contrato(s) por fechas fuera del período."
        )

    # ── Pasos 2-3: RF-03, RF-04 — IBC consolidado ─────────────────────────────
    ibc_result = calcular_ibc_consolidado(contratos_activos, parametros, periodo)

    # ── Paso 4: CT-01 — Validar IBC en rango ──────────────────────────────────
    validar_ct01_ibc_rango(ibc_result, parametros)

    # ── Paso 5: RF-05 — Piso de Protección Social ─────────────────────────────
    opcion_piso_efectiva = evaluar_piso_proteccion(
        ibc_result.ingreso_bruto_total, parametros.smmlv, opcion_piso
    )

    # ── Pasos 6: RF-06 — Aportes SGSSI ────────────────────────────────────────
    aportes_result = calcular_aportes(ibc_result, parametros, opcion_piso_efectiva)

    # ── Paso 7: CT-02 — Consistencia de aportes ───────────────────────────────
    # Solo valida en régimen ordinario (BEPS tiene lógica diferente)
    if opcion_piso_efectiva != OpcionPisoProteccion.BEPS:
        validar_ct02_suma_aportes(aportes_result, ibc_result, parametros)

    # ── Pasos 8-9: RF-07, CT-03 — Retención en la fuente ──────────────────────
    retencion_result = calcular_retencion(
        ibc_result.ingreso_bruto_total, aportes_result, parametros
    )
    validar_ct03_base_gravable(
        retencion_result, ibc_result.ingreso_bruto_total, aportes_result
    )

    # ── Paso 10: Ensamblar resultado ───────────────────────────────────────────
    return LiquidacionResult(
        periodo=periodo,
        ibc_result=ibc_result,
        opcion_piso_proteccion=opcion_piso_efectiva,
        aportes_result=aportes_result,
        retencion_result=retencion_result,
    )
