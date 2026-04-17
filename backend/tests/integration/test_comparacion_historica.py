"""
Tests de integración: comparación histórica entre períodos.
Ref: RF-12, HU-13, INV-03
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_comparar_periodos_requiere_autenticacion(async_client: AsyncClient):
    response = await async_client.get(
        "/liquidaciones/comparar?periodo_a=2025-01&periodo_b=2025-02&perfil_id=x"
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_comparar_periodos_inexistentes_retorna_404(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "email": "comparacion_test@test.com",
        "password": "pass123",
        "nombre_completo": "Test Comparacion",
        "rol": "CONTRATISTA",
    })
    login = await async_client.post("/auth/login", data={
        "username": "comparacion_test@test.com",
        "password": "pass123",
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    perfil_res = await async_client.post("/perfiles/", json={
        "tipo_documento": "CC",
        "numero_documento": "99881122",
        "nombre_completo": "Test Comparacion",
        "eps": "Sura",
        "afp": "Porvenir",
        "ciiu_codigo": "6201",
    }, headers=headers)
    assert perfil_res.status_code == 201, perfil_res.text
    perfil_id = perfil_res.json()["id"]

    response = await async_client.get(
        f"/liquidaciones/comparar?periodo_a=2020-01&periodo_b=2020-02&perfil_id={perfil_id}",
        headers=headers,
    )
    assert response.status_code == 404
    assert "períodos" in response.json()["detail"]
