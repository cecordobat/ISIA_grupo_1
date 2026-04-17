# FASE 2 — Admin Parámetros Normativos: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir que un usuario con rol ADMIN actualice tablas normativas (SnapshotNormativo, TablaParametroCIIU, TablaRetencion383) sin alterar liquidaciones históricas. Ref: RF-10, HU-11, RNF-03, INV-04.

**Architecture:** Se agrega un router `/admin/parametros` protegido por guard `require_admin`. Los endpoints de escritura siempre crean filas nuevas con nueva vigencia (nunca UPDATE en datos usados por liquidaciones históricas). El repositorio de parámetros ya existe — se extiende con métodos de escritura. Una página de administración en el frontend permite gestionar los datos.

**Tech Stack:** FastAPI + SQLAlchemy async + React + Zustand

**Invariante crítica:** INV-04 — los parámetros normativos no se sobreescriben. Crear filas nuevas con `vigencia_anio` nuevo para SnapshotNormativo, o `vigente_desde` nuevo para CIIU y Retención383.

---

## Mapa de archivos

| Acción | Archivo |
|---|---|
| Crear | `backend/src/api/routers/admin.py` |
| Crear | `backend/src/api/schemas/admin.py` |
| Crear | `backend/tests/test_admin_parametros.py` |
| Crear | `frontend/src/pages/AdminParametrosPage.tsx` |
| Crear | `frontend/src/api/admin.ts` |
| Modificar | `backend/src/infrastructure/repositories/parametros_repo.py` |
| Modificar | `backend/src/api/dependencies.py` (guard require_admin) |
| Modificar | `backend/src/api/main.py` (incluir router admin) |

---

## Task 1: Guard require_admin en dependencies

**Files:**
- Modify: `backend/src/api/dependencies.py`

- [ ] **Step 1.1: Escribir test del guard**

Crea `backend/tests/test_admin_parametros.py`:

```python
"""
Tests de administración de parámetros normativos.
Ref: RF-10, HU-11, RNF-03, INV-04
"""
import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

from src.api.dependencies import require_admin
from src.domain.enums import RolUsuario


@pytest.mark.asyncio
async def test_require_admin_permite_admin():
    usuario = MagicMock()
    usuario.rol = RolUsuario.ADMIN
    result = await require_admin(current_user=usuario)
    assert result is usuario


@pytest.mark.asyncio
async def test_require_admin_rechaza_contratista():
    usuario = MagicMock()
    usuario.rol = RolUsuario.CONTRATISTA
    with pytest.raises(HTTPException) as exc:
        await require_admin(current_user=usuario)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_admin_rechaza_contador():
    usuario = MagicMock()
    usuario.rol = RolUsuario.CONTADOR
    with pytest.raises(HTTPException) as exc:
        await require_admin(current_user=usuario)
    assert exc.value.status_code == 403
```

- [ ] **Step 1.2: Ejecutar tests para verificar que fallan**

```bash
cd backend
python -m pytest tests/test_admin_parametros.py -k "require_admin" -v
```

Expected: FAIL — `require_admin` no existe

- [ ] **Step 1.3: Agregar require_admin a dependencies.py**

En `backend/src/api/dependencies.py`, agrega al final:

```python
from src.domain.enums import RolUsuario


async def require_admin(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """Guard: solo usuarios con rol ADMIN pueden acceder."""
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido al rol Administrador.",
        )
    return current_user
```

- [ ] **Step 1.4: Ejecutar tests**

```bash
cd backend
python -m pytest tests/test_admin_parametros.py -k "require_admin" -v
```

Expected: PASS (3 tests)

- [ ] **Step 1.5: Commit**

```bash
git add backend/src/api/dependencies.py backend/tests/test_admin_parametros.py
git commit -m "feat: add require_admin guard to dependencies"
```

---

## Task 2: Métodos de escritura en ParametrosRepository

**Files:**
- Modify: `backend/src/infrastructure/repositories/parametros_repo.py`

- [ ] **Step 2.1: Escribir tests de los nuevos métodos**

En `backend/tests/test_admin_parametros.py`, agrega:

```python
from unittest.mock import AsyncMock

from src.infrastructure.repositories.parametros_repo import ParametrosRepository


@pytest.mark.asyncio
async def test_crear_snapshot_normativo():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    repo = ParametrosRepository(db)
    snapshot = await repo.crear_snapshot(
        smmlv=1300000.00,
        uvt=47065.00,
        pct_salud=0.125,
        pct_pension=0.16,
        tabla_arl_json='{"I":"0.00522","II":"0.01044","III":"0.02436","IV":"0.04350","V":"0.06960"}',
        vigencia_anio=2026,
    )

    db.add.assert_called_once()
    assert snapshot.vigencia_anio == 2026


@pytest.mark.asyncio
async def test_crear_ciiu():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    from datetime import date

    repo = ParametrosRepository(db)
    ciiu = await repo.crear_ciiu(
        codigo_ciiu="7010",
        descripcion="Actividades de consultoría de gestión",
        pct_costos_presuntos=0.27,
        vigente_desde=date(2026, 1, 1),
    )

    db.add.assert_called_once()
    assert ciiu.codigo_ciiu == "7010"


@pytest.mark.asyncio
async def test_crear_tramo_retencion():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    from datetime import date

    repo = ParametrosRepository(db)
    tramo = await repo.crear_tramo_retencion(
        uvt_desde=0,
        uvt_hasta=87,
        tarifa_marginal=0.0,
        uvt_deduccion=0.0,
        vigente_desde=date(2026, 1, 1),
    )

    db.add.assert_called_once()
    assert tramo.uvt_desde == 0
```

- [ ] **Step 2.2: Ejecutar tests para verificar que fallan**

```bash
cd backend
python -m pytest tests/test_admin_parametros.py -k "crear_snapshot or crear_ciiu or crear_tramo" -v
```

Expected: FAIL

- [ ] **Step 2.3: Agregar métodos al repositorio**

En `backend/src/infrastructure/repositories/parametros_repo.py`, agrega los siguientes métodos a la clase `ParametrosRepository`:

```python
    async def crear_snapshot(
        self,
        smmlv: float,
        uvt: float,
        pct_salud: float,
        pct_pension: float,
        tabla_arl_json: str,
        vigencia_anio: int,
    ) -> SnapshotNormativo:
        """
        Crea un snapshot normativo para un año nuevo.
        INV-04: nunca sobreescribe un snapshot existente.
        """
        existing = await self.get_snapshot_por_anio(vigencia_anio)
        if existing is not None:
            raise ValueError(f"Ya existe un snapshot para el año {vigencia_anio}. Usa un año nuevo.")

        snapshot = SnapshotNormativo(
            smmlv=smmlv,
            uvt=uvt,
            pct_salud=pct_salud,
            pct_pension=pct_pension,
            tabla_arl_json=tabla_arl_json,
            vigencia_anio=vigencia_anio,
        )
        self._db.add(snapshot)
        await self._db.flush()
        return snapshot

    async def crear_ciiu(
        self,
        codigo_ciiu: str,
        descripcion: str,
        pct_costos_presuntos: float,
        vigente_desde: "date",
    ) -> TablaParametroCIIU:
        """Crea una nueva entrada CIIU. Los registros históricos no se modifican."""
        from datetime import date as date_type
        ciiu = TablaParametroCIIU(
            codigo_ciiu=codigo_ciiu,
            descripcion=descripcion,
            pct_costos_presuntos=pct_costos_presuntos,
            vigente_desde=vigente_desde,
        )
        self._db.add(ciiu)
        await self._db.flush()
        return ciiu

    async def crear_tramo_retencion(
        self,
        uvt_desde: float,
        uvt_hasta: "float | None",
        tarifa_marginal: float,
        uvt_deduccion: float,
        vigente_desde: "date",
    ) -> TablaRetencion383:
        """Crea un nuevo tramo Art. 383. Los tramos históricos no se modifican."""
        tramo = TablaRetencion383(
            uvt_desde=uvt_desde,
            uvt_hasta=uvt_hasta,
            tarifa_marginal=tarifa_marginal,
            uvt_deduccion=uvt_deduccion,
            vigente_desde=vigente_desde,
        )
        self._db.add(tramo)
        await self._db.flush()
        return tramo

    async def listar_snapshots(self) -> "list[SnapshotNormativo]":
        from sqlalchemy import select
        result = await self._db.execute(
            select(SnapshotNormativo).order_by(SnapshotNormativo.vigencia_anio.desc())
        )
        return list(result.scalars().all())

    async def listar_ciiu(self) -> "list[TablaParametroCIIU]":
        from sqlalchemy import select
        result = await self._db.execute(
            select(TablaParametroCIIU).order_by(TablaParametroCIIU.codigo_ciiu)
        )
        return list(result.scalars().all())

    async def listar_tramos_retencion_todos(self) -> "list[TablaRetencion383]":
        from sqlalchemy import select
        result = await self._db.execute(
            select(TablaRetencion383).order_by(
                TablaRetencion383.vigente_desde.desc(), TablaRetencion383.uvt_desde
            )
        )
        return list(result.scalars().all())
```

- [ ] **Step 2.4: Ejecutar tests**

```bash
cd backend
python -m pytest tests/test_admin_parametros.py -k "crear_snapshot or crear_ciiu or crear_tramo" -v
```

Expected: PASS

- [ ] **Step 2.5: Commit**

```bash
git add backend/src/infrastructure/repositories/parametros_repo.py backend/tests/test_admin_parametros.py
git commit -m "feat: add write methods to ParametrosRepository (INV-04 safe)"
```

---

## Task 3: Schemas de administración

**Files:**
- Create: `backend/src/api/schemas/admin.py`

- [ ] **Step 3.1: Crear schemas**

Crea `backend/src/api/schemas/admin.py`:

```python
"""
Schemas Pydantic para endpoints de administración de parámetros normativos.
Ref: RF-10, HU-11, INV-04
"""
from datetime import date

from pydantic import BaseModel, Field


class SnapshotNormativoCreate(BaseModel):
    smmlv: float = Field(..., gt=0, description="Salario Mínimo Mensual Legal Vigente")
    uvt: float = Field(..., gt=0, description="Unidad de Valor Tributario")
    pct_salud: float = Field(default=0.125, ge=0, le=1)
    pct_pension: float = Field(default=0.16, ge=0, le=1)
    tabla_arl_json: str = Field(
        ...,
        description='JSON con tasas ARL por nivel, ej: {"I":"0.00522","II":"0.01044",...}'
    )
    vigencia_anio: int = Field(..., ge=2020, le=2100)


class SnapshotNormativoResponse(BaseModel):
    id: str
    smmlv: float
    uvt: float
    pct_salud: float
    pct_pension: float
    tabla_arl_json: str
    vigencia_anio: int

    model_config = {"from_attributes": True}


class CIIUCreate(BaseModel):
    codigo_ciiu: str = Field(..., min_length=4, max_length=10)
    descripcion: str = Field(..., min_length=5, max_length=500)
    pct_costos_presuntos: float = Field(..., ge=0, le=1)
    vigente_desde: date


class CIIUResponse(BaseModel):
    codigo_ciiu: str
    descripcion: str
    pct_costos_presuntos: float
    vigente_desde: date

    model_config = {"from_attributes": True}


class TramoRetencionCreate(BaseModel):
    uvt_desde: float = Field(..., ge=0)
    uvt_hasta: float | None = None
    tarifa_marginal: float = Field(..., ge=0, le=1)
    uvt_deduccion: float = Field(..., ge=0)
    vigente_desde: date


class TramoRetencionResponse(BaseModel):
    id: int
    uvt_desde: float
    uvt_hasta: float | None
    tarifa_marginal: float
    uvt_deduccion: float
    vigente_desde: date

    model_config = {"from_attributes": True}
```

- [ ] **Step 3.2: Verificar importación**

```bash
cd backend
python -c "from src.api.schemas.admin import SnapshotNormativoCreate, CIIUCreate, TramoRetencionCreate; print('OK')"
```

Expected: `OK`

- [ ] **Step 3.3: Commit**

```bash
git add backend/src/api/schemas/admin.py
git commit -m "feat: add admin Pydantic schemas for normative parameters"
```

---

## Task 4: Router de administración

**Files:**
- Create: `backend/src/api/routers/admin.py`
- Modify: `backend/src/api/main.py`

- [ ] **Step 4.1: Escribir tests de integración del router**

En `backend/tests/test_admin_parametros.py`, agrega:

```python
import pytest
from httpx import AsyncClient, ASGITransport

from src.api.main import app


@pytest.fixture
async def admin_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Registrar y logear como ADMIN
        await client.post("/auth/register", json={
            "email": "admin@test.com",
            "password": "adminpass",
            "nombre_completo": "Administrador",
            "rol": "ADMIN",
        })
        login = await client.post("/auth/login", data={
            "username": "admin@test.com",
            "password": "adminpass",
        })
        token = login.json()["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client


@pytest.mark.asyncio
async def test_crear_snapshot_como_admin(admin_client):
    response = await admin_client.post("/admin/parametros/snapshots", json={
        "smmlv": 1300000.0,
        "uvt": 47065.0,
        "pct_salud": 0.125,
        "pct_pension": 0.16,
        "tabla_arl_json": '{"I":"0.00522","II":"0.01044","III":"0.02436","IV":"0.04350","V":"0.06960"}',
        "vigencia_anio": 2099,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["vigencia_anio"] == 2099


@pytest.mark.asyncio
async def test_listar_snapshots_como_admin(admin_client):
    response = await admin_client.get("/admin/parametros/snapshots")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_admin_endpoint_rechaza_contratista():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/register", json={
            "email": "contratista_noadmin@test.com",
            "password": "pass123",
            "nombre_completo": "Contratista",
            "rol": "CONTRATISTA",
        })
        login = await client.post("/auth/login", data={
            "username": "contratista_noadmin@test.com",
            "password": "pass123",
        })
        token = login.json()["access_token"]
        response = await client.get(
            "/admin/parametros/snapshots",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
```

- [ ] **Step 4.2: Ejecutar tests para verificar que fallan**

```bash
cd backend
python -m pytest tests/test_admin_parametros.py -k "admin_client or snapshot or contratista_noadmin" -v
```

Expected: FAIL — router no existe

- [ ] **Step 4.3: Crear router admin**

Crea `backend/src/api/routers/admin.py`:

```python
"""
Router de administración de parámetros normativos.
Solo accesible para rol ADMIN.
Ref: RF-10, HU-11, INV-04, RNF-03
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import require_admin
from src.api.schemas.admin import (
    CIIUCreate,
    CIIUResponse,
    SnapshotNormativoCreate,
    SnapshotNormativoResponse,
    TramoRetencionCreate,
    TramoRetencionResponse,
)
from src.infrastructure.database import get_db
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.parametros_repo import ParametrosRepository

router = APIRouter(prefix="/admin/parametros", tags=["administración"])


@router.get("/snapshots", response_model=list[SnapshotNormativoResponse])
async def listar_snapshots(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[SnapshotNormativoResponse]:
    repo = ParametrosRepository(db)
    snapshots = await repo.listar_snapshots()
    return [SnapshotNormativoResponse.model_validate(s) for s in snapshots]


@router.post("/snapshots", response_model=SnapshotNormativoResponse, status_code=status.HTTP_201_CREATED)
async def crear_snapshot(
    body: SnapshotNormativoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> SnapshotNormativoResponse:
    repo = ParametrosRepository(db)
    try:
        snapshot = await repo.crear_snapshot(
            smmlv=body.smmlv,
            uvt=body.uvt,
            pct_salud=body.pct_salud,
            pct_pension=body.pct_pension,
            tabla_arl_json=body.tabla_arl_json,
            vigencia_anio=body.vigencia_anio,
        )
        await db.commit()
        return SnapshotNormativoResponse.model_validate(snapshot)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/ciiu", response_model=list[CIIUResponse])
async def listar_ciiu(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[CIIUResponse]:
    repo = ParametrosRepository(db)
    return [CIIUResponse.model_validate(c) for c in await repo.listar_ciiu()]


@router.post("/ciiu", response_model=CIIUResponse, status_code=status.HTTP_201_CREATED)
async def crear_ciiu(
    body: CIIUCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> CIIUResponse:
    repo = ParametrosRepository(db)
    ciiu = await repo.crear_ciiu(
        codigo_ciiu=body.codigo_ciiu,
        descripcion=body.descripcion,
        pct_costos_presuntos=body.pct_costos_presuntos,
        vigente_desde=body.vigente_desde,
    )
    await db.commit()
    return CIIUResponse.model_validate(ciiu)


@router.get("/retencion", response_model=list[TramoRetencionResponse])
async def listar_tramos_retencion(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[TramoRetencionResponse]:
    repo = ParametrosRepository(db)
    return [TramoRetencionResponse.model_validate(t) for t in await repo.listar_tramos_retencion_todos()]


@router.post("/retencion", response_model=TramoRetencionResponse, status_code=status.HTTP_201_CREATED)
async def crear_tramo_retencion(
    body: TramoRetencionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> TramoRetencionResponse:
    repo = ParametrosRepository(db)
    tramo = await repo.crear_tramo_retencion(
        uvt_desde=body.uvt_desde,
        uvt_hasta=body.uvt_hasta,
        tarifa_marginal=body.tarifa_marginal,
        uvt_deduccion=body.uvt_deduccion,
        vigente_desde=body.vigente_desde,
    )
    await db.commit()
    return TramoRetencionResponse.model_validate(tramo)
```

- [ ] **Step 4.4: Registrar router en main.py**

En `backend/src/api/main.py`:
- Agrega `from src.api.routers import admin` en el bloque de imports de routers
- Agrega `app.include_router(admin.router)` en `create_app()`

- [ ] **Step 4.5: Ejecutar tests**

```bash
cd backend
python -m pytest tests/test_admin_parametros.py -v
```

Expected: PASS

- [ ] **Step 4.6: Linting**

```bash
cd backend
python -m ruff check src tests
```

- [ ] **Step 4.7: Commit**

```bash
git add backend/src/api/routers/admin.py backend/src/api/main.py backend/tests/test_admin_parametros.py
git commit -m "feat: add /admin/parametros router for normative parameter management (RF-10)"
```

---

## Task 5: Frontend AdminParametrosPage

**Files:**
- Create: `frontend/src/api/admin.ts`
- Create: `frontend/src/pages/AdminParametrosPage.tsx`

- [ ] **Step 5.1: Crear cliente API admin**

Crea `frontend/src/api/admin.ts`:

```typescript
import apiClient from './client';

export interface SnapshotNormativo {
  id: string;
  smmlv: number;
  uvt: number;
  pct_salud: number;
  pct_pension: number;
  tabla_arl_json: string;
  vigencia_anio: number;
}

export interface SnapshotCreate {
  smmlv: number;
  uvt: number;
  pct_salud: number;
  pct_pension: number;
  tabla_arl_json: string;
  vigencia_anio: number;
}

export async function listarSnapshots(): Promise<SnapshotNormativo[]> {
  const res = await apiClient.get<SnapshotNormativo[]>('/admin/parametros/snapshots');
  return res.data;
}

export async function crearSnapshot(data: SnapshotCreate): Promise<SnapshotNormativo> {
  const res = await apiClient.post<SnapshotNormativo>('/admin/parametros/snapshots', data);
  return res.data;
}
```

- [ ] **Step 5.2: Crear página AdminParametrosPage**

Crea `frontend/src/pages/AdminParametrosPage.tsx`:

```tsx
import { useEffect, useState } from 'react';
import { listarSnapshots, crearSnapshot, SnapshotNormativo, SnapshotCreate } from '../api/admin';

export function AdminParametrosPage() {
  const [snapshots, setSnapshots] = useState<SnapshotNormativo[]>([]);
  const [error, setError] = useState('');
  const [form, setForm] = useState<SnapshotCreate>({
    smmlv: 0,
    uvt: 0,
    pct_salud: 0.125,
    pct_pension: 0.16,
    tabla_arl_json: '{"I":"0.00522","II":"0.01044","III":"0.02436","IV":"0.04350","V":"0.06960"}',
    vigencia_anio: new Date().getFullYear(),
  });

  useEffect(() => {
    listarSnapshots()
      .then(setSnapshots)
      .catch(() => setError('Error al cargar snapshots.'));
  }, []);

  async function handleCrear(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const nuevo = await crearSnapshot(form);
      setSnapshots([nuevo, ...snapshots]);
    } catch {
      setError('Error al crear snapshot. Verifica que el año no exista ya.');
    }
  }

  return (
    <div>
      <h1>Administración de Parámetros Normativos</h1>

      <section>
        <h2>Crear Snapshot Normativo</h2>
        <form onSubmit={handleCrear}>
          <label>
            Año: <input type="number" value={form.vigencia_anio}
              onChange={e => setForm({...form, vigencia_anio: +e.target.value})} />
          </label>
          <label>
            SMMLV: <input type="number" step="0.01" value={form.smmlv}
              onChange={e => setForm({...form, smmlv: +e.target.value})} />
          </label>
          <label>
            UVT: <input type="number" step="0.01" value={form.uvt}
              onChange={e => setForm({...form, uvt: +e.target.value})} />
          </label>
          <label>
            ARL JSON: <input type="text" value={form.tabla_arl_json}
              onChange={e => setForm({...form, tabla_arl_json: e.target.value})} />
          </label>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <button type="submit">Crear Snapshot</button>
        </form>
      </section>

      <section>
        <h2>Snapshots existentes</h2>
        <table>
          <thead>
            <tr><th>Año</th><th>SMMLV</th><th>UVT</th></tr>
          </thead>
          <tbody>
            {snapshots.map(s => (
              <tr key={s.id}><td>{s.vigencia_anio}</td><td>{s.smmlv}</td><td>{s.uvt}</td></tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
```

- [ ] **Step 5.3: Build frontend**

```bash
cd frontend
npm run build
```

Expected: sin errores

- [ ] **Step 5.4: Commit**

```bash
git add frontend/src/api/admin.ts frontend/src/pages/AdminParametrosPage.tsx
git commit -m "feat: add AdminParametrosPage and admin API client (RF-10)"
```

---

## Criterios de terminación — FASE 2

| Criterio | Verificación |
|---|---|
| Solo ADMIN accede a /admin/parametros | Test `test_admin_endpoint_rechaza_contratista` PASS |
| Se puede crear snapshot para año nuevo | Test `test_crear_snapshot_como_admin` PASS |
| Snapshot duplicado retorna 409 | Verificar en tests con mismo vigencia_anio |
| Liquidaciones históricas mantienen su snapshot original | Suite completa backend sin regresiones |
| Build frontend sin errores | `npm run build` OK |
