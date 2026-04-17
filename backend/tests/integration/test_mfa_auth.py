"""
Pruebas de integracion y servicio para MFA del rol CONTADOR.
Ref: RF-13, HU-14, RNF-02, RNF-06
"""
import pyotp
import pytest
from httpx import AsyncClient

from src.application.services.mfa_service import (
    crear_mfa_pending_token,
    decodificar_mfa_pending_token,
    generar_totp_uri,
    verificar_codigo_totp,
)


def test_generar_totp_uri_formato_correcto():
    secret = pyotp.random_base32()
    uri = generar_totp_uri(secret=secret, email="contador@test.com")
    assert uri.startswith("otpauth://totp/")
    assert "contador%40test.com" in uri or "contador@test.com" in uri


def test_verificar_codigo_totp_valido():
    secret = pyotp.random_base32()
    codigo = pyotp.TOTP(secret).now()
    assert verificar_codigo_totp(secret, codigo) is True


def test_verificar_codigo_totp_invalido():
    secret = pyotp.random_base32()
    assert verificar_codigo_totp(secret, "000000") is False


def test_mfa_pending_token_round_trip():
    token = crear_mfa_pending_token(usuario_id="user-abc", email="c@t.com")
    payload = decodificar_mfa_pending_token(token)
    assert payload["sub"] == "user-abc"
    assert payload["scope"] == "mfa_pending"


@pytest.mark.asyncio
async def test_login_contador_sin_mfa_retorna_token_completo(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={
            "email": "contador_nomfa@test.com",
            "password": "clave123",
            "nombre_completo": "Contador Sin MFA",
            "rol": "CONTADOR",
        },
    )

    response = await async_client.post(
        "/auth/login",
        data={"username": "contador_nomfa@test.com", "password": "clave123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data.get("mfa_required") is None


@pytest.mark.asyncio
async def test_setup_mfa_retorna_uri(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={
            "email": "contador_setup@test.com",
            "password": "clave123",
            "nombre_completo": "Contador Setup",
            "rol": "CONTADOR",
        },
    )
    login = await async_client.post(
        "/auth/login",
        data={"username": "contador_setup@test.com", "password": "clave123"},
    )

    response = await async_client.post(
        "/auth/mfa/setup",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["totp_uri"].startswith("otpauth://totp/")
    assert len(data["secret"]) >= 16


@pytest.mark.asyncio
async def test_activar_mfa_con_codigo_valido(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={
            "email": "contador_activate@test.com",
            "password": "clave123",
            "nombre_completo": "Contador Activate",
            "rol": "CONTADOR",
        },
    )
    login = await async_client.post(
        "/auth/login",
        data={"username": "contador_activate@test.com", "password": "clave123"},
    )
    token = login.json()["access_token"]

    setup = await async_client.post(
        "/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    codigo = pyotp.TOTP(setup.json()["secret"]).now()

    response = await async_client.post(
        "/auth/mfa/activate",
        json={"codigo": codigo},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_contador_con_mfa_activo_retorna_mfa_required(async_client: AsyncClient):
    email = "contador_mfa_active@test.com"
    await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "clave123",
            "nombre_completo": "Contador MFA",
            "rol": "CONTADOR",
        },
    )
    login1 = await async_client.post(
        "/auth/login",
        data={"username": email, "password": "clave123"},
    )
    token1 = login1.json()["access_token"]
    setup = await async_client.post(
        "/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token1}"},
    )
    codigo = pyotp.TOTP(setup.json()["secret"]).now()
    await async_client.post(
        "/auth/mfa/activate",
        json={"codigo": codigo},
        headers={"Authorization": f"Bearer {token1}"},
    )

    login2 = await async_client.post(
        "/auth/login",
        data={"username": email, "password": "clave123"},
    )

    assert login2.status_code == 200
    data = login2.json()
    assert data["mfa_required"] is True
    assert "mfa_token" in data


@pytest.mark.asyncio
async def test_verify_mfa_con_codigo_valido_retorna_token_completo(async_client: AsyncClient):
    email = "contador_verify@test.com"
    await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "clave123",
            "nombre_completo": "Contador Verify",
            "rol": "CONTADOR",
        },
    )
    login1 = await async_client.post(
        "/auth/login",
        data={"username": email, "password": "clave123"},
    )
    token1 = login1.json()["access_token"]
    setup = await async_client.post(
        "/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token1}"},
    )
    secret = setup.json()["secret"]
    await async_client.post(
        "/auth/mfa/activate",
        json={"codigo": pyotp.TOTP(secret).now()},
        headers={"Authorization": f"Bearer {token1}"},
    )

    login2 = await async_client.post(
        "/auth/login",
        data={"username": email, "password": "clave123"},
    )
    mfa_token = login2.json()["mfa_token"]
    response = await async_client.post(
        "/auth/mfa/verify",
        json={"mfa_token": mfa_token, "codigo": pyotp.TOTP(secret).now()},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["rol"] == "CONTADOR"


@pytest.mark.asyncio
async def test_verify_mfa_con_codigo_invalido_retorna_401(async_client: AsyncClient):
    email = "contador_bad_code@test.com"
    await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "clave123",
            "nombre_completo": "Contador Bad",
            "rol": "CONTADOR",
        },
    )
    login1 = await async_client.post(
        "/auth/login",
        data={"username": email, "password": "clave123"},
    )
    token1 = login1.json()["access_token"]
    setup = await async_client.post(
        "/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token1}"},
    )
    secret = setup.json()["secret"]
    await async_client.post(
        "/auth/mfa/activate",
        json={"codigo": pyotp.TOTP(secret).now()},
        headers={"Authorization": f"Bearer {token1}"},
    )
    login2 = await async_client.post(
        "/auth/login",
        data={"username": email, "password": "clave123"},
    )
    mfa_token = login2.json()["mfa_token"]

    response = await async_client.post(
        "/auth/mfa/verify",
        json={"mfa_token": mfa_token, "codigo": "000000"},
    )

    assert response.status_code == 401
