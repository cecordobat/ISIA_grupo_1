"""
Dependencias de FastAPI — autenticación y sesión de BD.
Ref: context/non_functional_requirements.md RNF-06
"""
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auth_service import decodificar_token
from src.infrastructure.database import get_db
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.usuario_repo import UsuarioRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """
    Valida el JWT y retorna el usuario autenticado.
    HTTP 401 si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas. Inicie sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(token)
        usuario_id: str | None = payload.get("sub")  # type: ignore[assignment]
        if usuario_id is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    repo = UsuarioRepository(db)
    usuario = await repo.get_por_id(usuario_id)
    if usuario is None or not usuario.activo:
        raise credentials_exception

    return usuario
