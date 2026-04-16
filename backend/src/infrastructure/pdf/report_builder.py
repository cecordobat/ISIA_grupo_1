"""
Generador de reportes PDF para liquidaciones de período.

REGLA CRÍTICA: Este módulo solo importa stdlib + fpdf2 +
src.infrastructure.models.liquidacion_periodo.
NO importa SQLAlchemy, FastAPI, Pydantic ni asyncio.

Ref: RF-08, HU-07
"""
from __future__ import annotations

import io
from datetime import datetime, timezone
from decimal import Decimal

from fpdf import FPDF

from src.infrastructure.models.liquidacion_periodo import LiquidacionPeriodo

# Nombres de meses en español
_MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

# Dimensiones de página (A4 en mm)
_PAGE_W = 210
_MARGIN = 15
_COL_LABEL = 120
_COL_VALUE = _PAGE_W - 2 * _MARGIN - _COL_LABEL

# Altura de fila
_ROW_H = 8


def _fmt_cop(value: object) -> str:
    """Formatea un valor monetario en pesos colombianos."""
    try:
        dec = Decimal(str(value))
    except Exception:
        dec = Decimal("0")
    # Formato: $ 1,234,567.89
    negative = dec < 0
    abs_val = abs(dec)
    # Formatear con separadores de miles
    parts = f"{abs_val:,.2f}".split(".")
    formatted = f"$ {parts[0]}.{parts[1]}"
    return f"-{formatted}" if negative else formatted


def _periodo_label(periodo: str) -> str:
    """Convierte 'YYYY-MM' -> 'Enero 2025'."""
    try:
        anio, mes = periodo.split("-")
        return f"{_MESES.get(int(mes), mes)} {anio}"
    except Exception:
        return periodo


def generar_reporte_pdf(liquidacion: LiquidacionPeriodo) -> bytes:
    """
    Genera el reporte PDF de una liquidación de período.

    Args:
        liquidacion: Instancia ORM LiquidacionPeriodo con todos los campos cargados.
                     El campo 'liquidacion.perfil' debe estar disponible para el nombre.

    Returns:
        Contenido del PDF como bytes.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=_MARGIN, top=_MARGIN, right=_MARGIN)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ------------------------------------------------------------------
    # 1. ENCABEZADO
    # ------------------------------------------------------------------
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(
        w=_PAGE_W - 2 * _MARGIN,
        h=12,
        text="Motor de Cumplimiento Tributario",
        border=0,
        align="C",
        fill=True,
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", style="", size=9)
    pdf.set_fill_color(60, 60, 60)
    pdf.set_text_color(220, 220, 220)
    pdf.cell(
        w=_PAGE_W - 2 * _MARGIN,
        h=7,
        text="Reporte de Liquidacion de Aportes y Retencion en la Fuente",
        border=0,
        align="C",
        fill=True,
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    # Restablecer color de texto para el cuerpo
    pdf.set_text_color(0, 0, 0)

    # ------------------------------------------------------------------
    # 2. PERÍODO
    # ------------------------------------------------------------------
    periodo_label = _periodo_label(liquidacion.periodo)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(
        w=_PAGE_W - 2 * _MARGIN,
        h=9,
        text=f"Periodo: {periodo_label}",
        border=0,
        align="L",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    # ID de liquidación (referencia)
    pdf.set_font("Helvetica", style="", size=8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(
        w=_PAGE_W - 2 * _MARGIN,
        h=6,
        text=f"ID de liquidacion: {liquidacion.id}",
        border=0,
        align="L",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    # ------------------------------------------------------------------
    # Helpers para secciones de tabla
    # ------------------------------------------------------------------
    def section_title(title: str) -> None:
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(
            w=_PAGE_W - 2 * _MARGIN,
            h=7,
            text=f"  {title}",
            border=1,
            align="L",
            fill=True,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    def data_row(label: str, value: str, highlight: bool = False) -> None:
        pdf.set_font("Helvetica", style="", size=9)
        if highlight:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(
            w=_COL_LABEL,
            h=_ROW_H,
            text=f"  {label}",
            border="LBR",
            align="L",
            fill=highlight,
            new_x="RIGHT",
            new_y="TOP",
        )
        pdf.set_font("Helvetica", style="B", size=9)
        pdf.cell(
            w=_COL_VALUE,
            h=_ROW_H,
            text=f"{value}  ",
            border="LBR",
            align="R",
            fill=highlight,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    def total_row(label: str, value: str) -> None:
        pdf.set_font("Helvetica", style="B", size=9)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(
            w=_COL_LABEL,
            h=_ROW_H + 1,
            text=f"  {label}",
            border=1,
            align="L",
            fill=True,
            new_x="RIGHT",
            new_y="TOP",
        )
        pdf.cell(
            w=_COL_VALUE,
            h=_ROW_H + 1,
            text=f"{value}  ",
            border=1,
            align="R",
            fill=True,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    # ------------------------------------------------------------------
    # 3. RESUMEN IBC
    # ------------------------------------------------------------------
    section_title("Resumen del Ingreso Base de Cotizacion (IBC)")
    data_row("Ingreso Bruto Total", _fmt_cop(liquidacion.ingreso_bruto_total))
    data_row("Costos Presuntos", _fmt_cop(liquidacion.costos_presuntos), highlight=True)
    total_row("IBC Consolidado", _fmt_cop(liquidacion.ibc))
    pdf.ln(4)

    # ------------------------------------------------------------------
    # 4. APORTES AL SISTEMA DE SEGURIDAD SOCIAL (SGSSI)
    # ------------------------------------------------------------------
    section_title("Aportes al Sistema General de Seguridad Social Integral (SGSSI)")
    data_row("Aporte Salud (12.5%)", _fmt_cop(liquidacion.aporte_salud))
    data_row("Aporte Pension (16%)", _fmt_cop(liquidacion.aporte_pension), highlight=True)
    data_row(
        f"Aporte ARL (Nivel {liquidacion.nivel_arl_aplicado.value})",
        _fmt_cop(liquidacion.aporte_arl),
    )

    # Mostrar bandera BEPS si aplica
    opcion = liquidacion.opcion_piso_proteccion
    if hasattr(opcion, "value"):
        opcion_str = opcion.value
    else:
        opcion_str = str(opcion)

    if opcion_str == "BEPS":
        pdf.set_font("Helvetica", style="I", size=8)
        pdf.set_text_color(80, 80, 180)
        pdf.cell(
            w=_PAGE_W - 2 * _MARGIN,
            h=7,
            text="  * Opcion Piso de Proteccion Social: BEPS aplicado",
            border="LBR",
            align="L",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.set_text_color(0, 0, 0)

    # Total aportes
    total_aportes = (
        Decimal(str(liquidacion.aporte_salud))
        + Decimal(str(liquidacion.aporte_pension))
        + Decimal(str(liquidacion.aporte_arl))
    )
    total_row("Total Aportes SGSSI", _fmt_cop(total_aportes))
    pdf.ln(4)

    # ------------------------------------------------------------------
    # 5. RETENCIÓN EN LA FUENTE (Art. 383 E.T.)
    # ------------------------------------------------------------------
    section_title("Retencion en la Fuente (Art. 383 E.T.)")
    data_row("Base Gravable", _fmt_cop(liquidacion.base_gravable_retencion))
    total_row("Retencion Calculada", _fmt_cop(liquidacion.retencion_fuente))
    pdf.ln(4)

    # ------------------------------------------------------------------
    # 6. NETO ESTIMADO
    # ------------------------------------------------------------------
    neto = (
        Decimal(str(liquidacion.ingreso_bruto_total))
        - total_aportes
        - Decimal(str(liquidacion.retencion_fuente))
    )
    section_title("Neto Estimado")
    data_row("Ingreso Bruto Total", _fmt_cop(liquidacion.ingreso_bruto_total))
    data_row("(-) Total Aportes SGSSI", _fmt_cop(total_aportes), highlight=True)
    data_row("(-) Retencion en la Fuente", _fmt_cop(liquidacion.retencion_fuente))
    total_row("NETO ESTIMADO", _fmt_cop(neto))
    pdf.ln(6)

    # ------------------------------------------------------------------
    # 7. DISCLAIMER LEGAL
    # ------------------------------------------------------------------
    pdf.set_font("Helvetica", style="I", size=7)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        w=_PAGE_W - 2 * _MARGIN,
        h=5,
        text=(
            "AVISO LEGAL: Este documento es informativo y no constituye una declaracion oficial "
            "ante la DIAN, la UGPP ni ninguna entidad del Estado colombiano. "
            "Los valores presentados son estimativos y pueden variar segun circunstancias "
            "particulares del contribuyente. "
            "Consulte a un asesor tributario certificado antes de tomar decisiones financieras."
        ),
        border=1,
        align="J",
    )
    pdf.set_text_color(0, 0, 0)

    # ------------------------------------------------------------------
    # 8. PIE DE PÁGINA con timestamp
    # ------------------------------------------------------------------
    now_utc = datetime.now(tz=timezone.utc)
    timestamp_str = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

    pdf.ln(4)
    pdf.set_font("Helvetica", style="", size=7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(
        w=_PAGE_W - 2 * _MARGIN,
        h=5,
        text=f"Generado el: {timestamp_str}  |  Generado por Motor de Cumplimiento - ISIA Grupo 1",
        border=0,
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_text_color(0, 0, 0)

    # ------------------------------------------------------------------
    # Serializar a bytes
    # ------------------------------------------------------------------
    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
