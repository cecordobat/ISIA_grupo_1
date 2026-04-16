"""
Router de autenticación — POST /auth/login, POST /auth/register
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auth_service import (
    crear_access_token,
    hash_password,
    verify_password,
)
from src.domain.enums import RolUsuario
from src.infrastructure.database import get_db
from src.infrastructure.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/auth", tags=["autenticación"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: RolUsuario


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombre_completo: str
    rol: RolUsuario = RolUsuario.CONTRATISTA


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Autentica al usuario y retorna un JWT."""
    repo = UsuarioRepository(db)
    usuario = await repo.get_por_email(form_data.username)

    if usuario is None or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
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
