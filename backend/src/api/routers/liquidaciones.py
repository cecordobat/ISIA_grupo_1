"""
Router de liquidaciones — el endpoint principal del sistema.
POST /liquidaciones/calcular
GET  /liquidaciones/historial/{perfil_id}
GET  /liquidaciones/{liquidacion_id}/pdf
"""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.dependencies import get_current_user
from src.application.services.liquidacion_service import LiquidacionService
from src.domain.enums import NivelARL, OpcionPisoProteccion
from src.domain.exceptions import (
    AccesoNoAutorizadoError,
    ContratistaNoEncontradoError,
    LiquidacionDuplicadaError,
    PisoProteccionRequeridoError,
)
from src.domain.exceptions import ValidationError as DomainValidationError
from src.engine.dtos import LiquidacionResult
from src.infrastructure.database import get_db
from src.infrastructure.models.liquidacion_periodo import LiquidacionPeriodo
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.pdf.report_builder import generar_reporte_pdf

router = APIRouter(prefix="/liquidaciones", tags=["liquidaciones"])


class LiquidacionRequest(BaseModel):
    perfil_id: str
    anio: int
    mes: int
    opcion_piso: OpcionPisoProteccion | None = None


class LiquidacionResponse(BaseModel):
    model_config = ConfigDict(json_encoders={Decimal: str})

    liquidacion_id: str
    periodo: str
    ingreso_bruto_total: str
    ibc: str
    aporte_salud: str
    aporte_pension: str
    aporte_arl: str
    nivel_arl_aplicado: NivelARL
    total_aportes: str
    base_gravable_retencion: str
    retencion_fuente: str
    opcion_piso_proteccion: OpcionPisoProteccion
    neto_estimado: str
    ajustado_por_tope: bool


def _resultado_a_response(
    resultado: LiquidacionResult,
    liquidacion_id: str,
) -> LiquidacionResponse:
    return LiquidacionResponse(
        liquidacion_id=liquidacion_id,
        periodo=resultado.periodo.codigo,
        ingreso_bruto_total=str(resultado.ingreso_bruto_total),
        ibc=str(resultado.ibc),
        aporte_salud=str(resultado.aporte_salud),
        aporte_pension=str(resultado.aporte_pension),
        aporte_arl=str(resultado.aporte_arl),
        nivel_arl_aplicado=resultado.aportes_result.nivel_arl_aplicado,
        total_aportes=str(resultado.total_aportes),
        base_gravable_retencion=str(resultado.retencion_result.base_gravable),
        retencion_fuente=str(resultado.retencion_fuente),
        opcion_piso_proteccion=resultado.opcion_piso_proteccion,
        neto_estimado=str(resultado.neto_estimado),
        ajustado_por_tope=resultado.ibc_result.ajustado_por_tope,
    )


@router.post("/calcular", response_model=LiquidacionResponse, status_code=status.HTTP_201_CREATED)
async def calcular_liquidacion(
    body: LiquidacionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LiquidacionResponse:
    """
    Ejecuta el flujo completo de liquidación.
    Requiere autenticación JWT.
    """
    service = LiquidacionService(db)
    try:
        resultado, liquidacion = await service.ejecutar_liquidacion(
            perfil_id=body.perfil_id,
            usuario_id=current_user.id,
            anio=body.anio,
            mes=body.mes,
            opcion_piso=body.opcion_piso,
        )
    except ContratistaNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccesoNoAutorizadoError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LiquidacionDuplicadaError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PisoProteccionRequeridoError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": str(e), "requires_piso_decision": True},
        )
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"ct_code": e.ct_code, "message": str(e)},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return _resultado_a_response(resultado, liquidacion.id)


@router.get("/historial/{perfil_id}", response_model=list[dict])
async def historial(
    perfil_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Retorna el historial de liquidaciones del contratista."""
    service = LiquidacionService(db)
    try:
        liquidaciones = await service.obtener_historial(perfil_id, current_user.id)
    except (ContratistaNoEncontradoError, AccesoNoAutorizadoError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return [
        {
            "id": liq.id,
            "periodo": liq.periodo,
            "ibc": str(liq.ibc),
            "total_aportes": str(
                Decimal(str(liq.aporte_salud))
                + Decimal(str(liq.aporte_pension))
                + Decimal(str(liq.aporte_arl))
            ),
            "retencion_fuente": str(liq.retencion_fuente),
            "generado_en": liq.generado_en.isoformat(),
        }
        for liq in liquidaciones
    ]


@router.get("/{liquidacion_id}/pdf")
async def descargar_pdf(
    liquidacion_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Genera y descarga el reporte PDF de una liquidación específica.
    Requiere autenticación JWT. Solo el dueño del perfil puede descargar su reporte.
    Ref: RF-08, HU-07
    """
    # Cargar la liquidación junto con su perfil (para verificar propiedad)
    result = await db.execute(
        select(LiquidacionPeriodo)
        .where(LiquidacionPeriodo.id == liquidacion_id)
        .options(selectinload(LiquidacionPeriodo.perfil))
    )
    liquidacion: LiquidacionPeriodo | None = result.scalar_one_or_none()

    if liquidacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Liquidación '{liquidacion_id}' no encontrada.",
        )

    # Verificar que la liquidación pertenece al usuario autenticado
    if liquidacion.perfil.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a esta liquidación.",
        )

    pdf_bytes = generar_reporte_pdf(liquidacion)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=liquidacion_{liquidacion_id}.pdf"
        },
    )
