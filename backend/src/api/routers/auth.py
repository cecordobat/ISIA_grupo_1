"""
Router de autenticacion: register, login y MFA para rol CONTADOR.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.api.schemas.mfa import (
    MFAActivateRequest,
    MFAPendingResponse,
    MFASetupResponse,
    MFAVerifyRequest,
)
from src.application.services.auth_service import (
    crear_access_token,
    hash_password,
    verify_password,
)
from src.application.services.mfa_service import (
    crear_mfa_pending_token,
    decodificar_mfa_pending_token,
    generar_totp_uri,
    verificar_codigo_totp,
)
from src.domain.enums import RolUsuario
from src.infrastructure.database import get_db
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.usuario_mfa_repo import UsuarioMFARepository
from src.infrastructure.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/auth", tags=["autenticacion"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: RolUsuario


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombre_completo: str
    rol: RolUsuario = RolUsuario.CONTRATISTA


@router.post("/login", response_model=TokenResponse | MFAPendingResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse | MFAPendingResponse:
    """Autentica al usuario; si el contador tiene MFA activo, exige segundo factor."""
    repo = UsuarioRepository(db)
    usuario = await repo.get_por_email(form_data.username)

    if usuario is None or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if usuario.rol == RolUsuario.CONTADOR:
        mfa_config = await UsuarioMFARepository(db).get_por_usuario(usuario.id)
        if mfa_config is not None and mfa_config.activo:
            return MFAPendingResponse(
                mfa_token=crear_mfa_pending_token(
                    usuario_id=usuario.id,
                    email=usuario.email,
                )
            )

    token = crear_access_token({"sub": usuario.id, "email": usuario.email, "rol": usuario.rol})
    return TokenResponse(access_token=token, rol=usuario.rol)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Registra un nuevo usuario y retorna su JWT."""
    repo = UsuarioRepository(db)
    if await repo.get_por_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese email.",
        )

    usuario = await repo.crear(
        email=body.email,
        hashed_password=hash_password(body.password),
        nombre_completo=body.nombre_completo,
        rol=body.rol,
    )
    await db.commit()

    token = crear_access_token({"sub": usuario.id, "email": usuario.email, "rol": usuario.rol})
    return TokenResponse(access_token=token, rol=usuario.rol)


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> MFASetupResponse:
    if current_user.rol != RolUsuario.CONTADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los contadores pueden configurar MFA.",
        )

    config = await UsuarioMFARepository(db).get_or_create(current_user.id)
    await db.commit()
    return MFASetupResponse(
        totp_uri=generar_totp_uri(config.totp_secret, current_user.email),
        secret=config.totp_secret,
    )


@router.post("/mfa/activate")
async def mfa_activate(
    body: MFAActivateRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if current_user.rol != RolUsuario.CONTADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los contadores pueden activar MFA.",
        )

    repo = UsuarioMFARepository(db)
    config = await repo.get_por_usuario(current_user.id)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Primero ejecute la configuracion MFA.",
        )
    if not verificar_codigo_totp(config.totp_secret, body.codigo):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Codigo TOTP invalido.",
        )

    await repo.activar_mfa(current_user.id)
    await db.commit()
    return {"mensaje": "MFA activado correctamente."}


@router.post("/mfa/verify", response_model=TokenResponse)
async def mfa_verify(
    body: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        payload = decodificar_mfa_pending_token(body.mfa_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token MFA invalido o expirado.",
        )

    usuario_id = str(payload["sub"])
    usuario = await UsuarioRepository(db).get_por_id(usuario_id)
    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
        )

    config = await UsuarioMFARepository(db).get_por_usuario(usuario.id)
    if config is None or not config.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA no esta activo para este usuario.",
        )
    if not verificar_codigo_totp(config.totp_secret, body.codigo):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Codigo TOTP incorrecto.",
        )

    token = crear_access_token({"sub": usuario.id, "email": usuario.email, "rol": usuario.rol})
    return TokenResponse(access_token=token, rol=usuario.rol)
