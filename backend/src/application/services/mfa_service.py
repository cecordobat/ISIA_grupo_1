"""
Servicio MFA: generacion y verificacion TOTP + token intermedio de MFA.
Ref: RF-13, HU-14, RNF-02, RNF-06
"""
from datetime import UTC, datetime, timedelta

import pyotp
from jose import JWTError, jwt

from src.config import get_settings

settings = get_settings()
_MFA_PENDING_EXPIRE_MINUTES = 5


def generar_totp_uri(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="Motor Cumplimiento CO")


def verificar_codigo_totp(secret: str, codigo: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(codigo, valid_window=1)


def crear_mfa_pending_token(usuario_id: str, email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=_MFA_PENDING_EXPIRE_MINUTES)
    payload = {
        "sub": usuario_id,
        "email": email,
        "scope": "mfa_pending",
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decodificar_mfa_pending_token(token: str) -> dict[str, object]:
    try:
        payload: dict[str, object] = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
    except JWTError as e:
        raise ValueError(f"Token MFA invalido: {e}") from e

    if payload.get("scope") != "mfa_pending":
        raise ValueError("Token sin scope mfa_pending")
    return payload
