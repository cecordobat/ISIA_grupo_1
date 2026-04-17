from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, field_serializer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.dependencies import get_current_user
from src.api.schemas.comparacion import ComparacionResponse, DiferenciasComparacion, LiquidacionResumen
from src.application.services.liquidacion_service import LiquidacionEjecutada, LiquidacionService
from src.domain.enums import NivelARL, OpcionPisoProteccion, RolUsuario
from src.domain.exceptions import (
    AccesoNoAutorizadoError,
    ContratistaNoEncontradoError,
    LiquidacionDuplicadaError,
    PisoProteccionRequeridoError,
)
from src.domain.exceptions import ValidationError as DomainValidationError
from src.engine.dtos import ContratoInput, LiquidacionResult, ParametrosNormativosDTO
from src.infrastructure.database import get_db
from src.infrastructure.models.liquidacion_periodo import LiquidacionPeriodo
from src.infrastructure.models.perfil_contratista import PerfilContratista
from src.infrastructure.models.snapshot_normativo import SnapshotNormativo
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.pdf.report_builder import generar_reporte_pdf
from src.infrastructure.repositories.acceso_contador_repo import AccesoContadorRepository
from src.infrastructure.repositories.liquidacion_confirmacion_repo import (
    LiquidacionConfirmacionRepository,
)

router = APIRouter(prefix="/liquidaciones", tags=["liquidaciones"])


async def _puede_ver_perfil(
    perfil_id: str,
    current_user: Usuario,
    db: AsyncSession,
) -> bool:
    perfil = await db.scalar(select(PerfilContratista).where(PerfilContratista.id == perfil_id))
    if perfil is None:
        return False
    if perfil.usuario_id == current_user.id:
        return True
    if current_user.rol == RolUsuario.CONTADOR:
        repo = AccesoContadorRepository(db)
        return await repo.contador_tiene_acceso(current_user.id, perfil_id)
    return False


class LiquidacionRequest(BaseModel):
    perfil_id: str
    anio: int
    mes: int
    opcion_piso: OpcionPisoProteccion | None = None


class ContratoConsideradoResponse(BaseModel):
    contrato_id: str
    entidad_contratante: str
    valor_bruto_mensual: str
    dias_cotizados: int
    ingreso_bruto_proporcional: str
    nivel_arl: NivelARL


class SnapshotNormativoResponse(BaseModel):
    smmlv: str
    uvt: str
    pct_salud: str
    pct_pension: str
    pct_costos_presuntos: str
    tarifas_arl: dict[str, str]
    vigencia_anio: int


class RevisionResponse(BaseModel):
    contador_id: str
    nota: str
    aprobada: bool
    revisado_en: str


class ConfirmacionResponse(BaseModel):
    usuario_id: str
    confirmado_en: str


class LiquidacionResponse(BaseModel):
    liquidacion_id: str
    periodo: str
    ingreso_bruto_total: str
    costos_presuntos: str
    pct_costos_presuntos: str
    base_40_pct: str
    ibc: str
    aporte_salud: str
    aporte_pension: str
    aporte_arl: str
    nivel_arl_aplicado: NivelARL
    tarifa_arl_aplicada: str
    total_aportes: str
    base_gravable_retencion: str
    retencion_fuente: str
    opcion_piso_proteccion: OpcionPisoProteccion
    neto_estimado: str
    ajustado_por_tope: bool
    contratos_considerados: list[ContratoConsideradoResponse]
    snapshot_normativo: SnapshotNormativoResponse
    revision: RevisionResponse | None = None
    confirmacion: ConfirmacionResponse | None = None
    requiere_revision_contador: bool
    puede_confirmar: bool

    @field_serializer(
        "ingreso_bruto_total",
        "costos_presuntos",
        "pct_costos_presuntos",
        "base_40_pct",
        "ibc",
        "aporte_salud",
        "aporte_pension",
        "aporte_arl",
        "tarifa_arl_aplicada",
        "total_aportes",
        "base_gravable_retencion",
        "retencion_fuente",
        "neto_estimado",
    )
    def serialize_decimal_fields(self, value: Decimal) -> str:
        return str(value)


class HistorialItemResponse(BaseModel):
    id: str
    periodo: str
    ibc: str
    total_aportes: str
    retencion_fuente: str
    generado_en: str
    opcion_piso_proteccion: OpcionPisoProteccion
    estado_proceso: str


class AniosDisponiblesResponse(BaseModel):
    anios: list[int]


class LiquidacionDetalleResponse(BaseModel):
    id: str
    periodo: str
    ingreso_bruto_total: str
    costos_presuntos: str
    pct_costos_presuntos: str
    base_40_pct: str
    ibc: str
    aporte_salud: str
    aporte_pension: str
    aporte_arl: str
    nivel_arl_aplicado: NivelARL
    total_aportes: str
    base_gravable_retencion: str
    retencion_fuente: str
    neto_estimado: str
    opcion_piso_proteccion: OpcionPisoProteccion
    generado_en: str
    snapshot_normativo: SnapshotNormativoResponse
    revision: RevisionResponse | None = None
    confirmacion: ConfirmacionResponse | None = None
    requiere_revision_contador: bool
    puede_confirmar: bool
    estado_proceso: str

    @field_serializer(
        "ingreso_bruto_total",
        "costos_presuntos",
        "pct_costos_presuntos",
        "base_40_pct",
        "ibc",
        "aporte_salud",
        "aporte_pension",
        "aporte_arl",
        "total_aportes",
        "base_gravable_retencion",
        "retencion_fuente",
        "neto_estimado",
    )
    def serialize_decimal_fields(self, value: Decimal) -> str:
        return str(value)


def _revision_response(liquidacion: LiquidacionPeriodo) -> RevisionResponse | None:
    if liquidacion.revision is None:
        return None
    return RevisionResponse(
        contador_id=liquidacion.revision.contador_id,
        nota=liquidacion.revision.nota,
        aprobada=liquidacion.revision.aprobada,
        revisado_en=liquidacion.revision.revisado_en.isoformat(),
    )


def _confirmacion_response(liquidacion: LiquidacionPeriodo) -> ConfirmacionResponse | None:
    if liquidacion.confirmacion is None:
        return None
    return ConfirmacionResponse(
        usuario_id=liquidacion.confirmacion.usuario_id,
        confirmado_en=liquidacion.confirmacion.confirmado_en.isoformat(),
    )


def _estado_proceso(liquidacion: LiquidacionPeriodo, requiere_revision_contador: bool) -> str:
    if liquidacion.confirmacion is not None:
        return "CONFIRMADA"
    if liquidacion.revision is not None:
        return "REVISADA"
    if requiere_revision_contador:
        return "PENDIENTE_REVISION"
    return "PENDIENTE_CONFIRMACION"


def _snapshot_response(parametros: ParametrosNormativosDTO) -> SnapshotNormativoResponse:
    return SnapshotNormativoResponse(
        smmlv=str(parametros.smmlv),
        uvt=str(parametros.uvt),
        pct_salud=str(parametros.pct_salud),
        pct_pension=str(parametros.pct_pension),
        pct_costos_presuntos=str(parametros.pct_costos_presuntos),
        tarifas_arl={nivel.value: str(valor) for nivel, valor in parametros.tarifas_arl.items()},
        vigencia_anio=parametros.vigencia_anio,
    )


def _contratos_response(
    resultado: LiquidacionResult,
    contratos: list[ContratoInput],
) -> list[ContratoConsideradoResponse]:
    contratos_por_id = {contrato.id: contrato for contrato in contratos}
    return [
        ContratoConsideradoResponse(
            contrato_id=item.contrato_id,
            entidad_contratante=contratos_por_id[item.contrato_id].entidad_contratante,
            valor_bruto_mensual=str(contratos_por_id[item.contrato_id].valor_bruto_mensual),
            dias_cotizados=item.dias_cotizados,
            ingreso_bruto_proporcional=str(item.ingreso_bruto_proporcional),
            nivel_arl=contratos_por_id[item.contrato_id].nivel_arl,
        )
        for item in resultado.ibc_result.contratos_calculados
        if item.contrato_id in contratos_por_id
    ]


async def _resultado_a_response(
    ejecucion: LiquidacionEjecutada,
    db: AsyncSession,
) -> LiquidacionResponse:
    resultado = ejecucion.resultado
    parametros = ejecucion.parametros
    acceso_repo = AccesoContadorRepository(db)
    accesos_contador = await acceso_repo.contar_por_perfil(ejecucion.liquidacion.perfil_id)
    requiere_revision_contador = accesos_contador > 0
    return LiquidacionResponse(
        liquidacion_id=ejecucion.liquidacion.id,
        periodo=resultado.periodo.codigo,
        ingreso_bruto_total=str(resultado.ingreso_bruto_total),
        costos_presuntos=str(resultado.ibc_result.costos_presuntos),
        pct_costos_presuntos=str(parametros.pct_costos_presuntos),
        base_40_pct=str(resultado.ibc_result.base_40_pct),
        ibc=str(resultado.ibc),
        aporte_salud=str(resultado.aporte_salud),
        aporte_pension=str(resultado.aporte_pension),
        aporte_arl=str(resultado.aporte_arl),
        nivel_arl_aplicado=resultado.aportes_result.nivel_arl_aplicado,
        tarifa_arl_aplicada=str(resultado.aportes_result.tarifa_arl_aplicada),
        total_aportes=str(resultado.total_aportes),
        base_gravable_retencion=str(resultado.retencion_result.base_gravable),
        retencion_fuente=str(resultado.retencion_fuente),
        opcion_piso_proteccion=resultado.opcion_piso_proteccion,
        neto_estimado=str(resultado.neto_estimado),
        ajustado_por_tope=resultado.ibc_result.ajustado_por_tope,
        contratos_considerados=_contratos_response(resultado, ejecucion.contratos),
        snapshot_normativo=_snapshot_response(parametros),
        revision=None,
        confirmacion=None,
        requiere_revision_contador=requiere_revision_contador,
        puede_confirmar=not requiere_revision_contador,
    )


async def _detalle_historico_response(
    liquidacion: LiquidacionPeriodo,
    db: AsyncSession,
) -> LiquidacionDetalleResponse:
    ingreso_bruto_total = Decimal(str(liquidacion.ingreso_bruto_total))
    costos_presuntos = Decimal(str(liquidacion.costos_presuntos))
    aporte_salud = Decimal(str(liquidacion.aporte_salud))
    aporte_pension = Decimal(str(liquidacion.aporte_pension))
    aporte_arl = Decimal(str(liquidacion.aporte_arl))
    retencion_fuente = Decimal(str(liquidacion.retencion_fuente))
    total_aportes = aporte_salud + aporte_pension + aporte_arl
    neto_estimado = ingreso_bruto_total - total_aportes - retencion_fuente
    base_40_pct = (ingreso_bruto_total - costos_presuntos) * Decimal("0.40")
    pct_costos_presuntos = (
        (costos_presuntos / ingreso_bruto_total).quantize(Decimal("0.0001"))
        if ingreso_bruto_total > 0
        else Decimal("0.0000")
    )

    snapshot = liquidacion.snapshot
    acceso_repo = AccesoContadorRepository(db)
    requiere_revision_contador = await acceso_repo.contar_por_perfil(liquidacion.perfil_id) > 0
    tarifas_arl = {}
    if snapshot is not None:
        import json

        tarifas_arl = {k: str(v) for k, v in json.loads(snapshot.tabla_arl_json).items()}

    return LiquidacionDetalleResponse(
        id=liquidacion.id,
        periodo=liquidacion.periodo,
        ingreso_bruto_total=str(liquidacion.ingreso_bruto_total),
        costos_presuntos=str(liquidacion.costos_presuntos),
        pct_costos_presuntos=str(pct_costos_presuntos),
        base_40_pct=str(base_40_pct.quantize(Decimal("0.0001"))),
        ibc=str(liquidacion.ibc),
        aporte_salud=str(liquidacion.aporte_salud),
        aporte_pension=str(liquidacion.aporte_pension),
        aporte_arl=str(liquidacion.aporte_arl),
        nivel_arl_aplicado=liquidacion.nivel_arl_aplicado,
        total_aportes=str(total_aportes),
        base_gravable_retencion=str(liquidacion.base_gravable_retencion),
        retencion_fuente=str(liquidacion.retencion_fuente),
        neto_estimado=str(neto_estimado),
        opcion_piso_proteccion=liquidacion.opcion_piso_proteccion,
        generado_en=liquidacion.generado_en.isoformat(),
        snapshot_normativo=SnapshotNormativoResponse(
            smmlv=str(snapshot.smmlv),
            uvt=str(snapshot.uvt),
            pct_salud=str(snapshot.pct_salud),
            pct_pension=str(snapshot.pct_pension),
            pct_costos_presuntos=str(pct_costos_presuntos),
            tarifas_arl=tarifas_arl,
            vigencia_anio=snapshot.vigencia_anio,
        ),
        revision=_revision_response(liquidacion),
        confirmacion=_confirmacion_response(liquidacion),
        requiere_revision_contador=requiere_revision_contador,
        puede_confirmar=(not requiere_revision_contador) or liquidacion.revision is not None,
        estado_proceso=_estado_proceso(liquidacion, requiere_revision_contador),
    )


@router.post("/calcular", response_model=LiquidacionResponse, status_code=status.HTTP_201_CREATED)
async def calcular_liquidacion(
    body: LiquidacionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LiquidacionResponse:
    service = LiquidacionService(db)
    try:
        ejecucion = await service.ejecutar_liquidacion(
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

    return await _resultado_a_response(ejecucion, db)


@router.get("/anios-disponibles", response_model=AniosDisponiblesResponse)
async def anios_disponibles(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AniosDisponiblesResponse:
    _ = current_user
    rows = await db.execute(
        select(SnapshotNormativo.vigencia_anio).order_by(SnapshotNormativo.vigencia_anio.desc())
    )
    return AniosDisponiblesResponse(anios=list(rows.scalars().all()))


@router.get("/historial/{perfil_id}", response_model=list[HistorialItemResponse])
async def historial(
    perfil_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[HistorialItemResponse]:
    if not await _puede_ver_perfil(perfil_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para consultar el historial de este perfil.",
        )

    result = await db.execute(
        select(LiquidacionPeriodo)
        .where(LiquidacionPeriodo.perfil_id == perfil_id)
        .options(
            selectinload(LiquidacionPeriodo.revision),
            selectinload(LiquidacionPeriodo.confirmacion),
        )
        .order_by(LiquidacionPeriodo.periodo.desc())
    )
    liquidaciones = list(result.scalars().all())

    acceso_repo = AccesoContadorRepository(db)
    requiere_revision_contador = await acceso_repo.contar_por_perfil(perfil_id) > 0

    return [
        HistorialItemResponse(
            id=liq.id,
            periodo=liq.periodo,
            ibc=str(liq.ibc),
            total_aportes=str(
                Decimal(str(liq.aporte_salud))
                + Decimal(str(liq.aporte_pension))
                + Decimal(str(liq.aporte_arl))
            ),
            retencion_fuente=str(liq.retencion_fuente),
            generado_en=liq.generado_en.isoformat(),
            opcion_piso_proteccion=liq.opcion_piso_proteccion,
            estado_proceso=_estado_proceso(liq, requiere_revision_contador),
        )
        for liq in liquidaciones
    ]


@router.get("/comparar", response_model=ComparacionResponse)
async def comparar_periodos(
    periodo_a: str,
    periodo_b: str,
    perfil_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ComparacionResponse:
    """
    Compara dos liquidaciones de distintos períodos para un perfil.
    Solo el contratista dueño o su contador autorizado puede comparar.
    Ref: RF-12, HU-13, INV-03
    """
    if not await _puede_ver_perfil(perfil_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para consultar las liquidaciones de este perfil.",
        )

    result = await db.execute(
        select(LiquidacionPeriodo)
        .where(LiquidacionPeriodo.perfil_id == perfil_id)
        .order_by(LiquidacionPeriodo.periodo.desc())
    )
    todas = list(result.scalars().all())
    mapa = {liq.periodo: liq for liq in todas}

    liq_a = mapa.get(periodo_a)
    liq_b = mapa.get(periodo_b)

    faltantes = [p for p, l in [(periodo_a, liq_a), (periodo_b, liq_b)] if l is None]
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existen liquidaciones para los períodos: {', '.join(faltantes)}",
        )

    def _resumen(liq: LiquidacionPeriodo) -> LiquidacionResumen:
        return LiquidacionResumen(
            periodo=liq.periodo,
            ingreso_bruto_total=float(liq.ingreso_bruto_total),
            ibc=float(liq.ibc),
            aporte_salud=float(liq.aporte_salud),
            aporte_pension=float(liq.aporte_pension),
            aporte_arl=float(liq.aporte_arl),
            retencion_fuente=float(liq.retencion_fuente),
            base_gravable_retencion=float(liq.base_gravable_retencion),
        )

    resumen_a = _resumen(liq_a)  # type: ignore[arg-type]
    resumen_b = _resumen(liq_b)  # type: ignore[arg-type]

    diferencias = DiferenciasComparacion(
        ingreso_bruto_total=resumen_b.ingreso_bruto_total - resumen_a.ingreso_bruto_total,
        ibc=resumen_b.ibc - resumen_a.ibc,
        aporte_salud=resumen_b.aporte_salud - resumen_a.aporte_salud,
        aporte_pension=resumen_b.aporte_pension - resumen_a.aporte_pension,
        aporte_arl=resumen_b.aporte_arl - resumen_a.aporte_arl,
        retencion_fuente=resumen_b.retencion_fuente - resumen_a.retencion_fuente,
        base_gravable_retencion=resumen_b.base_gravable_retencion - resumen_a.base_gravable_retencion,
    )

    return ComparacionResponse(periodo_a=resumen_a, periodo_b=resumen_b, diferencias=diferencias)


@router.get("/{liquidacion_id}", response_model=LiquidacionDetalleResponse)
async def obtener_liquidacion(
    liquidacion_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LiquidacionDetalleResponse:
    result = await db.execute(
        select(LiquidacionPeriodo)
        .where(LiquidacionPeriodo.id == liquidacion_id)
        .options(
            selectinload(LiquidacionPeriodo.perfil),
            selectinload(LiquidacionPeriodo.snapshot),
            selectinload(LiquidacionPeriodo.revision),
            selectinload(LiquidacionPeriodo.confirmacion),
        )
    )
    liquidacion = result.scalar_one_or_none()

    if liquidacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Liquidacion '{liquidacion_id}' no encontrada.",
        )

    acceso_repo = AccesoContadorRepository(db)
    autorizado = liquidacion.perfil.usuario_id == current_user.id or (
        current_user.rol == RolUsuario.CONTADOR
        and await acceso_repo.contador_tiene_acceso(current_user.id, liquidacion.perfil_id)
    )
    if not autorizado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a esta liquidacion.",
        )

    return await _detalle_historico_response(liquidacion, db)


@router.post("/{liquidacion_id}/confirmar", status_code=status.HTTP_201_CREATED)
async def confirmar_liquidacion(
    liquidacion_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    result = await db.execute(
        select(LiquidacionPeriodo)
        .where(LiquidacionPeriodo.id == liquidacion_id)
        .options(
            selectinload(LiquidacionPeriodo.perfil),
            selectinload(LiquidacionPeriodo.revision),
            selectinload(LiquidacionPeriodo.confirmacion),
        )
    )
    liquidacion = result.scalar_one_or_none()
    if liquidacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Liquidacion '{liquidacion_id}' no encontrada.",
        )
    if liquidacion.perfil.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el contratista dueno del perfil puede confirmar la liquidacion.",
        )

    acceso_repo = AccesoContadorRepository(db)
    requiere_revision = await acceso_repo.contar_por_perfil(liquidacion.perfil_id) > 0
    if requiere_revision and liquidacion.revision is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La liquidacion requiere revision previa del contador antes de ser confirmada.",
        )

    confirmacion_repo = LiquidacionConfirmacionRepository(db)
    await confirmacion_repo.confirmar(liquidacion_id, current_user.id)
    await db.commit()
    return {"message": "Liquidacion confirmada correctamente."}


@router.get("/{liquidacion_id}/pdf")
async def descargar_pdf(
    liquidacion_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(
        select(LiquidacionPeriodo)
        .where(LiquidacionPeriodo.id == liquidacion_id)
        .options(
            selectinload(LiquidacionPeriodo.perfil),
            selectinload(LiquidacionPeriodo.revision),
            selectinload(LiquidacionPeriodo.confirmacion),
        )
    )
    liquidacion = result.scalar_one_or_none()

    if liquidacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Liquidacion '{liquidacion_id}' no encontrada.",
        )

    acceso_repo = AccesoContadorRepository(db)
    autorizado = liquidacion.perfil.usuario_id == current_user.id or (
        current_user.rol == RolUsuario.CONTADOR
        and await acceso_repo.contador_tiene_acceso(current_user.id, liquidacion.perfil_id)
    )
    if not autorizado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a esta liquidacion.",
        )
    if liquidacion.confirmacion is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La liquidacion debe ser confirmada por el contratista antes de descargar el PDF.",
        )

    pdf_bytes = generar_reporte_pdf(liquidacion)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=liquidacion_{liquidacion_id}.pdf"
        },
    )
