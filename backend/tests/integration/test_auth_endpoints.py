"""
Pruebas de integración — endpoints de autenticación.

Cubre:
  - Registro de usuario (POST /auth/register)
  - Login exitoso (POST /auth/login)
  - Login con credenciales inválidas
  - Acceso a ruta protegida sin token
"""
import pytest
from httpx import AsyncClient

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
PERFILES_URL = "/perfiles/"

# Payload base de registro
VALID_REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "password": "securePass123",
    "nombre_completo": "Juan Pérez",
}


@pytest.mark.asyncio
async def test_register_crea_usuario(async_client: AsyncClient):
    """POST /auth/register con payload válido → 201 y access_token presente."""
    response = await async_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)

    assert response.status_code == 201, response.text
    data = response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0
    assert data.get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_login_retorna_token(async_client: AsyncClient):
    """Registro seguido de login → 200 y access_token presente."""
    # Primero registrar
    await async_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)

    # Luego hacer login (OAuth2PasswordRequestForm usa form-data)
    response = await async_client.post(
        LOGIN_URL,
        data={
            "username": VALID_REGISTER_PAYLOAD["email"],
            "password": VALID_REGISTER_PAYLOAD["password"],
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_credenciales_invalidas(async_client: AsyncClient):
    """Login con contraseña incorrecta → 401."""
    await async_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)

    response = await async_client.post(
        LOGIN_URL,
        data={
            "username": VALID_REGISTER_PAYLOAD["email"],
            "password": "contraseña_incorrecta",
        },
    )

    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_ruta_protegida_sin_token(async_client: AsyncClient):
    """GET /perfiles/ sin cabecera Authorization → 401."""
    response = await async_client.get(PERFILES_URL)

    assert response.status_code == 401, response.text
