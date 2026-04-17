"""
Repositorio MFA para configuracion TOTP de usuarios CONTADOR.
Ref: RF-13, HU-14
"""
import pyotp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.usuario_mfa import UsuarioMFAConfig


class UsuarioMFARepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_por_usuario(self, usuario_id: str) -> UsuarioMFAConfig | None:
        result = await self._db.execute(
            select(UsuarioMFAConfig).where(UsuarioMFAConfig.usuario_id == usuario_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, usuario_id: str) -> UsuarioMFAConfig:
        config = await self.get_por_usuario(usuario_id)
        if config is not None:
            return config

        config = UsuarioMFAConfig(
            usuario_id=usuario_id,
            totp_secret=pyotp.random_base32(),
            activo=False,
        )
        self._db.add(config)
        await self._db.flush()
        return config

    async def activar_mfa(self, usuario_id: str) -> UsuarioMFAConfig:
        config = await self.get_por_usuario(usuario_id)
        if config is None:
            raise ValueError(f"No existe configuracion MFA para usuario {usuario_id}")
        config.activo = True
        await self._db.flush()
        return config
