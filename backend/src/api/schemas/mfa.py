"""
Schemas Pydantic para endpoints MFA.
Ref: RF-13, HU-14
"""
from pydantic import BaseModel


class MFASetupResponse(BaseModel):
    totp_uri: str
    secret: str
    mensaje: str = (
        "Escanea el codigo QR en tu app TOTP (Google Authenticator, Authy, etc.)"
    )


class MFAActivateRequest(BaseModel):
    codigo: str


class MFAVerifyRequest(BaseModel):
    mfa_token: str
    codigo: str


class MFAPendingResponse(BaseModel):
    mfa_required: bool = True
    mfa_token: str
    mensaje: str = "Ingresa el codigo de tu app autenticadora."
