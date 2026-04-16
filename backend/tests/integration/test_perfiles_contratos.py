"""
Pruebas de integración — endpoints de perfiles y contratos.

Cubre:
  - Crear perfil exitosamente
  - Listar perfiles: cada usuario solo ve los suyos
  - Crear contrato exitosamente
  - Crear contrato para perfil ajeno → 403
  - Eliminar contrato propio → 204
  - Eliminar contrato ajeno → 403
"""
import pytest
from httpx import AsyncClient

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
PERFILES_URL = "/perfiles/"
CONTRATOS_URL = "/contratos/"
CONTADOR_URL = "/contador"

# Payloads base
USER_A = {
    "email": "user_a@example.com",
    "password": "passA123",
    "nombre_completo": "Usuario A",
}
USER_B = {
    "email": "user_b@example.com",
    "password": "passB123",
    "nombre_completo": "Usuario B",
}

PERFIL_PAYLOAD = {
    "tipo_documento": "CC",
    "numero_documento": "1234567890",
    "nombre_completo": "Contratista Prueba",
    "eps": "Sura EPS",
    "afp": "Protección",
    "ciiu_codigo": "6201",
}

CONTRATO_PAYLOAD = {
    "entidad_contratante": "Empresa S.A.S.",
    "valor_bruto_mensual": "5000000",
    "nivel_arl": "I",
    "fecha_inicio": "2025-01-01",
    "fecha_fin": "2025-12-31",
}


async def _register_and_token(client: AsyncClient, user_data: dict) -> str:
    """Helper: registra usuario y retorna el access_token."""
    resp = await client.post(REGISTER_URL, json=user_data)
    assert resp.status_code == 201, f"Register failed: {resp.text}"
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _crear_perfil(client: AsyncClient, token: str, payload: dict | None = None) -> dict:
    """Helper: crea un perfil y retorna el JSON de respuesta."""
    body = payload or PERFIL_PAYLOAD
    resp = await client.post(PERFILES_URL, json=body, headers=_auth_header(token))
    assert resp.status_code == 201, f"Crear perfil falló: {resp.text}"
    return resp.json()


async def _crear_contrato(
    client: AsyncClient, token: str, perfil_id: str, payload: dict | None = None
) -> dict:
    """Helper: crea un contrato y retorna el JSON de respuesta."""
    body = {**(payload or CONTRATO_PAYLOAD), "perfil_id": perfil_id}
    resp = await client.post(CONTRATOS_URL, json=body, headers=_auth_header(token))
    assert resp.status_code == 201, f"Crear contrato falló: {resp.text}"
    return resp.json()


# ─── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_crear_perfil_exitoso(async_client: AsyncClient):
    """POST /perfiles/ con token válido → 201, respuesta con id y nombre_completo."""
    token = await _register_and_token(async_client, USER_A)
    resp = await async_client.post(PERFILES_URL, json=PERFIL_PAYLOAD, headers=_auth_header(token))

    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "id" in data
    assert data["nombre_completo"] == PERFIL_PAYLOAD["nombre_completo"]


@pytest.mark.asyncio
async def test_crear_perfil_con_ciiu_alto_requiere_confirmacion(async_client: AsyncClient):
    token = await _register_and_token(async_client, USER_A)
    payload = {
        **PERFIL_PAYLOAD,
        "numero_documento": "3333333333",
        "ciiu_codigo": "9001",
    }

    resp = await async_client.post(PERFILES_URL, json=payload, headers=_auth_header(token))

    assert resp.status_code == 422, resp.text
    detail = resp.json()["detail"]
    assert detail["requires_ciiu_confirmation"] is True

    resp_ok = await async_client.post(
        PERFILES_URL,
        json={**payload, "confirmar_ciiu_alto": True},
        headers=_auth_header(token),
    )
    assert resp_ok.status_code == 201, resp_ok.text


@pytest.mark.asyncio
async def test_listar_perfiles_solo_propios(async_client: AsyncClient):
    """Dos usuarios crean un perfil cada uno; cada uno solo ve el suyo en GET /perfiles/."""
    token_a = await _register_and_token(async_client, USER_A)
    token_b = await _register_and_token(async_client, USER_B)

    # Perfil de usuario A
    payload_a = {**PERFIL_PAYLOAD, "numero_documento": "1111111111"}
    await _crear_perfil(async_client, token_a, payload_a)

    # Perfil de usuario B (número de documento diferente para evitar colisión)
    payload_b = {**PERFIL_PAYLOAD, "numero_documento": "2222222222"}
    await _crear_perfil(async_client, token_b, payload_b)

    # Usuario A lista sus perfiles
    resp_a = await async_client.get(PERFILES_URL, headers=_auth_header(token_a))
    assert resp_a.status_code == 200
    perfiles_a = resp_a.json()
    assert len(perfiles_a) == 1
    assert perfiles_a[0]["numero_documento"] == "1111111111"

    # Usuario B lista sus perfiles
    resp_b = await async_client.get(PERFILES_URL, headers=_auth_header(token_b))
    assert resp_b.status_code == 200
    perfiles_b = resp_b.json()
    assert len(perfiles_b) == 1
    assert perfiles_b[0]["numero_documento"] == "2222222222"


@pytest.mark.asyncio
async def test_crear_contrato_exitoso(async_client: AsyncClient):
    """Registrar → crear perfil → crear contrato → 201."""
    token = await _register_and_token(async_client, USER_A)
    perfil = await _crear_perfil(async_client, token)

    resp = await async_client.post(
        CONTRATOS_URL,
        json={**CONTRATO_PAYLOAD, "perfil_id": perfil["id"]},
        headers=_auth_header(token),
    )

    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "id" in data
    assert data["perfil_id"] == perfil["id"]


@pytest.mark.asyncio
async def test_crear_contrato_perfil_ajeno_retorna_403(async_client: AsyncClient):
    """Usuario B intenta crear contrato sobre perfil de Usuario A → 403."""
    token_a = await _register_and_token(async_client, USER_A)
    token_b = await _register_and_token(async_client, USER_B)

    # Usuario A crea su perfil
    perfil_a = await _crear_perfil(async_client, token_a)

    # Usuario B intenta crear un contrato para el perfil de A
    resp = await async_client.post(
        CONTRATOS_URL,
        json={**CONTRATO_PAYLOAD, "perfil_id": perfil_a["id"]},
        headers=_auth_header(token_b),
    )

    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_eliminar_contrato_exitoso(async_client: AsyncClient):
    """Crear contrato y luego eliminarlo → 204."""
    token = await _register_and_token(async_client, USER_A)
    perfil = await _crear_perfil(async_client, token)
    contrato = await _crear_contrato(async_client, token, perfil["id"])

    resp = await async_client.delete(
        f"{CONTRATOS_URL}{contrato['id']}",
        headers=_auth_header(token),
    )

    assert resp.status_code == 204, resp.text


@pytest.mark.asyncio
async def test_eliminar_contrato_ajeno_retorna_403(async_client: AsyncClient):
    """Usuario B intenta eliminar contrato de Usuario A → 403."""
    token_a = await _register_and_token(async_client, USER_A)
    token_b = await _register_and_token(async_client, USER_B)

    perfil_a = await _crear_perfil(async_client, token_a)
    contrato_a = await _crear_contrato(async_client, token_a, perfil_a["id"])

    resp = await async_client.delete(
        f"{CONTRATOS_URL}{contrato_a['id']}",
        headers=_auth_header(token_b),
    )

    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_contratista_vincula_contador_y_contador_ve_clientes(async_client: AsyncClient):
    token_contratista = await _register_and_token(async_client, USER_A)
    token_contador = await _register_and_token(
        async_client,
        {
            "email": "contador@example.com",
            "password": "passContador123",
            "nombre_completo": "Contador Uno",
            "rol": "CONTADOR",
        },
    )
    perfil = await _crear_perfil(
        async_client,
        token_contratista,
        {**PERFIL_PAYLOAD, "numero_documento": "4444444444"},
    )

    vinculo_resp = await async_client.post(
        f"{CONTADOR_URL}/vinculos",
        json={"perfil_id": perfil["id"], "contador_email": "contador@example.com"},
        headers=_auth_header(token_contratista),
    )
    assert vinculo_resp.status_code == 201, vinculo_resp.text

    clientes_resp = await async_client.get(
        f"{CONTADOR_URL}/clientes",
        headers=_auth_header(token_contador),
    )
    assert clientes_resp.status_code == 200, clientes_resp.text
    clientes = clientes_resp.json()
    assert len(clientes) == 1
    assert clientes[0]["perfil_id"] == perfil["id"]
