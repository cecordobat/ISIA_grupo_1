"""
Tests de integración: administración de parámetros normativos.
Ref: RF-10, HU-11, RNF-03, INV-04
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crear_snapshot_como_admin(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "email": "admin_snap@test.com",
        "password": "adminpass",
        "nombre_completo": "Administrador",
        "rol": "ADMIN",
    })
    login = await async_client.post("/auth/login", data={
        "username": "admin_snap@test.com",
        "password": "adminpass",
    })
    token = login.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {token}"})

    response = await async_client.post("/admin/parametros/snapshots", json={
        "smmlv": 1300000.0,
        "uvt": 47065.0,
        "pct_salud": 0.125,
        "pct_pension": 0.16,
        "tabla_arl_json": '{"I":"0.00522","II":"0.01044","III":"0.02436","IV":"0.04350","V":"0.06960"}',
        "vigencia_anio": 2099,
    })
    assert response.status_code == 201
    assert response.json()["vigencia_anio"] == 2099

    async_client.headers.clear()


@pytest.mark.asyncio
async def test_listar_snapshots_como_admin(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "email": "admin_list@test.com",
        "password": "adminpass",
        "nombre_completo": "Administrador",
        "rol": "ADMIN",
    })
    login = await async_client.post("/auth/login", data={
        "username": "admin_list@test.com",
        "password": "adminpass",
    })
    token = login.json()["access_token"]

    response = await async_client.get(
        "/admin/parametros/snapshots",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_admin_endpoint_rechaza_contratista(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "email": "contratista_noadmin@test.com",
        "password": "pass123",
        "nombre_completo": "Contratista",
        "rol": "CONTRATISTA",
    })
    login = await async_client.post("/auth/login", data={
        "username": "contratista_noadmin@test.com",
        "password": "pass123",
    })
    token = login.json()["access_token"]

    response = await async_client.get(
        "/admin/parametros/snapshots",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
