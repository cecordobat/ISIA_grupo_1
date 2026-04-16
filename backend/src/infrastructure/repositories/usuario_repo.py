"""Repositorio de usuarios para autenticación."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import RolUsuario
from src.infrastructure.models.usuario import Usuario


class UsuarioRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_por_email(self, email: str) -> Usuario | None:
        result = await self._db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalar_one_or_none()

    async def get_por_id(self, usuario_id: str) -> Usuario | None:
        result = await self._db.execute(
            select(Usuario).where(Usuario.id == usuario_id)
        )
        return result.scalar_one_or_none()

    async def crear(
        self,
        email: str,
        hashed_password: str,
        nombre_completo: str,
        rol: RolUsuario = RolUsuario.CONTRATISTA,
    ) -> Usuario:
        usuario = Usuario(
            email=email,
            hashed_password=hashed_password,
            nombre_completo=nombre_completo,
            rol=rol,
        )
        self._db.add(usuario)
        await self._db.flush()
        return usuario
