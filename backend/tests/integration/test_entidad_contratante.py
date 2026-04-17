"""
Tests de integración: verificación de cumplimiento por entidad contratante.
Ref: RF-11, HU-12, RNF-06
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_entidad_sin_autorizacion_no_puede_ver_cumplimiento(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "email": "entidad_noauth@empresa.com",
        "password": "pass123",
        "nombre_completo": "Empresa SA",
        "rol": "ENTIDAD_CONTRATANTE",
    })
    login = await async_client.post("/auth/login", data={
        "username": "entidad_noauth@empresa.com",
        "password": "pass123",
    })
    token = login.json()["access_token"]

    response = await async_client.get(
        "/verificacion/cumplimiento/perfil-inexistente",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_contratista_puede_autorizar_entidad(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "email": "contratista_ent_test@test.com",
        "password": "pass123",
        "nombre_completo": "Contratista Test",
        "rol": "CONTRATISTA",
    })
    login_c = await async_client.post("/auth/login", data={
        "username": "contratista_ent_test@test.com",
        "password": "pass123",
    })
    token_c = login_c.json()["access_token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    perfil_res = await async_client.post("/perfiles/", json={
        "tipo_documento": "CC",
        "numero_documento": "11112223",
        "nombre_completo": "Contratista Test",
        "eps": "Sura",
        "afp": "Porvenir",
        "ciiu_codigo": "6201",
    }, headers=headers_c)
    assert perfil_res.status_code == 201, perfil_res.text
    perfil_id = perfil_res.json()["id"]

    await async_client.post("/auth/register", json={
        "email": "entidad_auth_test@empresa.com",
        "password": "pass123",
        "nombre_completo": "Empresa Autorizada",
        "rol": "ENTIDAD_CONTRATANTE",
    })

    response = await async_client.post(
        f"/verificacion/accesos/{perfil_id}/autorizar",
        json={"entidad_email": "entidad_auth_test@empresa.com"},
        headers=headers_c,
    )
    assert response.status_code == 200
    assert "Acceso autorizado" in response.json()["mensaje"]


@pytest.mark.asyncio
async def test_entidad_autorizada_ve_estado_cumplimiento(async_client: AsyncClient):
    # Contratista
    await async_client.post("/auth/register", json={
        "email": "contratista_v2@test.com",
        "password": "pass123",
        "nombre_completo": "Contratista V2",
        "rol": "CONTRATISTA",
    })
    login_c = await async_client.post("/auth/login", data={
        "username": "contratista_v2@test.com",
        "password": "pass123",
    })
    token_c = login_c.json()["access_token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    perfil_res = await async_client.post("/perfiles/", json={
        "tipo_documento": "CC",
        "numero_documento": "55556666",
        "nombre_completo": "Contratista V2",
        "eps": "Sura",
        "afp": "Porvenir",
        "ciiu_codigo": "6201",
    }, headers=headers_c)
    assert perfil_res.status_code == 201
    perfil_id = perfil_res.json()["id"]

    # Entidad contratante
    await async_client.post("/auth/register", json={
        "email": "entidad_v2@empresa.com",
        "password": "pass123",
        "nombre_completo": "Empresa V2",
        "rol": "ENTIDAD_CONTRATANTE",
    })
    login_e = await async_client.post("/auth/login", data={
        "username": "entidad_v2@empresa.com",
        "password": "pass123",
    })
    token_e = login_e.json()["access_token"]

    # Contratista autoriza entidad
    await async_client.post(
        f"/verificacion/accesos/{perfil_id}/autorizar",
        json={"entidad_email": "entidad_v2@empresa.com"},
        headers=headers_c,
    )

    # Entidad consulta cumplimiento
    response = await async_client.get(
        f"/verificacion/cumplimiento/{perfil_id}",
        headers={"Authorization": f"Bearer {token_e}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "SIN_LIQUIDACIONES"
    assert "ibc" not in data
    assert "contratos" not in data
