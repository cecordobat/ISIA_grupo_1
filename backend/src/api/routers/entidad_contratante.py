"""
Router: verificación de cumplimiento para entidad contratante autorizada.
Principio de mínimo privilegio activo: solo estado de cumplimiento, sin detalle.
Ref: RF-11, HU-12, RNF-06
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.dependencies import get_current_user
from src.api.schemas.entidad_contratante import AutorizarAccesoRequest, EstadoCumplimientoResponse
from src.domain.enums import RolUsuario
from src.infrastructure.database import get_db
from src.infrastructure.models.liquidacion_periodo import LiquidacionPeriodo
from src.infrastructure.models.perfil_contratista import PerfilContratista
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.acceso_entidad_repo import AccesoEntidadRepository
from src.infrastructure.repositories.liquidacion_confirmacion_repo import LiquidacionConfirmacionRepository
from src.infrastructure.repositories.perfil_repo import PerfilRepository
from src.infrastructure.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/verificacion", tags=["verificación de cumplimiento"])


@router.post("/accesos/{perfil_id}/autorizar")
async def autorizar_entidad(
    perfil_id: str,
    body: AutorizarAccesoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    """El contratista autoriza a una entidad contratante a ver su estado de cumplimiento."""
    if current_user.rol != RolUsuario.CONTRATISTA:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el contratista puede autorizar.")

    perfil_repo = PerfilRepository(db)
    perfil = await perfil_repo.get_por_id(perfil_id)
    if perfil is None or perfil.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado.")

    usuario_repo = UsuarioRepository(db)
    entidad = await usuario_repo.get_por_email(body.entidad_email)
    if entidad is None or entidad.rol != RolUsuario.ENTIDAD_CONTRATANTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existe un usuario con ese email y rol ENTIDAD_CONTRATANTE.",
        )

    acceso_repo = AccesoEntidadRepository(db)
    await acceso_repo.autorizar(entidad_usuario_id=entidad.id, perfil_id=perfil_id)
    await db.commit()
    return {"mensaje": f"Acceso autorizado a {body.entidad_email}."}


@router.delete("/accesos/{perfil_id}/revocar")
async def revocar_entidad(
    perfil_id: str,
    body: AutorizarAccesoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    """El contratista revoca el acceso de una entidad contratante."""
    if current_user.rol != RolUsuario.CONTRATISTA:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el contratista puede revocar.")

    perfil_repo = PerfilRepository(db)
    perfil = await perfil_repo.get_por_id(perfil_id)
    if perfil is None or perfil.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado.")

    usuario_repo = UsuarioRepository(db)
    entidad = await usuario_repo.get_por_email(body.entidad_email)
    if entidad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario entidad no encontrado.")

    acceso_repo = AccesoEntidadRepository(db)
    await acceso_repo.revocar(entidad_usuario_id=entidad.id, perfil_id=perfil_id)
    await db.commit()
    return {"mensaje": "Acceso revocado."}


@router.get("/cumplimiento/{perfil_id}", response_model=EstadoCumplimientoResponse)
async def verificar_cumplimiento(
    perfil_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> EstadoCumplimientoResponse:
    """
    La entidad contratante consulta el estado de cumplimiento del contratista.
    Solo accesible si fue autorizada explícitamente por el contratista.
    Devuelve solo estado mínimo: nombre, documento, período más reciente, estado confirmado.
    """
    if current_user.rol != RolUsuario.ENTIDAD_CONTRATANTE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo entidades contratantes autorizadas.")

    acceso_repo = AccesoEntidadRepository(db)
    if not await acceso_repo.tiene_acceso(entidad_usuario_id=current_user.id, perfil_id=perfil_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso autorizado a este perfil.")

    perfil_repo = PerfilRepository(db)
    perfil = await perfil_repo.get_por_id(perfil_id)
    if perfil is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado.")

    result = await db.execute(
        select(LiquidacionPeriodo)
        .where(LiquidacionPeriodo.perfil_id == perfil_id)
        .options(selectinload(LiquidacionPeriodo.confirmacion))
        .order_by(LiquidacionPeriodo.periodo.desc())
    )
    liquidaciones = list(result.scalars().all())

    if not liquidaciones:
        return EstadoCumplimientoResponse(
            nombre_contratista=perfil.nombre_completo,
            documento=f"{perfil.tipo_documento} {perfil.numero_documento}",
            periodo_reciente=None,
            tiene_liquidacion_confirmada=False,
            estado="SIN_LIQUIDACIONES",
        )

    liq_reciente = liquidaciones[0]
    confirmada = liq_reciente.confirmacion is not None

    return EstadoCumplimientoResponse(
        nombre_contratista=perfil.nombre_completo,
        documento=f"{perfil.tipo_documento} {perfil.numero_documento}",
        periodo_reciente=liq_reciente.periodo,
        tiene_liquidacion_confirmada=confirmada,
        estado="CONFIRMADA" if confirmada else "PENDIENTE_CONFIRMACION",
    )
