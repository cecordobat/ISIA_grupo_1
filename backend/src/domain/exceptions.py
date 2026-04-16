"""
Excepciones tipadas del dominio.
Las excepciones CT-* son bloqueantes: impiden confirmar una liquidación.
Ref: context/invariantes.md INV-06, context/functional_requirements.md CT-01..CT-04
"""
from decimal import Decimal


class MotorCumplimientoError(Exception):
    """Base de todas las excepciones del dominio."""


# ─── Excepciones del Motor de Cálculo (Validaciones CT) ───────────────────────

class ValidationError(MotorCumplimientoError):
    """Violación de consistencia transversal. Bloquea la confirmación."""
    ct_code: str

    def __init__(self, message: str, ct_code: str) -> None:
        super().__init__(message)
        self.ct_code = ct_code


class ErrorCT01_IBCFueraDeRango(ValidationError):
    """CT-01: IBC < 1 SMMLV o IBC > 25 SMMLV. Ref: RN-01, RES-N01."""

    def __init__(self, ibc: Decimal, smmlv: Decimal) -> None:
        self.ibc = ibc
        self.smmlv = smmlv
        super().__init__(
            f"CT-01: IBC ${ibc:,.0f} fuera del rango permitido "
            f"[${smmlv:,.0f} – ${smmlv * 25:,.0f}]. "
            "Verifique sus ingresos y código CIIU.",
            ct_code="CT-01",
        )


class ErrorCT02_SumaAportesInconsistente(ValidationError):
    """CT-02: Σ(Salud + Pensión + ARL) difiere del cálculo directo en más de $1 COP."""

    def __init__(self, diferencia: Decimal) -> None:
        self.diferencia = diferencia
        super().__init__(
            f"CT-02: Inconsistencia en suma de aportes. Diferencia: ${diferencia}. "
            "Tolerancia máxima: $1.00 COP.",
            ct_code="CT-02",
        )


class ErrorCT03_BaseGravableIncorrecta(ValidationError):
    """CT-03: Base gravable retención ≠ Ingreso bruto − Salud − Pensión."""

    def __init__(self, calculada: Decimal, esperada: Decimal) -> None:
        self.calculada = calculada
        self.esperada = esperada
        super().__init__(
            f"CT-03: Base gravable ${calculada:,.2f} no coincide con el valor "
            f"esperado ${esperada:,.2f} (Ingreso − Salud − Pensión). Ref: Art. 383 E.T.",
            ct_code="CT-03",
        )


class ErrorCT04_ContratosInvalidosEnPeriodo(ValidationError):
    """CT-04: Contratos con fechas fuera del período participaron en el consolidado."""

    def __init__(self, contratos_excluidos: int) -> None:
        self.contratos_excluidos = contratos_excluidos
        super().__init__(
            f"CT-04: {contratos_excluidos} contrato(s) con fechas fuera del período "
            "fueron excluidos automáticamente del consolidado.",
            ct_code="CT-04",
        )


# ─── Excepciones de Negocio ────────────────────────────────────────────────────

class LiquidacionInmutableError(MotorCumplimientoError):
    """Intento de modificar o eliminar un LiquidacionPeriodo. Ref: INV-03."""

    def __init__(self, liquidacion_id: str) -> None:
        super().__init__(
            f"La liquidación {liquidacion_id} es inmutable (APPEND-ONLY). "
            "Para corregir, genere una liquidación rectificatoria."
        )


class PisoProteccionRequeridoError(MotorCumplimientoError):
    """El ingreso neto < 1 SMMLV y el usuario no eligió opción. Ref: RN-06."""

    def __init__(self) -> None:
        super().__init__(
            "Su ingreso neto es inferior a 1 SMMLV. "
            "Debe elegir entre Piso de Protección Social (BEPS) "
            "o cotizar sobre 1 SMMLV completo antes de continuar."
        )


class ContratistaNoEncontradoError(MotorCumplimientoError):
    def __init__(self, contratista_id: str) -> None:
        super().__init__(f"Contratista {contratista_id} no encontrado.")


class AccesoNoAutorizadoError(MotorCumplimientoError):
    def __init__(self) -> None:
        super().__init__("No tiene autorización para acceder a este recurso.")


class LiquidacionDuplicadaError(MotorCumplimientoError):
    """Ya existe una liquidación confirmada para el mismo período."""

    def __init__(self, contratista_id: str, periodo: str) -> None:
        super().__init__(
            f"Ya existe una liquidación para el contratista {contratista_id} "
            f"en el período {periodo}. Use liquidación rectificatoria si hay error."
        )
